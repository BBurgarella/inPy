# -*- coding: utf-8 -*-
from __future__ import print_function
try:
    import numpy as np
    import copy
    import sys
    from random import random
    from math import *

except:
    print("Unable to import some modules\nfunctions and classes might not work properly")


"""
In this file, all the classes defined will be used to generate
Rigid Bodies

"""

class rigid_Body:

    """
    Master class, all the other classes should herit from this one

    """

    def __init__(self, Name, Density, RotInertiaMatrix = None, CenterPoint=[0,0,0], TransVect = [0,0,0], RotVect = [0,0,0], Ref_Base = None):
        """
        A Rigid body of any shape should be defined by a name, a Matrix to store its
        rotary intertias, a center point (Should always refer to the center of mass), a translation vector,
        and a rotation vector

        The rotation vector is defined as the angles (rad) to respectively rotate around each axis of the
        chosen base

        """
        from inPy.Classes.Geometry import Order3Base

        if Ref_Base == None:
            Ref_Base = Order3Base()

        # Name of the rigid body
        self.Name = Name

        #Density
        self.Density = Density

        # Mass center
        self.CenterPoint = CenterPoint

        # Rotary intertia matrix
        # Following abaqus notation
        # [[I11,I12,I13],
        #  [I12,I22,I23],
        #  [I13,I23,I33]]
        # If this is None, inPy will attempt to calculate it with the Calc_Rotary_intertia method
        # my advice would be to override this method for all the subclasses to match the shape
        # By default, it will only return:
        # [[0.001,0,0],
        #  [0,0.001,0],
        #  [0,0,0.001]]
        # Because it is therefore assumed that the rotary intertia is negligeable
        self.RotInertiaMatrix = RotInertiaMatrix

        # Translation vector
        self.TransVect = TransVect

        # Rotation vector
        self.RotVect = RotVect

        # Base in which express the rotations
        self.Ref_Base = Ref_Base

        # Generation method
        # None => by giving a series of points
        # Extrude => Extrude a surface over a lengh
        # Revolution => Takes a surface and makes a revolution solid
        self.GenMethod = None

    def Generate_INP_String(self):

        """
        this function is empty here but must be redefined in subclasses

        """
        raise ValueError("The Generate_INP_String method have not been overrided for this subclass and\
        is therefore empty, you must override this method when subclassing the rigid_Body class")

    def Calc_Rotary_intertia(self):

        """
        this function is empty here but must be redefined in subclasses

        """
        raise ValueError("The Calc_Rotary_intertia method have not been overrided for this subclass and\
        is therefore empty, you must override this method when subclassing the rigid_Body class")


class Pulley(rigid_Body):

    """
    Subclass of rigid_Body, used to define pulleys.

    New attributes:
    ShapeString --> defines the type of pulley,
    admissible values are "Cyl" (Cylinder), "V" (Vshape contact surface), "U" (U shape contact surface) and "I" (Cylinder with borders)

    ShapeArgs --> Tuple used to specify the shape-related parameters

    """
    def __init__(self, Name, Density,ShapeString, ShapeArgs, RotInertiaMatrix = None, CenterPoint=[0,0,0], TransVect = [0,0,0], RotVect = [0,0,0], Ref_Base = None):

        # init parent class (rigid_Body)
        super().__init__(Name, Density, RotInertiaMatrix = RotInertiaMatrix, CenterPoint=CenterPoint, TransVect = TransVect, RotVect = RotVect, Ref_Base = Ref_Base)

        if ShapeString == "Cyl":
            self.Radius = ShapeArgs[0]
            self.Lengh = ShapeArgs[1]
            self.GenMethod = "Revolution"

    def Draw(self,Sides = 100,color=(random(),random(),random()),standalone=True,fig = None,backend="Mayavi"):
        # Create the data.
        from numpy import pi, sin, cos, mgrid
        if backend == "Mayavi":
            print("Using Mayabi backend for plot")
            from mayavi import mlab
        elif backend == "matplotlib":
            print("Using matplotlib backend for plot")
            import matplotlib.pyplot as plt
            from mpl_toolkits.mplot3d import Axes3D

        # Increments
        dRot, incr = (2/pi)/Sides, self.Lengh/Sides

        # make the table
        [z,theta] = mgrid[0:self.Lengh:incr,0:2*pi:dRot]
        r = self.Radius # r only needs to be defined onces thaks to broadcasting
        x = r*np.cos(theta)
        y = r*np.sin(theta)

        # CenterPoint
        x = x + self.CenterPoint[0]
        y = y + self.CenterPoint[1]
        z = z + (-self.Lengh/2) + self.CenterPoint[2]

        # View it.
        # Mayavi Backend
        if backend == "Mayavi":
            if fig == None:
                fig = mlab.figure()
            s = mlab.mesh(x, y, z,color=color)
            if standalone:
                mlab.show()
            else:
                return fig

        # Matplotlib backend:
        elif backend == "Matplotlib":
            if fig == None:
                # fig[0]--> plt.figure,
                # fig[1]--> plt.axes
                figure = plt.figure()
                ax = figure.add_subplot(111, projection='3d')
                fig = (figure,ax)
            fig[1].scatter(x,y,z)
            if standalone:
                plt.show()
            else:
                return fig
