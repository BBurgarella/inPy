# -*- coding: utf-8 -*-

import numpy as np
import copy
import sys
import pdb
from math import *

from inPy.Classes import *
from inPy.inPy_Constants import *

##################################
#	   	wrapping functions		 #
##################################

"""
The functions here are defined to make standalone version of
functions already existing within a type of object
This allows to use this kind of function as parameter for another function
(for example it is used in the strand class to specify the path generation function)
"""

def CreatePath(PathTypeKey,*args,**kwargs):
    from inPy import path
    tempPath = path()
    if PathTypeKey == "Sinus":
        tempPath.Init3DSinus(*args,**kwargs)
    elif PathTypeKey == "Line":
        tempPath.InitLinear(*args,**kwargs)
    return tempPath
