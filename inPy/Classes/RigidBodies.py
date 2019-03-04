# -*- coding: utf-8 -*-
from __future__ import print_function
try:
    import numpy as np
    import copy
    import sys
    from random import random
    from math import *
    from inPy.Classes.Assembly import Instance

except:
    print("Unable to import some modules\nfunctions and classes might not work properly")


"""
In this file, all the classes defined will be used to generate
Rigid Bodies

"""

class rigid_Body(Instance):

    """
    Master class, all the other classes should herit from this one

    """

    def __init__(self, Name, Density, RotInertiaMatrix = None, CenterPoint=[0,0,0], RotVect = [0,0,0],**kwargs):
        """
        A Rigid body of any shape should be defined by a name, a Matrix to store its
        rotary intertias, a center point (Should always refer to the center of mass), a translation vector,
        and a rotation vector

        The rotation vector is defined as the angles (rad) to respectively rotate around each axis of the
        chosen base

        I only use **kwargs because I dislike how its harder to know what an *arg will be used for

        """
        from inPy.Classes.Geometry import Order3Base
        from inPy.Functions.linalg import RotVect_to_RotMat

        super().__init__(**kwargs)

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
        self.RotInertiaMatrix = np.array([[0.001,0,0],[0,0.001,0],[0,0,0.001]])

        # Rotation vector
        self.RotVect = RotVect
        self.RotMat = RotVect_to_RotMat(RotVect)

        # Generation method
        # None => by giving a series of points
        # Extrude => Extrude a surface over a lengh
        # Revolution => Takes a surface and makes a revolution solid
        self.GenMethod = None

    def Generate_PartINP_String(self):

        """
        This function returns the string to
        add to the inp when generating the parts

        """
        #raise ValueError("The Generate_INP_String method have not been overrided for this subclass and\
        #is therefore empty, you must override this method when subclassing the rigid_Body class")

        inpString = ""

        # First we need to create an empty part
        inpString += "**\n*Part, name={}\n".format(self.Name)

        if self.GenMethod == "Revolution":
            # Create analytical surface
            inpString += "*Surface, type=REVOLUTION, name={}-Surface\n".format(self.Name)
            inpString += self.PolygonString()

        if self.GenMethod == "Extrusion":
            # Create analytical surface
            inpString += "*Surface, type=CYLINDER, name={}-Surface\n".format(self.Name)
            #inpString += "{},{}\n".format(OriginString,XLocalString)
            inpString += self.PolygonString()

        # Create the reference point
        Node_ID = self.Get_NodeID()
        inpString += "*Node\n{}, 0., 0., 0.\n".format(Node_ID)
        # Node sets for the reference point
        inpString += "*Nset,nset={}-RefPt_, internal\n{},\n".format(self.Name,Node_ID)
        inpString += "*Nset, nset=set-RefPt{}, internal\n{},\n".format(self.Name,Node_ID)


        inpString += "*End Part\n"

        return inpString

    def Generate_AssemblyINP_String(self):

        from inPy.inPy_Constants import PI

        """
        this function returns the string to add to the inp file
        when building the assembly

        """
        #raise ValueError("The Generate_INP_String method have not been overrided for this subclass and\
        #is therefore empty, you must override this method when subclassing the rigid_Body class")

        inpString = ""

        # First we need to create an empty part
        inpString += "**\n*Instance, name={}, part={}\n".format(self.Name,self.Name)
        # Translation of the center point
        inpString += "{}, {}, {}\n".format(self.CenterPoint[0],self.CenterPoint[1],self.CenterPoint[2])

        #Rotations
        OriginString = "{}, {}, {}".format(self.CenterPoint[0],self.CenterPoint[1],self.CenterPoint[2])
        XLocalString = "{}, {}, {}".format(self.CenterPoint[0]+1,self.CenterPoint[1],self.CenterPoint[2])
        YLocalString = "{}, {}, {}".format(self.CenterPoint[0],self.CenterPoint[1]+1,self.CenterPoint[2])
        ZLocalString = "{}, {}, {}".format(self.CenterPoint[0],self.CenterPoint[1],self.CenterPoint[2]+1)

        #Rotation #1
        inpString +="{}, {}, {}\n".format(OriginString,XLocalString,self.RotVect[0]*180/PI)
        #Rotation #2
        inpString +="{}, {}, {}\n".format(OriginString,YLocalString,self.RotVect[0]*180/PI)
        #Rotation #3
        inpString +="{}, {}, {}\n".format(OriginString,ZLocalString,self.RotVect[0]*180/PI)

        # Create the rigid body reference in abaqus
        inpString += "*Rigid Body, ref node={}-RefPt_, analytical surface={}-Surface\n".format(self.Name,self.Name)
        inpString += "*Element, type=MASS, elset=Set-RefPt{}_{}Intertia_MASS_\n".format(self.Name,self.Name)
        inpString += "1, 1\n"
        inpString += "*Mass, elset=Set-RefPt{}_{}Intertia_MASS_\n".format(self.Name,self.Name)
        inpString += "10.,\n"
        inpString += "*Element, type=ROTARYI, elset=Set-RefPt{}_{}Intertia_ROTI_\n".format(self.Name,self.Name)
        inpString += "2, 1\n"
        inpString += "*Rotary Inertia, elset=Set-RefPt{}_{}Intertia_ROTI_\n".format(self.Name,self.Name)
        inpString += "{}, {}, {}, {}, {}, {}\n".format(self.RotInertiaMatrix[0,0],self.RotInertiaMatrix[1,1],self.RotInertiaMatrix[2,2],\
        self.RotInertiaMatrix[0,1],self.RotInertiaMatrix[0,2],self.RotInertiaMatrix[1,2])

        # End the instance definition
        inpString += "*End Instance\n"

        return inpString

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
    def __init__(self, Name, Density,ShapeString, ShapeArgs, RotInertiaMatrix = None, CenterPoint=[0,0,0], RotVect = [0,0,0],**kwargs):

        # init parent class (rigid_Body)
        super().__init__(Name, Density, RotInertiaMatrix = RotInertiaMatrix, CenterPoint=CenterPoint, RotVect = RotVect,**kwargs)

        if ShapeString == "Cyl":
            self.Radius = ShapeArgs[0]
            self.Lengh = ShapeArgs[1]
            self.GenMethod = "Revolution"

    def PolygonString(self):
        PolyString = ""
        # Draw a square that will be revoluted
        PolyString += "START, 0., {}\n".format(self.Lengh/2)
        PolyString += " LINE, {}, {}\n".format(self.Radius,self.Lengh/2)
        PolyString += " LINE, {}, {}\n".format(self.Radius,-self.Lengh/2)
        PolyString += " LINE, 0, {}\n".format(self.Radius,-self.Lengh/2)
        return PolyString

    def Draw(self,Sides = 100,color=(random(),random(),random()),standalone=True,fig = None):
        # Create the data.
        from numpy import pi, sin, cos, mgrid
        import inPy.Backend.BackendPlot as PlotBundle

        # Increments
        dRot, incr = (2/pi)/Sides, self.Lengh/Sides

        # make the table
        [z,theta] = mgrid[0:self.Lengh:incr,0:2*pi:dRot]
        r = self.Radius # r only needs to be defined onces thanks to broadcasting
        x = r*np.cos(theta)
        y = r*np.sin(theta)

        # CenterPoint
        x = x + self.CenterPoint[0]
        y = y + self.CenterPoint[1]
        z = z + (-self.Lengh/2) + self.CenterPoint[2]

        Coords = np.transpose([x,y,z])
        RealCoords = np.transpose(np.dot(Coords,self.RotMat))

        # View it.
        fig = PlotBundle.Plot_surface(RealCoords[0],RealCoords[1],RealCoords[2],fig)
        if standalone:
            PlotBundle.show()
        else:
            return fig


class SquareSectionBar(rigid_Body):

    def __init__(self, Name, Density, ShapeArgs, RotInertiaMatrix = None, CenterPoint=[0,0,0], RotVect = [0,0,0]):

        # init parent class (rigid_Body)
        super().__init__(Name, Density, RotInertiaMatrix = RotInertiaMatrix, CenterPoint=CenterPoint, RotVect = RotVect)

        self.L1 = ShapeArgs[0]
        self.L2 = ShapeArgs[1]
        self.Lengh = ShapeArgs[2]
        self.GenMethod = "Extrusion"

    def PolygonString(self):
        PolyString = ""
        # Draw a square that will be revoluted
        PolyString += "START, {}, {}\n".format(-self.L1/2,self.L2/2)
        PolyString += " LINE, {}, {}\n".format(-self.L1/2,-self.L2/2)
        PolyString += " LINE, {}, {}\n".format(self.L1/2,-self.L2/2)
        PolyString += " LINE, {}, {}\n".format(self.L1/2,self.L2/2)
        PolyString += " LINE, {}, {}\n".format(-self.L1/2,self.L2/2)
        return PolyString


    def Draw(self,color=(random(),random(),random()),standalone=True,fig = None):
        # Create the data.
        from numpy import pi, sin, cos, mgrid
        import inPy.Backend.BackendPlot as PlotBundle

        # make the table
        x = np.array([[-self.L1/2,self.L1/2,self.L1/2,-self.L1/2,-self.L1/2],[-self.L1/2,self.L1/2,self.L1/2,-self.L1/2,-self.L1/2]]) # Coordinates going in clockwise and positive z order
        y = np.array([[self.L2/2,self.L2/2,-self.L2/2,-self.L2/2,self.L2/2],[self.L2/2,self.L2/2,-self.L2/2,-self.L2/2,self.L2/2]])
        z = np.array([[-self.Lengh/2,-self.Lengh/2,-self.Lengh/2,-self.Lengh/2,-self.Lengh/2],[self.Lengh/2,self.Lengh/2,self.Lengh/2,self.Lengh/2,self.Lengh/2]])

        # CenterPoint
        x = x + self.CenterPoint[0]
        y = y + self.CenterPoint[1]
        z = z + self.CenterPoint[2]

        Coords = np.transpose([x,y,z])
        RealCoords = np.transpose(np.dot(Coords,self.RotMat))

        # View it.
        fig = PlotBundle.Plot_surface(RealCoords[0],RealCoords[1],RealCoords[2],fig)
        if standalone:
            PlotBundle.show()
        else:
            return fig
