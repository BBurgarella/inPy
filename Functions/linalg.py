# -*- coding: utf-8 -*-

import numpy as np
import copy
import sys
import pdb
from math import *

from inPy.Classes import *
from inPy.inPy_Constants import *





##################################
#	   	General functions		 #
##################################


def Get_angle(Vector1,Vector2,Rad_or_Deg = "Rad"):
    """
    This function returns the angle (rad) between two vectors
    input: Vector1 (numpy array or list) and Vector2 (numpy array or list)
    output: angle between the two (float)

    Optional parameter: Rad_or_Deg, default to Rad, defines if the angle should be returned
    in radians or degrees

    """
    if Rad_or_Deg == "Deg":
        Factor = 180/PI
    elif Rad_or_Deg == "Rad":
        Factor = 1

    return Factor*acos(np.dot(Vector1,Vector2)/(np.linalg.norm(Vector1)*np.linalg.norm(Vector2)))

def ExtractRotationMatrix(Base_1,Base_0 = None):
    from inPy.inPy_Classes import Order3Base
    """
    This function returns the rotation matrix to get from one base to the
    other. If Base_0 is not specified, it is assumed that the target
    base is e1 = [1,0,0], e1 = [0,1,0], e1 = [0,0,1]

    if Norm is set to False, it is assumed that the used gave
    an already normalized base

    This very simple implementation was found here:
    https://stackoverflow.com/questions/50474886/finding-rotation-matrix-to-transform-one-3-vector-basis-to-another-in-3d

    """
    # Normalization of the user input
    if Base_0 == None:
        Base_0 = Order3Base()
    # Proper code of the function
    MatB_1 = np.array([Base_1[0],Base_1[1],Base_1[2]])
    MatB_0 = np.array([Base_0[0],Base_0[1],Base_0[2]])

    return np.linalg.solve(MatB_1,MatB_0).T
