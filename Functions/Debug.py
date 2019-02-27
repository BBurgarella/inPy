# -*- coding: utf-8 -*-

import numpy as np
import copy
import sys
import pdb
from math import *

from inPy.Classes import *
from inPy.inPy_Constants import *




##############################
#	   Debug functions		 #
##############################

def PlotCircles(CirclesDistrib,R,XBd,YBd,D1,D2):
    # Local imports to avoid importing matplotlib
    # for no reasons
    from matplotlib.patches import Circle, Ellipse
    from matplotlib.collections import PatchCollection
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()

    patches = []
    EllipseP = Ellipse((0,0),D1,D2,alpha=1,edgecolor="Black",fill=False)
    for Coords in CirclesDistrib:
        circle = Circle((Coords[0], Coords[1]), R)
        patches.append(circle)

    colors = 100*np.random.rand(len(patches))
    p = PatchCollection(patches)
    p.set_array(np.array(colors))
    ax.add_collection(p)
    ax.add_patch(EllipseP)
    ax.set_xlim(*XBd)
    ax.set_ylim(*YBd)

    plt.show()
