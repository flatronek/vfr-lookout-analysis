import copy

import matplotlib
import matplotlib.pyplot as plt

from vfr_data_analysis.transition_matrix_utils import *


def plotData(data, title=None, x_axis = file_header_real_time):
    x = data.df[x_axis]
    values_labels = list(data.df.columns)[5:]
    fig, ax = plt.subplots()
    if title is None:
        title = data.device.position + " - " + data.category + data.device.id + " - "
    fig.canvas.set_window_title(title)
    # fig.set_size_inches(24.4, 6)
    fig.set_size_inches(21, 9)
    plt.title(title)
    plt.gcf().autofmt_xdate()
    for label in values_labels:
        values = list(data.df[label])
        plt.plot(x, values, marker='.', linestyle='--')
        if x_axis == file_header_real_time:
            ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M:%S"))
    plt.grid()
    plt.legend(values_labels)
    plt.show()

def plotDetectionData(data, title=None, x_axis = file_header_real_time):
    x = data.df[x_axis]
    values_labels = list(data.df.columns)[2:]
    fig, ax = plt.subplots()
    if title is None:
        title = data.device.position + " - " + data.category + data.device.id + " - "
    fig.canvas.set_window_title(title)
    # fig.set_size_inches(24.4, 6)
    fig.set_size_inches(21, 9)
    plt.title(title)
    plt.gcf().autofmt_xdate()
    for label in values_labels:
        values = list(data.df[label])
        plt.plot(x, values, marker='.', linestyle='--')
        if x_axis == file_header_real_time:
            ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M:%S"))
    plt.grid()
    plt.legend(values_labels)
    plt.show()


def compute_angle(row):
    angle = angle_between_vectors(row.iloc[0:3].values, row.iloc[3:6].values)
    return angle


def compute_vector_value(row):
    value = np.linalg.norm(row[5:8].values)
    return value


def take_common_time_period(df1, df2):
    start1 = df1[file_header_hostTimestamp].iloc[1]
    end1 = df1[file_header_hostTimestamp].iloc[-1]
    start2 = df2[file_header_hostTimestamp].iloc[1]
    end2 = df2[file_header_hostTimestamp].iloc[-1]
    return max([start1, start2]), min([end1, end2])


def compute_angles_between_vectors(data1, data2):
    """This method assumes that thowe two data come from one device - (in this case normally it'll make sense"""
    # take latter start and earlier end interpolate 25ms
    start_ts, end_ts = take_common_time_period(data1.df, data2.df)
    data1 = interpolate_data(data1, 25, start_ts, end_ts)
    data2 = interpolate_data(data2, 25, start_ts, end_ts)

    two_vectors_df = pd.concat([data1.df[data1.df.columns[5:8]], data2.df[data2.df.columns[5:8]]], axis=1)
    angles = two_vectors_df.apply(lambda row: compute_angle(row), axis=1)
    res_data = copy.deepcopy(data1)
    res_data.device.position = data1.device.position + "-" + data2.device.position
    res_data.device.id = data1.device.id + "-" + data2.device.id
    res_data.category = "angle_" + data1.category + "--" + data2.category + " "
    res_data.df = res_data.df.drop(res_data.df.columns[5:8], axis=1)

    res_data.df[file_header_angle] = angles
    return res_data


def compute_vector_values(data):
    """This method assumes that thowe two data come from one device - (in this case normally it'll make sense"""
    # take latter start and earlier end interpolate 25ms

    values = data.df.apply(lambda row: compute_vector_value(row), axis=1)
    res_data = copy.deepcopy(data)
    res_data.device.position = data.device.position
    res_data.device.id = data.device.id
    res_data.category = "vector length values" + data.category
    res_data.df = res_data.df.drop(res_data.df.columns[5:8], axis=1)

    res_data.df[file_header_vector_values] = values
    return res_data


def calibrate_data(data, minX, maxX, minY, maxY, minZ, maxZ):
    dX = maxX - minX
    dY = maxY - minY
    dZ = maxZ - minZ

    centerX = minX + (dX / 2)
    centerY = minY + (dY / 2)
    centerZ = minZ + (dZ / 2)

    # ratioX = 1000 / dX
    # ratioY = 1000 / dY
    # ratioZ = 1000 / dZ
    ratioX = 1
    ratioY = 1
    ratioZ = 1

    calibrated_x = data.df.apply(lambda row: (row[5] - centerX) * ratioX, axis=1)
    calibrated_y = data.df.apply(lambda row: (row[6] - centerY) * ratioY, axis=1)
    calibrated_z = data.df.apply(lambda row: (row[7] - centerZ) * ratioZ, axis=1)
    res_data = copy.deepcopy(data)
    res_data.device.position = data.device.position
    res_data.device.id = data.device.id
    res_data.category = "vector length values" + data.category
    res_data.df[res_data.df.columns[5]] = calibrated_x
    res_data.df[res_data.df.columns[6]] = calibrated_y
    res_data.df[res_data.df.columns[7]] = calibrated_z
    return res_data


def translate_data(data, x, y, z):
    translate_x = data.df.apply(lambda row: row[5] - x, axis=1)
    translate_y = data.df.apply(lambda row: row[6] - y, axis=1)
    translate_z = data.df.apply(lambda row: row[7] - z, axis=1)
    res_data = copy.deepcopy(data)
    res_data.device.position = data.device.position
    res_data.device.id = data.device.id
    res_data.category = data.category
    res_data.df[res_data.df.columns[5]] = translate_x
    res_data.df[res_data.df.columns[6]] = translate_y
    res_data.df[res_data.df.columns[7]] = translate_z
    return res_data