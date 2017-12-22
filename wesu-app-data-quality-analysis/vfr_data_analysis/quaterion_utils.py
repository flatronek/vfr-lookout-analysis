import math

import numpy as np
from pyquaternion import Quaternion


def angle_between_vectors(v1, v2):
    cos_theta = normalize(v1).dot(normalize(v2))
    angle = math.acos(cos_theta)
    return angle

def qt_from_two_vectors(v1, v2):
    angle = angle_between_vectors(v1, v2)
    perpendicular_v = normalize(np.cross(v1, v2))
    return Quaternion(axis=perpendicular_v, angle=angle)


def normalize(vector):
    return vector / np.linalg.norm(vector)


def project_to_plane(vect_to_project, vect_perpen_to_plane):
  '''Create a 'projection', and subract it from the original vector'''
  projection = vect_to_project.dot(normalize(vect_perpen_to_plane)) * normalize(vect_perpen_to_plane)
  return vect_to_project - projection

def qt_from_two_paris_of_vectors(u0, v0, u2, v2):
    q2 = qt_from_two_vectors(u0, u2)
    v1 = q2.inverse.rotate(v2)
    v0_proj = project_to_plane(v0, u0)
    v1_proj = project_to_plane(v1, u0)
    q1 = qt_from_two_vectors(v0_proj, v1_proj)
    q = q2 * q1
    return q

#angle between vectors
# a1 = angle_between_vectors(np.array([1,0,0]),np.array([0,1,0]))
# a2 = angle_between_vectors(np.array([1,0,0]),np.array([1,1,0]))
# a = 1

# From two pairs test
# u0 = np.array([10,0.1,0])
# v0 = np.array([0,1,0])
# u2 = np.array([0,1,0])
# v2 = np.array([0,0,10])
# quat = qt_from_two_paris_of_vectors(u0, v0, u2, v2)
# rotated = quat.rotate([-10,-10,0])
# a = 1


# Projection test
# v1 = np.array([1,1,1])
# v2 = np.array([0,0,1])
# projection = project_to_plane(v1, v2)
# a = 1


# Quaterion test
# v1 = normalize(np.array([-1,1,1]))
# v2 = normalize(np.array([-1,5,1]))
# quat = qt_from_two_vectors(v1, v2)
# newV2 = quat.rotate(v1)
# newV1 = quat.inverse.rotate(v2)
# a = 1

