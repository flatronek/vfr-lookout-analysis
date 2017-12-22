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
from vfr_data_analysis.constants_and_utils import *
from vfr_data_analysis.quaterion_utils import *
from vfr_data_analysis.constants_and_utils import *


def get_mean_head_acceleration_vector(startTime, endTime):
    head_accelerometer_data = load_data_of(dev_head, cat_accelerometer)
    df = head_accelerometer_data.df
    data_window = df[df[file_header_real_time].between(startTime, endTime)]
    acceleration_vector = data_window.mean()[2:].values
    print("Computed Head Earth Acceleration Vector: " + str(acceleration_vector))


def compute_head_sensor_transition_matrix_for_time_window(startTime, endTime):
    acceleration_vector = get_mean_head_acceleration_vector(startTime, endTime)
    return compute_head_sensor_transition_matrix_for_acceleration_vector(acceleration_vector)


def compute_head_sensor_transition_matrix_for_acceleration_vector(acceleration_vector):
    arbitrary_value = 500

    X = np.zeros(3)
    Y = np.zeros(3)
    Z = -acceleration_vector
    A, B, C = Z.tolist()  # surface coefficients

    X[0] = arbitrary_value
    X[1] = arbitrary_value
    X[2] = (-A * X[0] - B * X[1]) / C

    Y[0] = arbitrary_value
    Y[1] = Y[0] * (A * X[2] - C * X[0]) / (C * X[1] - B * X[2])
    Y[2] = (-A * Y[0] - B * Y[1]) / C

    transition_matrix_head = np.column_stack((X, Y, Z))
    transition_matrix_head = np.apply_along_axis(normalize, 0, transition_matrix_head)
    print("Computed Head Transition Matrix:")
    print(str(transition_matrix_head))
    return transition_matrix_head


def _get_head_sensor_transition_matrix(args):
    accelerationVector = args.get(cmd_arg_accelerationVector)
    if accelerationVector is None:
        print("No commandline arguments passed. Taking default (unit) transition matrix for Head sensor")
        return np.eye(3) * -1
    else:
        acceleration_vector = accelerationVector
        print("Given in command line Head Acceleration Vector: " + str(acceleration_vector))
        return compute_head_sensor_transition_matrix_for_acceleration_vector(acceleration_vector)


def obtain_head_sensor_reversed_transition_matrix(args):
    trans_matrix = _get_head_sensor_transition_matrix(args)
    return np.linalg.matrix_power(trans_matrix, -1)


def reorientate_vector(vector, rev_trans_matrix):
    return np.dot(rev_trans_matrix, vector)


def orientate_df(df, rev_trans_matrix):
    sensor_values_df = df[df.columns[5:]]
    df[df.columns[5:]] = np.apply_along_axis(reorientate_vector, 1, sensor_values_df, rev_trans_matrix)
    return df
