# -*- coding: utf-8 -*-
"""
inPy was written by Boris Burgarella
the objective of this module is to simplify the interaction between python and abaqus

  Copyright (C) <2019>  <Boris Burgarella>
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

#Error list
#Error #01, please enter at least a list of nodes or a list of elements
#Error #02:  please enter an even number of nodes

import numpy as np
import copy
import sys

Error = False


# inPy classes import

from inPy.inPy_Constants import *

try:
    from inPy.Classes.FEM import *
    from inPy.Classes.Geometry import *
    from inPy.Classes.Path import *
    from inPy.Classes.Wired_Structures import *
    from inPy.Classes.RigidBodies import *
    from inPy.Classes.Assembly import *



except Exception as e:
    print("Error, impossible to load the inPy class files")
    print("The error is: \"{}\"".format(e))
    Error = True

# inPy functions import
try:
    from inPy.Functions.FEM import *
    from inPy.Functions.Geometry import *
    from inPy.Functions.Meta import *
    from inPy.Functions.Debug import *
    from inPy.Functions.linalg import *

except Exception as e:
    Error = True
    print("Error, impossible to load the inPy function files")
    print("The error is: \"{}\"".format(e))

# inPy Backend import
try:
    from inPy.Backend.BackendPlot import *

except Exception as e:
    Error = True
    print("Error, impossible to load the inPy backend files")
    print("The error is: \"{}\"".format(e))

# try to import abaqus related libraries
try:
    from abaqus import *
    from abaqusConstants import *
    import regionToolset
    from part import *
    from material import *
    from section import *
    from assembly import *
    from step import *
    from interaction import *
    from load import *
    from mesh import *
    from optimization import *
    from job import *
    from sketch import *
    from visualization import *
    from connectorBehavior import *
    import sketch
    import part
except:
    print("Abaqus libraries not detected, inPy runs in standalone mode")

if Error == False:
    print("inPy V{} imported".format(inPy_Version))
    for key in backendDict:
        print("Using {} backend for {}s".format(backendDict[key],key))
    print("Copyright (C) <2019>  <Boris Burgarella>")
