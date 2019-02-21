# -*- coding: utf-8 -*-

import numpy as np
import copy
import sys
import pdb
from math import *

from inPy.inPy_Classes import *
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

######################################
#	   FEM specific functions		 #
######################################

def CreateDummyString(NodeNum,X,Y,Z):
    strtoreturn = ""
    strtoreturn += "**\n*Part, name = Dummy\n"
    strtoreturn += "*End Part\n**\n"
    return strtoreturn

##################################
#	   Geometry functions		 #
##################################

def cart2polar(x,y):
	rho=np.sqrt(x**2+y**2)
	phi=np.arctan2(y,x)
	return(rho,phi);

def polar2cart(rho,phi):
	x=rho*np.cos(phi)
	y=rho*np.sin(phi)
	return(x,y);

def Get_angle(Vector1,Vector2):
    return acos(np.dot(Vector1,Vector2)/(np.linalg.norm(Vector1)*np.linalg.norm(Vector2)))

def ExtractRotationMatrix(Base_1,Base_0 = None):
    from inPy.inPy_Classes import Order3Base
    """
    This function returns the rotation matrix to get from one base to the
    other. If Base_0 is not specified, it is assumed that the target
    base is e1 = [1,0,0], e1 = [0,1,0], e1 = [0,0,1]

    if Norm is set to False, it is assumed that the used gave
    an already normalized base

    This very simple implementation was found here:
    https://stackoverflow.com/questions/50474886/finding-rotation-matrix-to-transform-one-3-vector-basis-to-another-in-3d

    """
    # Normalization of the user input
    if Base_0 == None:
        Base_0 = Order3Base()
    # Proper code of the function
    MatB_1 = np.array([Base_1[0],Base_1[1],Base_1[2]])
    MatB_0 = np.array([Base_0[0],Base_0[1],Base_0[2]])

    return np.linalg.solve(MatB_1,MatB_0).T




def theta(i,Ri,Rt,angle,L,NbSeg):
    if angle == 0:
        return 0
    ## Gives the rotation angle of the base
    ## depending of the position on the fiber.
    ############################################
    ##    xi linear coordinate on the fibre   ##
    ##     Ri inner radius of the poulie      ##
    ##      Rt radius of the fiber bundle     ##
    ############################################
    if (-(L/2)+(i*L/NbSeg)) <= 0:
        return 0
    elif (-(L/2)+(i*L/NbSeg))  > 0 and (-(L/2)+(i*L/NbSeg))  < (pi*(Ri+Rt)/angle):
#        print(xi/(Ri+Rt)*(180/pi))
        return (-(L/2)+((i)*L/NbSeg))/(Ri+Rt)
    elif (-(L/2)+(i*L/NbSeg))  >= (pi*(Ri+Rt)/angle):
        return (pi/angle)


def circlespace(xC,yC,radius,n):
	X=[];
	Y=[];
	THETA = np.linspace(0,2*np.pi,n)
	RHO = np.ones((1,n))*radius
	X, Y = polar2cart(RHO,THETA)
	X = X + xC
	Y = Y + yC
	#print(RHO)
	#print(X,Y)
	return X,Y

def circlespacking(R,yarnR):
	xy_disc = []
	num_cercles = []
	layers = []
	#FiberR = yarnR/R
	#xouterc, youterc = circlespace(0,0,R,1000)
	#pyplot.plot(xouterc,youterc,'k.')
	#xinnerc, yinnerc = circlespace(0,0,1,100)
	#pyplot.plot(xinnerc,yinnerc,'k.')
	layers = int(((2*R)-(R+1))/2)
	#print (layers)
	if layers != 0:
		for i in range(0,layers):
			num_cercles = (i+1)*6
			xcoor,ycoor = circlespace(0,0,(i+1)*2,num_cercles+1)
			x_disc = np.zeros((1,num_cercles+1))
			y_disc = np.zeros((1,num_cercles+1))
			#print x_disc,y_disc
			for j in range(0,num_cercles):
				x_disc[0][j] = (xcoor[0][j]*yarnR)/R
				y_disc[0][j] = (ycoor[0][j]*yarnR)/R
				xy_disc.append((x_disc[0][j],y_disc[0][j]))
		x_disc[0][j+1] = 0
		y_disc[0][j+1] = 0
		xy_disc.append((x_disc[0][j+1],y_disc[0][j+1]))
	elif layers == 0:
		xy_disc.append((0,0))
	return xy_disc


def OvalDistribution(yarnR,Setup = "Hex",R1=None,R2=None,SparsingCoeff=0):

    """
    This function returns an array of coordinates
    similarly to circle packing, the objective is to fit
    circles (fibers) is a specific shape

    Valid arguments for Setup are: "Hex" and "Square"

    """
    #Generate candidate fibers matrix
    if Setup == "Hex":
        # Horizontal and vertical coefficients
        # calculated to  determine how many candidates
        # should be generated
        VerticalDistanceCoeff = 2*yarnR*cos(30*PI/180)*(1+SparsingCoeff)
        HorizontalDistanceCoeff = 2*yarnR*(1+SparsingCoeff)

        # Number of candidates to generate, depending on
        # the factors calculated right above
        HorNbCandidates = int((3*R1)/(HorizontalDistanceCoeff))
        VertNbCandidates = int((3*R2)/(VerticalDistanceCoeff))

        # Offset between layers (two layers might not be aligned exept for example
        # for square packing)
        HorizOffsetBetweenLayers = sin(30*PI/180)*2*yarnR
    elif Setup == "Square":
        # Horizontal and vertical coefficients
        # calculated to  determine how many candidates
        # should be generated
        VerticalDistanceCoeff = 2*yarnR*(1+SparsingCoeff)
        HorizontalDistanceCoeff = 2*yarnR*(1+SparsingCoeff)

        # Number of candidates to generate, depending on
        # the factors calculated right above
        HorNbCandidates = int((3*R1)/(HorizontalDistanceCoeff))
        VertNbCandidates = int((3*R2)/(VerticalDistanceCoeff))

        # Offset between layers (two layers might not be aligned exept for example
        # for square packing)
        HorizOffsetBetweenLayers = 0

    candidatesTable = []
    for VLayer in range(VertNbCandidates):
        for HLayer in range(HorNbCandidates):
            # The X coordiante is determined from -R1 to R1
            # The offset is only added for odd layers
            XCandidate = -R1*1.5+ yarnR + ((HLayer)*HorizontalDistanceCoeff) + VLayer%2*HorizOffsetBetweenLayers
            YCandidate = -R2*1.5+ yarnR + (((VLayer)*VerticalDistanceCoeff))
            candidatesTable.append([XCandidate,YCandidate])
    SelectedTable = []
    for PossibleFiber in candidatesTable:
        if ((abs(PossibleFiber[0])+yarnR)/R1)**2 + ((abs(PossibleFiber[1])+yarnR)/R2)**2 <= 1:
            SelectedTable.append(PossibleFiber)
    return SelectedTable

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
