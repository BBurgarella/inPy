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

def EnableScriptingEnvironement(Verbose = True):
    import AbaqusScripting
    if Verbose:
        print("This file can now be used as a script in abaqus")
    try:
        if Verbose:
            print("This file can now be used as a script in abaqus")
            print(AbaqusScripting.methods)
    except:
        if Verbose:
            print("Impossible to import abaqus libraries")
            print("You need to use the abaqus python command or, in CAE 'File -> run script'")

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
