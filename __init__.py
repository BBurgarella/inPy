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


# inPy Imports

try:
    from inPy.inPy_Classes import *
    from inPy.inPy_Constants import *
    from inPy.inPy_Functions import *
    print("inPy V{} imported".format(inPy_Version))
    print("Copyright (C) <2019>  <Boris Burgarella>")
except Exception as e:
    print("Error, impossible to load the inPy files")
    print("The error is: \"{}\"".format(e))
