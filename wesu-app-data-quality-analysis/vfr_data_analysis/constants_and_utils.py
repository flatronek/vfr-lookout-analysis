import argparse
import datetime

import pandas as pd
import scipy.interpolate as inter
from scipy import signal
import os
import copy
import re

# constatns
file_header_real_time = "RealTime"
file_header_nodename = "NodeName"
file_header_hostTimestamp = 'HostTimestamp (ms)'
file_header_nodeTimestamp = 'NodeTimestamp'
file_header_raw_data = 'RawData'
file_header_Z_dps = 'Z (dps)'
file_header_angle = 'Angle between vectors'
file_header_vector_values = 'Vector values'
file_header_glider_turning = 'Glider Turning'
file_header_head_turning = 'Head Turning'

cat_gyroscope = "Gyroscope"
cat_accelerometer = "Accelerometer"
cat_magnetometer = "Magnetometer"

cat_head_turnings = "Head turnings"
cat_glider_turnings = "Glider turnings"

cmd_arg_cut_startTime = "cutStartTime"
cmd_arg_cut_endTime = "cutEndTime"
cmd_arg_sensorTime = "sensorTime"
cmd_arg_realTime = "realTime"
cmd_arg_accelerationVector = "accelerationVector"

z_axis_vector = [0, 0, -1]

class DeviceMeta:
    def __init__(self, position, id):
        self.position = position
        self.id = id


class Data:
    def __init__(self, device, category, df):
        self.device = device
        self.category = category
        self.df = df

dev_head = DeviceMeta('Head', "WeSU @214B6A")
dev_glider = DeviceMeta('Glider', "WeSU @31A190")
dev_kitchen = DeviceMeta('Kitchen', "Kitchen")


def load_data_of(device, category):
    filename_to_find = "Sep_" + device.id + "_" + category + ".csv"
    try:
        df = pd.DataFrame.from_csv(filename_to_find, parse_dates=[file_header_real_time])
        return Data(device, category, df)
    except FileNotFoundError:
        print("!!!!!!", filename_to_find, "not present in current directory!!!!!!")

def load_detections_data(filename):
    try:
        df = pd.DataFrame.from_csv(filename, parse_dates=[file_header_real_time])
        pd.set_option('display.max_rows', 5)
        print(df)
        pd.reset_option('display.max_rows')
        return Data("device", "category", df)
    except FileNotFoundError:
        print("!!!!!!", filename_to_find, "not present in current directory!!!!!!")


def interpolate_data(data, interpolation_step, start_ts=0, end_ts=None):
    """
    :param data: object of Class Data
    :param interpolation_step: interval between new computed values eg. 10ms (data originally has intervals of ~100ms)
    :param start_ts: start of window to cut out from all Data object
    :param end_ts: end of window to cut out from all Data object
    :return: 
    """
    cut_df = data.df.sort_values(file_header_hostTimestamp)
    old_t = cut_df[file_header_hostTimestamp]
    new_t = range(start_ts, end_ts, interpolation_step)
    values_labels = cut_df.columns[5:]
    new_df = pd.DataFrame()
    for vl in values_labels:
        values = cut_df[vl]
        cs = inter.Akima1DInterpolator(old_t, values)
        new_df.insert(len(new_df.columns), vl, cs(new_t))
    new_df.insert(0, file_header_raw_data, "MLEKO")
    new_df.insert(0, file_header_nodeTimestamp, "NA")
    new_df.insert(0, file_header_nodename, data.device)
    new_df.insert(0, file_header_hostTimestamp, new_t)

    # compute sensor_time <--> real_time ratio
    sensor_time = cut_df[file_header_hostTimestamp].iloc[0]
    real_time = cut_df[file_header_real_time].iloc[0]
    start_real_time = real_time - datetime.timedelta(milliseconds=int(sensor_time))
    real_time_column = [start_real_time + datetime.timedelta(milliseconds=int(ms)) for ms in list(new_t)]
    real_time_series = pd.to_datetime(real_time_column)
    new_df.insert(0, file_header_real_time, real_time_series)
    return Data(data.device, data.category, new_df)


def filter_out_spikes(data):
    kernel_size = 9
    no_spikes_x = signal.medfilt(data.df[data.df.columns[5]], kernel_size)
    no_spikes_y = signal.medfilt(data.df[data.df.columns[6]], kernel_size)
    no_spikes_z = signal.medfilt(data.df[data.df.columns[7]], kernel_size)
    res_data = copy.deepcopy(data)
    res_data.device.position = data.device.position
    res_data.device.id = data.device.id
    res_data.category = data.category
    res_data.df[res_data.df.columns[5]] = no_spikes_x
    res_data.df[res_data.df.columns[6]] = no_spikes_y
    res_data.df[res_data.df.columns[7]] = no_spikes_z
    return res_data


def __cut_datas_into_period(datas_list, start_real_time_str, end_real_time_str):
    if start_real_time_str is None or end_real_time_str is None:
        return
    start_time = datetime.datetime.strptime(start_real_time_str, '%Y-%m-%d_%H:%M:%S')
    end_time = datetime.datetime.strptime(end_real_time_str, '%Y-%m-%d_%H:%M:%S')
    for data_dict in datas_list:
        df_cut= data_dict['df'][data_dict['df'][file_header_real_time].between(start_time, end_time)]
        data_dict['df'] = df_cut


args0 = {
    cmd_arg_accelerationVector: pd.np.array([-773, 612, 175]),
    cmd_arg_cut_startTime: "2017-05-10_18:10:27",
    cmd_arg_cut_endTime: "2017-05-10_18:39:33",
    cmd_arg_sensorTime: 872772,
    cmd_arg_realTime: "2017-05-10_18:24:06"
}


def get_comandline_arguments():
    parser = argparse.ArgumentParser(
        description='Sample usage \n realTimeDataAnalysis.py -s=2017-05-10_18:25:27 -e=2017-05-10_18:25:29 \n '
                    'realTimeDataAnalysis.py -av=-773,612,175')
    parser.add_argument('-av', dest='accelerationVector', help='Earth Acceleration vector for Head sensor')
    parser.add_argument('-cst', dest='cut_startTime')
    parser.add_argument('-cet', dest='cut_endTime')
    parser.add_argument('-st', dest='sensorTime')
    parser.add_argument('-rt', dest='realTime')
    args = parser.parse_args()

    args.accelerationVector = pd.np.array(list(map(int, args.accelerationVector.split(',')))) \
        if args.accelerationVector is not None else pd.np.array([0, 0, -1])
    args.sensorTime = int(args.sensorTime) \
        if args.sensorTime is not None else 0
    args = {
        cmd_arg_accelerationVector: args.accelerationVector,
        cmd_arg_cut_startTime: args.cut_startTime,
        cmd_arg_cut_endTime:  args.cut_endTime,
        cmd_arg_sensorTime: args.sensorTime,
        cmd_arg_realTime: args.realTime
    }
    return args


def perform_import_separation_and_cut_of_original_data(args):
    file_paths_dict = __get_all_valid_data_filenames_from_local_dir()
    datas_list = __read_files_to_dataframes(file_paths_dict)
    __add_realTime_column(datas_list, args[cmd_arg_sensorTime], args[cmd_arg_realTime])
    __cut_datas_into_period(datas_list, args[cmd_arg_cut_startTime], args[cmd_arg_cut_endTime])
    __save_as_csvs(datas_list)

def __get_all_valid_data_filenames_from_local_dir():
    all_filenames_from_local_dir = os.listdir(".")
    filename_pattern = r"([0-9]{8,8})_([0-9]{6,6})_(.*).csv"
    file_path_dict = {}
    for filename in all_filenames_from_local_dir:
        result = re.match(filename_pattern, filename)
        if result:
            print("Recognized file: ", filename)
            file_path_dict[result.group(3)] = filename
        else:
            print("Skipping file: ", filename)
    return file_path_dict


def __read_files_to_dataframes(file_path_dict):
    datas_list = []
    file_header_skip = 3
    for sensor_cat, file_path in file_path_dict.items():
        df_togheter = pd.DataFrame.from_csv(file_path, file_header_skip, index_col=-1)
        dev_1_df = df_togheter[df_togheter[file_header_nodename] == dev_head.id]
        dev_2_df = df_togheter[df_togheter[file_header_nodename] == dev_glider.id]
        datas_list.append({'device': dev_head.id,
                           'category': sensor_cat,
                           'df': dev_1_df})
        datas_list.append({'device': dev_glider.id,
                           'category': sensor_cat,
                           'df': dev_2_df})
    return datas_list


def __add_realTime_column(datas_list, sensor_time, real_time_str):
    if real_time_str is None:
        real_time_str = "2017-05-10_18:10:27"
    if sensor_time is None:
        sensor_time= 0
    real_time = datetime.datetime.strptime(real_time_str, '%Y-%m-%d_%H:%M:%S')
    start_real_time = real_time - datetime.timedelta(milliseconds=sensor_time)
    for data_dict in datas_list:
        df = data_dict['df']
        real_time_column = [start_real_time + datetime.timedelta(milliseconds=int(ms)) for ms in
                            list(df[file_header_hostTimestamp])]
        series = pd.to_datetime(real_time_column)
        df.insert(0, file_header_real_time, series)


def __save_as_csvs(datas_list):
    for data_dict in datas_list:
        data_dict['df'].to_csv("Sep_" + data_dict['device'] + "_" + data_dict['category'] + ".csv")




def export_glider_turnings_to_csv(glider_turnings_data):
    glider_turnings_data.df.to_csv("glider_turnings.csv", columns=[file_header_real_time, file_header_hostTimestamp, file_header_glider_turning], index=False)

def export_head_turnings_to_csv(head_turnings_data):
    head_turnings_data.df.to_csv("head_turnings.csv", columns=[file_header_real_time, file_header_hostTimestamp, file_header_head_turning], index=False)


