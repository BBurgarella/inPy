# -*- coding: utf-8 -*-
from __future__ import print_function
try:
    import numpy as np
    import copy
    import sys
    from math import *
except:
    print("Unable to import some modules\nfunctions and classes might not work properly")

from inPy_Constants import *

"""
To implement your own backend, make sure that all these functions are defined:
 - Plot_surface()
 - show()
 - Plot_Path()

"""

# Definitions if matplotlib is the backend
if backendDict["Plot"] == "Matplotlib":
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D

    def Plot_surface(x,y,z,fig_axes_Tuple = None,**kwargs):

        """
        if matplotlib is the backend, this function is just a wrapper
        for matplotlib's plot_surface

        """
        if fig_axes_Tuple == None:
            # fig[0]--> plt.figure,
            # fig[1]--> plt.axes
            figure = plt.figure()
            ax = figure.add_subplot(111, projection='3d')
            fig_axes_Tuple = (figure,ax)
        fig_axes_Tuple[1].plot_surface(x,y,z,**kwargs)
        return fig_axes_Tuple

    def Plot_Path(Lx,Ly,Lz,fig_axes_Tuple = None,**kwargs):
        """
        if matplotlib is the backend, this function is just a wrapper
        for matplotlib's plot in a 3d case

        """

        if fig_axes_Tuple == None:
            # fig[0]--> plt.figure,
            # fig[1]--> plt.axes
            figure = plt.figure()
            ax = figure.add_subplot(111, projection='3d')
            fig_axes_Tuple = (figure,ax)
        fig_axes_Tuple[1].plot(Lx,Ly,Lz,**kwargs)
        return fig_axes_Tuple

    def show():
        plt.show()
        return 0

if backendDict["Plot"] == "Mayavi":
    from mayavi import mlab

    def Plot_surface(x,y,z,fig_axes_Tuple = None,**kwargs):

        """
        if mayavi is the backend, the mlab.mesh function
        is used to plot the surface

        """
        if fig_axes_Tuple == None:
            fig_axes_Tuple = mlab.figure()
        New_mesh = mlab.mesh(x, y, z,**kwargs)
        return fig_axes_Tuple

    def show():
        mlab.show()
        return 0
