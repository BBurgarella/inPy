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
        # I had to add this to force the aspect ratio
        # source: https://stackoverflow.com/questions/13685386/matplotlib-equal-unit-length-with-equal-aspect-ratio-z-axis-is-not-equal-to
        # Create cubic bounding box to simulate equal aspect ratio
        max_range = np.array([x.max()-x.min(), y.max()-y.min(), z.max()-z.min()]).max()
        Xb = 0.5*max_range*np.mgrid[-1:2:2,-1:2:2,-1:2:2][0].flatten() + 0.5*(x.max()+x.min())
        Yb = 0.5*max_range*np.mgrid[-1:2:2,-1:2:2,-1:2:2][1].flatten() + 0.5*(y.max()+y.min())
        Zb = 0.5*max_range*np.mgrid[-1:2:2,-1:2:2,-1:2:2][2].flatten() + 0.5*(z.max()+z.min())
        # Comment or uncomment following both lines to test the fake bounding box:
        for xb, yb, zb in zip(Xb, Yb, Zb):
           fig_axes_Tuple[1].plot([xb], [yb], [zb], 'w')
        return fig_axes_Tuple
        return fig_axes_Tuple

    def Plot_Path(Lx,Ly,Lz,fig_axes_Tuple = None,tube_radius=None,**kwargs):
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
        fig_axes_Tuple[1].plot(Lx,Ly,Lz,linewidth=None,**kwargs)
        Lx = np.array(Lx)
        Ly = np.array(Ly)
        Lz = np.array(Lz)

        # I had to add this to force the aspect ratio
        # source: https://stackoverflow.com/questions/13685386/matplotlib-equal-unit-length-with-equal-aspect-ratio-z-axis-is-not-equal-to
        # Create cubic bounding box to simulate equal aspect ratio
        max_range = np.array([Lx.max()-Lx.min(), Ly.max()-Ly.min(), Lz.max()-Lz.min()]).max()
        Xb = 0.5*max_range*np.mgrid[-1:2:2,-1:2:2,-1:2:2][0].flatten() + 0.5*(Lx.max()+Lx.min())
        Yb = 0.5*max_range*np.mgrid[-1:2:2,-1:2:2,-1:2:2][1].flatten() + 0.5*(Ly.max()+Ly.min())
        Zb = 0.5*max_range*np.mgrid[-1:2:2,-1:2:2,-1:2:2][2].flatten() + 0.5*(Lz.max()+Lz.min())
        # Comment or uncomment following both lines to test the fake bounding box:
        for xb, yb, zb in zip(Xb, Yb, Zb):
           fig_axes_Tuple[1].plot([xb], [yb], [zb], 'w')
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

    def Plot_Path(Lx,Ly,Lz,fig_axes_Tuple = None,tube_radius=None,**kwargs):
        """
        if matplotlib is the backend, this function is just a wrapper
        for matplotlib's plot in a 3d case

        """

        if fig_axes_Tuple == None:
            fig_axes_Tuple = mlab.figure()
        New_mesh = mlab.plot3d(Lx,Ly,Lz,tube_radius=tube_radius,**kwargs)
        return fig_axes_Tuple

    def show():
        mlab.show()
        return 0
