# -*- coding: utf-8 -*-
from __future__ import print_function
try:
    import numpy as np
    import copy
    import sys
    from math import *

except:
    print("Unable to import some modules\nfunctions and classes might not work properly")

##################################
#		Geometry classes		 #
##################################

class ParametricLine:

    def __init__(self,VectorTuple,InterceptTuple):
        self.VectorTuple = VectorTuple
        self.InterceptTuple = InterceptTuple

    def MakeLinearMatrix(self):
        return np.array([self.VectorTuple,self.InterceptTuple])

class Order3Base:

    """
    Used to store 3D linear algebra bases
    three attribues: e1, e2 and e3, corresponding to the
    three vectors

    The vector given as entry will always be normalized

    __getitem__() is defined so that you can call
    an axis by its index or char reference (x, y or z)

    """

    def __init__(self, e1 = [1,0,0], e2 = [0,1,0], e3 = [0,0,1], BuildFromThis = False):
        self.e1 = e1/np.linalg.norm(e1)
        if BuildFromThis:
            self.e3 = np.cross(self.e1,e2)/np.linalg.norm(np.cross(self.e1,e2))
            self.e2 = np.cross(self.e1,self.e3)/np.linalg.norm(np.cross(self.e1,self.e3))
        else:
            self.e2 = e2/np.linalg.norm(e2)
            self.e3 = e3/np.linalg.norm(e3)

    def __getitem__(self,i):
        if i == "x" or i==0:
            return self.e1
        elif i == "y" or i == 1:
            return self.e2
        elif i == "z" or i == 2:
            return self.e3
