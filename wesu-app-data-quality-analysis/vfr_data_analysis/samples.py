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

from vfr_data_analysis.quaterion_utils import *
from vfr_data_analysis.constants_and_utils import *
from vfr_data_analysis.transition_matrix_utils import *
from vfr_data_analysis.ploting import *
from vfr_data_analysis.realTimeDataAnalysis import *


# args = {cmd_arg_accelerationVector: np.array([-773, 612, 175])}
args = {cmd_arg_accelerationVector: np.array([-960,-136,199])}


def ex_load_and_plot_with_time_ms():
    x_axis = file_header_hostTimestamp
    head_magnetometer_data = load_data_of(dev_head, cat_magnetometer)
    head_gyr_data= load_data_of(dev_head, cat_gyroscope)
    head_acc_data= load_data_of(dev_head, cat_accelerometer)
    print("Data loaded")
    plotData(head_magnetometer_data, x_axis=x_axis)
    plotData(head_gyr_data, x_axis=x_axis)
    plotData(head_acc_data, x_axis=x_axis)

def ex_load_and_plot_glider_accelerometer_ms():
    x_axis = file_header_hostTimestamp
    glider_acc_data= load_data_of(dev_glider, cat_accelerometer)
    head_acc_data= load_data_of(dev_head, cat_accelerometer)
    print("Data loaded")
    plotData(glider_acc_data, x_axis=x_axis)
    plotData(head_acc_data, x_axis=x_axis)

def ex_load_and_plot_with_real_time():
    x_axis = file_header_real_time
    head_magnetometer_data = load_data_of(dev_head, cat_magnetometer)
    head_gyr_data= load_data_of(dev_head, cat_gyroscope)
    head_acc_data= load_data_of(dev_head, cat_accelerometer)
    plotData(head_magnetometer_data, x_axis=x_axis)
    plotData(head_gyr_data, x_axis=x_axis)
    plotData(head_acc_data, x_axis=x_axis)


def ex_orientation_using_matrix():
# 2 przeliczanie tego żyroskopu wg macierzy z accelerometru - sprawdź czy działa deepcopy (plotuj dwa wykresy) - OK
    rev_trans_matrix = obtain_head_sensor_reversed_transition_matrix(args)  # z argsów jest wektor do ziemi
    head_gyroscope_data = load_data_of(dev_head, cat_gyroscope)
    head_gyroscope_data_orient = orientate_data(head_gyroscope_data, rev_trans_matrix)
    plotData(head_gyroscope_data)
    plotData(head_gyroscope_data_orient)

    head_accelerometr_data = load_data_of(dev_head, cat_accelerometer)
    head_accelerometr_data_orient = orientate_data(head_accelerometr_data, rev_trans_matrix)
    plotData(head_accelerometr_data)
    plotData(head_accelerometr_data_orient)

def ex_interpolation():
    # 3 interpolacja - OK
    # args = get_comandline_arguments()
    rev_trans_matrix = obtain_head_sensor_reversed_transition_matrix(args)  # z argsów jest wektor do ziemi
    head_gyroscope_data = load_data_of(dev_head, cat_gyroscope)
    head_gyroscope_data_orient = orientate_data(head_gyroscope_data, rev_trans_matrix)
    head_gyroscope_orient_interpolated_data = interpolate_data(head_gyroscope_data_orient, 10)#, 140, 933359)
    plotData(head_gyroscope_data_orient)
    plotData(head_gyroscope_orient_interpolated_data)

def ex_cumulative_field_below_plot():
    # 4 sprawdź czy działa wyliczanie cumulative dla gyroskopu - dane bazowe i zinterpolowane - OK
    rev_trans_matrix = obtain_head_sensor_reversed_transition_matrix(args)  # z argsów jest wektor do ziemi
    head_gyroscope_data = load_data_of(dev_head, cat_gyroscope)
    head_gyroscope_data_orient = orientate_data(head_gyroscope_data, rev_trans_matrix)
    head_gyroscope_orient_interpolated_data = interpolate_data(head_gyroscope_data_orient, 10)#, 140, 933359)
    compute_gyroscope_cumulative_relative_position_and_plot(head_gyroscope_data_orient)

def ex_comparison_of_orientation_matrix_quaternion():
    # 5 porównaj orientacje za pomocą kwaternionu i macierzy - powinieneś otrzymac ten sam rezultat na Z - OK
    quat = qt_from_two_vectors(args[cmd_arg_accelerationVector], z_axis_vector)

    head_accelerometer_data = load_data_of(dev_head, cat_accelerometer)
    head_accelerometer_orient_quaternion_data = orientate_data_using_quaternion(head_accelerometer_data, quat)

    rev_trans_matrix = obtain_head_sensor_reversed_transition_matrix(args)  # z argsów jest wektor do ziemi
    head_accelerometer_orient_matrix_data = orientate_data(head_accelerometer_data, rev_trans_matrix)
    plotData(head_accelerometer_data, 'Akcelerometr - nieprzekształcone dane')
    plotData(head_accelerometer_orient_matrix_data, "Akcelerometr - dane w zorientowanych układzie współrzędnych za pomocą macierzy przejścia")
    plotData(head_accelerometer_orient_quaternion_data,
             'Akcelerometr - dane w zorientowanych układzie współrzędnych za pomocą kwaternionu')

    head_gyroscope_data = load_data_of(dev_head, cat_gyroscope)
    head_gyroscope_orient_quaternion_data = orientate_data_using_quaternion(head_gyroscope_data, quat)
    head_gyroscope_orient_matrix_data = orientate_data(head_gyroscope_data, rev_trans_matrix)

    plotData(head_gyroscope_data, 'Żyroskop - nieprzekształcone dane')
    plotData(head_gyroscope_orient_matrix_data, 'Żyroskop - dane w zorientowanych układzie współrzędnych za pomocą macierzy przejścia')
    plotData(head_gyroscope_orient_quaternion_data, "Żyroskop - dane w zorientowanych układzie współrzędnych za pomocą kwaternionu")


def ex_computing_angles_between_vectors():
    head_magnetometer_data = load_data_of(dev_head, cat_magnetometer)
    head_accelerometer_data = load_data_of(dev_head, cat_accelerometer)
    head_mag_acc_angles = compute_angles_between_vectors(head_magnetometer_data, head_accelerometer_data)
    plotData(head_mag_acc_angles, "Wartość kąta pomiędzy wektorem pola indukcji magnetycznej a wektorem przyśpieszenia ziemskiego w radianach")
    plotData(head_magnetometer_data, "Wartości wskazań magnetometru")

def ex_compute_vector_values():
    head_accelerometer_data = load_data_of(dev_head, cat_accelerometer)
    head_acc_vector_values_data = compute_vector_values(head_accelerometer_data)
    plotData(head_acc_vector_values_data)

def ex_calibrate_head_magnetometer_data():
    # Kalibracja danych z kuchni
    head_mag_min_X = -122
    head_mag_max_X = 758

    head_mag_min_Y = -795
    head_mag_max_Y = 96

    head_mag_min_Z = 41
    head_mag_max_Z = 879

    # head_magnetometer_data = load_data_of(dev_kitchen, cat_magnetometer)
    head_magnetometer_data = load_data_of(dev_head, cat_magnetometer)
    head_magnetometer_data = interpolate_data(head_magnetometer_data, 100)
    head_accelerometer_data = load_data_of(dev_head, cat_accelerometer)
    head_accelerometer_data = interpolate_data(head_accelerometer_data, 100)

    head_magnetometer_calib_data = calibrate_data(head_magnetometer_data, head_mag_min_X, head_mag_max_X, head_mag_min_Y, head_mag_max_Y, head_mag_min_Z, head_mag_max_Z)
    head_magnetometer_calib_vec_values = compute_vector_values(head_magnetometer_calib_data)

    head_mag_acc_angles = compute_angles_between_vectors(head_magnetometer_calib_data, head_accelerometer_data)

    plotData(head_magnetometer_data)
    plotData(head_magnetometer_calib_data)
    plotData(head_magnetometer_calib_vec_values)
    plotData(head_mag_acc_angles, "Wartość kąta pomiędzy wektorem pola indukcji magnetycznej (po kalibracji danych), a wektorem przyśpieszenia ziemskiego w radianach")


def ex_glider_turnings_detection():
    glider_mag_data = load_data_of(dev_glider, cat_magnetometer)
    glider_mag_no_spikes_data = filter_out_spikes(glider_mag_data)
    glider_turnings = detect_glider_turnings(glider_mag_no_spikes_data)
    plotData(glider_mag_data, "Wskazania magnetometru z czujnika umieszczonego na szybowcu")
    plotData(glider_mag_no_spikes_data, "Wskazania magnetometru z czujnika umieszczonego na szybowcu, po usunięciu szumu")
    plotData(glider_turnings, "Wykryte skręty szybowca, rezultat przefiltrowany medianowo")
    export_glider_turnings_to_csv(glider_turnings)

def ex_head_turnings_detection():
    quat = qt_from_two_vectors(args[cmd_arg_accelerationVector], z_axis_vector)
    head_gyr_data = load_data_of(dev_head, cat_gyroscope)
    head_gyr_orient_quaternion_data = orientate_data_using_quaternion(head_gyr_data, quat)
    plotData(head_gyr_orient_quaternion_data)

    head_turnings_data = detect_head_turnings(head_gyr_orient_quaternion_data)
    plotData(head_turnings_data)
    export_head_turnings_to_csv(head_turnings_data)


def ex_head_rotation_gyroscope():
    quat = qt_from_two_vectors(args[cmd_arg_accelerationVector], z_axis_vector)
    head_gyroscope_data = load_data_of(dev_head, cat_gyroscope)
    head_gyroscope_orient_quaternion_data = orientate_data_using_quaternion(head_gyroscope_data, quat)
    plotData(head_gyroscope_orient_quaternion_data)


def remove_drift_from_gyroscope_cumulative():
    quat = qt_from_two_vectors(args[cmd_arg_accelerationVector], z_axis_vector)
    head_gyroscope_data = load_data_of(dev_head, cat_gyroscope)
    head_gyroscope_orient_quaternion_data = orientate_data_using_quaternion(head_gyroscope_data, quat)
    head_gyroscope_orient_quaternion_translated_data = translate_data(head_gyroscope_orient_quaternion_data, 0, 0, 1)
    plotData(head_gyroscope_data)
    plotData(head_gyroscope_orient_quaternion_data)
    plotData(head_gyroscope_orient_quaternion_translated_data)
    compute_gyroscope_cumulative_relative_position_and_plot(head_gyroscope_orient_quaternion_data)
    compute_gyroscope_cumulative_relative_position_and_plot(head_gyroscope_orient_quaternion_translated_data)



def run():
    ex_load_and_plot_glider_accelerometer_ms()
    plt.show()

if __name__ == "__main__":
    run()
