import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import sympy
import os
import re
import sys
import argparse
import datetime
import random
import copy
from scipy import integrate
import scipy.interpolate as inter
from scipy import signal

from vfr_data_analysis.quaterion_utils import *
from vfr_data_analysis.constants_and_utils import *
from vfr_data_analysis.transition_matrix_utils import *
from vfr_data_analysis.ploting import *
from vfr_data_analysis.samples import *


def orientate_data(data, rev_trans_matrix):
    data = copy.deepcopy(data)
    orientate_df(data.df, rev_trans_matrix)
    return data


def load_and_orientate_data_of(device, category, rev_trans_matrix):
    data = load_data_of(device, category)
    return orientate_data(data, rev_trans_matrix)


def rotate_vector_using_quaterion(vector, quaternion):
    return quaternion.rotate(vector)


# def orientate_data_for_earth_acc_vector(data, earth_acc_vector):
#     """you should take accelerometer value vector when the object (head or glider) are in horizontal position
#     and that will mean in such moments the value of Earth Acceleration will be only on Z axis"""
#     quaternion = qt_from_two_vectors(earth_acc_vector, np.array([0, 0, -1]))
#     sensor_values_df = data.df[data.df.columns[5:]]
#     data.df[data.df.columns[5:]] = np.apply_along_axis(rotate_vector_using_quaterion, 1, sensor_values_df, quaternion)
#     return data

def orientate_data_using_quaternion(data, quaternion):
    data = copy.deepcopy(data)
    sensor_values_df = data.df[data.df.columns[5:]]
    data.df[data.df.columns[5:]] = np.apply_along_axis(rotate_vector_using_quaterion, 1, sensor_values_df, quaternion)
    return data


def compute_gyroscope_cumulative_relative_position_and_plot(head_gyroscope_data):
    z = head_gyroscope_data.df[file_header_Z_dps]
    t = head_gyroscope_data.df[file_header_real_time]
    z_cum_int = integrate.cumtrapz(z, t, initial=0, )
    fig, ax = plt.subplots()
    fig.set_size_inches(24.4, 6)
    plt.title("Cumulative trapez integration")
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M:%S"))
    plt.grid()
    plt.plot(t, z_cum_int, marker='.', linestyle='--')


def orientate_data_from_glider_to_head(data):
    glider_acc = np.array([90, -16, 1001])
    glider_mag = np.array([479, -345, 190])
    head_acc = np.array([-885, 515, -109])
    head_mag = np.array([556, -771, 529])
    quaternion = qt_from_two_paris_of_vectors(glider_acc, glider_mag, head_acc, head_mag)
    sensor_values_df = data.df[data.df.columns[5:]]
    data.df[data.df.columns[5:]] = np.apply_along_axis(rotate_vector_using_quaterion, 1, sensor_values_df, quaternion)
    return data

def turning_check(gyr_value):
    threshold = 75
    if gyr_value > threshold:
        return 1
    elif gyr_value < - threshold:
        return -1
    else:
        return 0

def detect_head_turnings(head_gyroscope_orientated_data):
    """head_gyroscope_orientated_data is assumed to be orientated e.g. Z axis to perpendicular to glider bottom side"""
    threshold = 75
    gyr_df = head_gyroscope_orientated_data.df
    detected_turnings = [turning_check(i) for i in gyr_df[file_header_Z_dps]]

    head_turnings_df = copy.deepcopy(head_gyroscope_orientated_data.df[[file_header_real_time, file_header_hostTimestamp]])
    head_turnings_df[file_header_head_turning] = detected_turnings
    head_turnings_data = Data(dev_head, cat_head_turnings, head_turnings_df)
    return head_turnings_data


def detect_glider_turnings(magnetometer_data):
    window_size = 50  # 5 sekuund
    scale = (2 / 3)
    x_threshold_per_sec = scale * (320 / 13) * (window_size / 10)
    y_threshold_per_sec = scale * (420 / 13) * (window_size / 10)
    z_threshold_per_sec = scale * (225 / 13) * (window_size / 10)

    # po to aby mieć pod tymi sami indeksami te same chwile czasowe
    magnetometer_data = interpolate_data(magnetometer_data, 100)
    df = magnetometer_data.df
    new_data = copy.deepcopy(magnetometer_data)
    new_data.category = cat_glider_turnings
    new_df = new_data.df

    # wyliczamy moduł różnicę między wartościami magnetometra na końcach okna i potem sprawdzamy czy jest większy niż próg
    x_vec = df[df.columns[5]][0:len(df) - window_size]
    x_vec2 = df[df.columns[5]][window_size:len(df)]
    y_vec = df[df.columns[6]][0:len(df) - window_size]
    y_vec2 = df[df.columns[6]][window_size:len(df)]
    z_vec = df[df.columns[7]][0:len(df) - window_size]
    z_vec2 = df[df.columns[7]][window_size:len(df)]
    x_res = np.absolute(x_vec2.values - x_vec.values) > x_threshold_per_sec
    y_res = np.absolute(y_vec2.values - y_vec.values) > y_threshold_per_sec
    z_res = np.absolute(z_vec2.values - z_vec.values) > z_threshold_per_sec
    result = x_res + y_res + z_res
    # filtr medianowy - żeby jednolicić okresy skrętu - na oknie 1.5 razy okno detekcji
    result = signal.medfilt(result, int(window_size / 6) * 18 + 1)
    result = list(map(int, result))
    del new_df[new_df.columns[5]]
    del new_df[new_df.columns[5]]
    del new_df[new_df.columns[5]]
    new_df.drop(df.index[[range(window_size)]], inplace=True)
    new_df[file_header_glider_turning] = result
    return new_data


args0 = {
    cmd_arg_accelerationVector: np.array([-773, 612, 175]),
    cmd_arg_cut_startTime: "2017-05-10_18:10:27",
    cmd_arg_cut_endTime: "2017-05-10_18:39:33",
    cmd_arg_sensorTime: 872772,
    cmd_arg_realTime: "2017-05-10_18:24:06"
}


def run():
    # this is useful place to test methods from library

    perform_import_separation_and_cut_of_original_data(args0)

    ex_orientation_using_matrix()
    ex_comparison_of_orientation_matrix_quaternion()

    ex_head_turnings_detection()
    ex_glider_turnings_detection()
    # ex_comparison_of_orientation_matrix_quaternion()
    glider_gyr_data = load_data_of(dev_glider, cat_gyroscope)
    # _gyr_data = load_data_of(dev_glider, cat_gyroscope)
    plotData(glider_gyr_data)
    plt.show()


if __name__ == "__main__":
    run()
