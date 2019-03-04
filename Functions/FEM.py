# -*- coding: utf-8 -*-

import numpy as np
import copy
import sys
import pdb
from math import *

from inPy.Classes import *
from inPy.inPy_Constants import *

######################################
#	   FEM specific functions		 #
######################################

def CreateDummyString():
    strtoreturn = ""
    strtoreturn += "**\n*Part, name = Dummy\n"
    strtoreturn += "*End Part\n**\n"
    return strtoreturn
