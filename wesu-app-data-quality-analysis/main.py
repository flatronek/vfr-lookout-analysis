import argparse
import datetime
import os
import re
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

#constatns
file_header_nodename = "NodeName"
file_header_hostTimestamp = 'HostTimestamp (ms)'
file_header_nodeTimestamp = 'NodeTimestamp'
file_value_device1 = "WeSU @214B6A"
file_value_device2 = "WeSU @31A190"
file_header_real_time = "RealTime"

file_header_skip = 3

print_head_value = 10

#set up of logger

class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open("raport.txt", "w")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        #this flush method is needed for python 3 compatibility.
        #this handles the flush command by doing nothing.
        #you might want to specify some extra behavior here.
        pass

sys.stdout = Logger()



def get_all_valid_data_filenames_from_local_dir():
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




def read_files_to_dict_of_df(file_path_dict):
    data_both_dict = {}
    for sensor_type in file_path_dict:
        file_path = file_path_dict[sensor_type]
        data_both_dict[sensor_type] = pd.DataFrame.from_csv(file_path, file_header_skip, index_col=-1)
    return data_both_dict


def parse_comandline_arguments():
    parser = argparse.ArgumentParser(
        description='Sample usage \n main.py -st=1235 -rt=2017-05-10_18:25:27')
    parser.add_argument('-st', dest='sensorTime', type=int, help='timestamp from sensor data')
    parser.add_argument('-rt', dest='realTime', help='timestamp from video moment')

    args = parser.parse_args()
    return (args.sensorTime, args.realTime)


def add_real_time_column_if_cmdline_options_present(data_devices_dict):
    (sensor_time, real_time_str) = parse_comandline_arguments()
    agrs_passed = True
    if sensor_time is None or real_time_str is None:
        print("Sensor time or real time is missing. Continuing without them")
        agrs_passed = False
    else:
        real_time = datetime.datetime.strptime(real_time_str, '%Y-%m-%d_%H:%M:%S')
        start_real_time = real_time - datetime.timedelta(milliseconds=sensor_time)

    for device, device_data in data_devices_dict.items():
        for data_cat_key, data_cat in device_data.items():
            if agrs_passed:
                real_time_column = [start_real_time + datetime.timedelta(milliseconds=int(ms)) for ms in list(data_cat[file_header_hostTimestamp])]
                series = pd.to_datetime(real_time_column)
                data_cat.insert(0, file_header_real_time, series)
            else:
                data_cat.insert(0, file_header_real_time, None)

    return data_devices_dict


###############
# Tests part
###############

def separate_data_per_devices(data_both_dict):
    data_device_1 = {}
    data_device_2 = {}
    for key in data_both_dict:
        df = data_both_dict[key]
        data_device_1[key] = df[df[file_header_nodename] == file_value_device1]
        data_device_2[key] = df[df[file_header_nodename] == file_value_device2]
    return {
        file_value_device1 : data_device_1,
        file_value_device2 : data_device_2
    }

###############
# Tests part
###############

def __printDelimiter():
    print("#########################################")

def printlnDelimiter():
    print("")
    __printDelimiter()

def printStartTests():
    printlnDelimiter()
    print("Tests start")
    __printDelimiter()
    print("")

def is_alternation_preserved_in_df(df):
    even_device = df[file_header_nodename].iloc[0]
    uneven_device = df[file_header_nodename].iloc[1]
    return all(even_device == df[::2][file_header_nodename])\
           and \
           all(uneven_device == df[1::2][file_header_nodename])


def devices_data_aquisition_alternation_test(data_both_dict):
    printlnDelimiter()
    print("Is alternation in device logs preserved in files:")
    print("")
    for data_cat in data_both_dict:
        df = data_both_dict[data_cat]
        result = is_alternation_preserved_in_df(df)
        print(data_cat,"\t\t", result)



def chronology_in_logs_test(data_devices_dict):
    printlnDelimiter()
    print("Is chronology in device logs preserved in files:")
    for device in data_devices_dict:
        print("")
        print("Device: ", device)
        data = data_devices_dict[device]
        for data_cat_key in data:
            data_cat = data[data_cat_key]
            host_ts_result = np.diff(data_cat[file_header_hostTimestamp]) > 0
            host_ts_result_bool = all(host_ts_result)
            node_ts_result = np.diff(data_cat[file_header_nodeTimestamp]) > 0
            node_ts_result_bool = all(node_ts_result)
            print(data_cat_key,"-",file_header_hostTimestamp,": ", host_ts_result_bool)
            if not host_ts_result_bool:
                print("Check timepoints:", data_cat[file_header_hostTimestamp][np.append(host_ts_result, [True]) == False].head(print_head_value).tolist())
            print(data_cat_key,"-",file_header_nodeTimestamp,": ", node_ts_result_bool)
            if not node_ts_result_bool:
                print("Check timepoints e.g.:", data_cat[file_header_nodeTimestamp][np.append(node_ts_result, [True]) == False].head(print_head_value).tolist())


def save_test_csvs(data_devices_dict):
    for device_key in data_devices_dict:
        data = data_devices_dict[device_key]
        for data_cat_key in data:
            data_cat = data[data_cat_key]
            data_cat.to_csv("Sep_" + device_key + "_" + data_cat_key +".csv")


def checkAllEqual(iterator):
    return len(set(iterator)) <= 1


def amount_of_data_acquisitions_test(data_devices_dict):
    printlnDelimiter()
    print("Is amount of data acquisitions points equal for all categories per devise:")
    for device in data_devices_dict:
        print("")
        print("Device: ", device)
        data = data_devices_dict[device]
        result_dict = { data_cat_key : data[data_cat_key].shape[0] for data_cat_key in data}
        result_bool = checkAllEqual(result_dict.values())
        print("Is equal:", result_bool)
        if result_bool:
            print("Amount:", list(result_dict.values())[0])
        else:
            print("Result (sensor_category: data_amount):", result_dict)


def highest_interval_acquisition_test(data_devices_dict):
    printlnDelimiter()
    print("What are the highest intervals (HostTimestamp [ms]) for data acquisitions:")
    for device in data_devices_dict:
        print("")
        print("Device: ", device)
        data = data_devices_dict[device]
        for data_cat_key in data:
            data_cat = data[data_cat_key]
            host_ts_intervals_result = np.absolute(np.diff(data_cat[file_header_hostTimestamp]))
            host_ts_max_interval_start_index = host_ts_intervals_result.argmax()
            host_ts_max_interval = host_ts_intervals_result[host_ts_max_interval_start_index]
            start_ts = data_cat.iloc[host_ts_max_interval_start_index][file_header_hostTimestamp]
            end_ts = data_cat[file_header_hostTimestamp].iloc[host_ts_max_interval_start_index+1]
            print(data_cat_key + ":  ", "Max interval:", host_ts_max_interval, "[ms]",\
                  ", start_ts:", start_ts,\
                  ", end_ts:", end_ts)


def print_millis_nicely(millis):
    millis = int(millis)
    seconds = (millis / 1000) % 60
    seconds = int(seconds)
    minutes = (millis / (1000 * 60)) % 60
    minutes = int(minutes)
    hours = (millis / (1000 * 60 * 60)) % 24
    return str(int(hours)) + "h : " + str(int(minutes)) + "min : " + str(int(seconds)) + "sec"


def acquisition_time_length(data_devices_dict):
    printlnDelimiter()
    print("What are the lengths of acquisitions:")
    for device in data_devices_dict:
        print("")
        print("Device: ", device)
        data = data_devices_dict[device]
        for data_cat_key in data:
            data_cat = data[data_cat_key]
            start_ts = data_cat[file_header_hostTimestamp].iloc[0]
            end_ts = data_cat[file_header_hostTimestamp].iloc[-1]
            length = end_ts - start_ts
            print(data_cat_key, "- Acquisition length:", print_millis_nicely(length))


def plot_intervals(data_devices_dict):
    for device in data_devices_dict:
        data = data_devices_dict[device]
        dict_len = len(data)
        fig = plt.figure()
        fig.suptitle('Intervals for device ' + device)
        rows_in_plot = 3
        subplot_dim = str(rows_in_plot) + str(1 + int(dict_len / rows_in_plot))
        counter = 1
        for data_cat_key in data:
            data_cat = data[data_cat_key]
            host_ts_intervals_result = np.diff(data_cat[file_header_hostTimestamp])
            plt.subplot(subplot_dim + str(counter))
            plt.title(data_cat_key)
            plt.plot(host_ts_intervals_result, 'o')
            counter += 1


def create_data_cat_dictionary(data_devices_dict):
    devices = list(data_devices_dict.keys())
    data_categories = list(data_devices_dict[devices[0]].keys())
    data_cat_dict = {}
    for data_cat in data_categories:
        data_cat_dict[data_cat] = {}
        for device in devices:
            data_cat_dict[data_cat][device] = data_devices_dict[device][data_cat]
    return data_cat_dict


def plot_data_cat_values_all_separate(data_devices_dict):
    data_cat_dict = create_data_cat_dictionary(data_devices_dict)
    for data_cat_key in data_cat_dict:
        data_of_cat_all_devices = data_cat_dict[data_cat_key]
        fig = plt.figure()
        fig.suptitle(data_cat_key + ' data')
        rows_in_plot = len(list(data_cat_dict[data_cat_key].values())[0].columns) - 4
        cols_in_plot = len(data_cat_dict[data_cat_key])
        device_counter = 1
        for device_key in data_of_cat_all_devices:
            value_counter = 0
            data_cat_one_device_df = data_of_cat_all_devices[device_key]
            data_cat_values_labels = list(data_cat_dict[data_cat_key][device_key].columns)[4:]
            for data_cat_value_label in data_cat_values_labels:
                data_cat_values = data_cat_one_device_df[data_cat_value_label]
                plt.subplot(str(rows_in_plot) + str(cols_in_plot) + str(device_counter + value_counter*cols_in_plot))
                plt.title(data_cat_value_label)
                plt.ylabel(device_key)
                plt.plot(list(data_cat_values.values))
                value_counter += 1

def plot_data_cat_values(data_devices_dict):
    data_cat_dict = create_data_cat_dictionary(data_devices_dict)
    for data_cat_key in data_cat_dict:
        data_of_cat_all_devices = data_cat_dict[data_cat_key]
        fig = plt.figure()
        fig.suptitle(data_cat_key + ' data')
        rows_in_plot = 2
        cols_in_plot = int(len(data_cat_dict[data_cat_key]) / 2)
        counter = 1
        for device_key in data_of_cat_all_devices:
            data_cat_one_device_df = data_of_cat_all_devices[device_key]
            data_cat_values_labels = list(data_cat_dict[data_cat_key][device_key].columns)[4:]
            legend_list = []
            for data_cat_value_label in data_cat_values_labels:
                data_cat_values = data_cat_one_device_df[data_cat_value_label]
                plt.subplot(str(rows_in_plot) + str(cols_in_plot) + str(counter))
                # plt.title(data_cat_value_label)
                plt.ylabel(device_key)
                plt.plot(list(data_cat_values.values))
                legend_list.append(data_cat_value_label)
            counter += 1
            plt.legend(legend_list)


def run():
    filenames_dict = get_all_valid_data_filenames_from_local_dir()
    data_both_dict = read_files_to_dict_of_df(filenames_dict)
    data_devices_dict = separate_data_per_devices(data_both_dict)
    data_devices_dict = add_real_time_column_if_cmdline_options_present(data_devices_dict)
    save_test_csvs(data_devices_dict)
    # print(data_device_1)
    # print(data_device_2)
    printStartTests()
    devices_data_aquisition_alternation_test(data_both_dict)
    chronology_in_logs_test(data_devices_dict)
    amount_of_data_acquisitions_test(data_devices_dict)
    highest_interval_acquisition_test(data_devices_dict)
    acquisition_time_length(data_devices_dict)
    plot_intervals(data_devices_dict)
    plot_data_cat_values(data_devices_dict)
    plt.show()




if __name__ == "__main__":
    run()