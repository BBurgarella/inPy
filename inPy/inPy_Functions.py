# -*- coding: utf-8 -*-

import numpy as np
import copy
import sys

from inPy.inPy_Classes import *
from inPy.inPy_Constants import *

##########################
#	   	Functions		 #
##########################

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

def CreateDummyString(NodeNum,X,Y,Z):
    strtoreturn = ""
    strtoreturn += "**\n*Part, name = Dummy\n"
    strtoreturn += "*End Part\n**\n"
    return strtoreturn

def cart2polar(x,y):
	rho=np.sqrt(x**2+y**2)
	phi=np.arctan2(y,x)
	return(rho,phi);

def polar2cart(rho,phi):
	x=rho*np.cos(phi)
	y=rho*np.sin(phi)
	return(x,y);

def theta(i,Ri,Rt):
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

def fiberbasecoord(NbSeg,L,Ri,Rt,Rf,Phi0,Vr):
## Gives the coordinate vector on the fiber
## linear basis
############################################
##    xi linear coordinate on the fibre   ##
##     Ri inner radius of the poulie      ##
##      Rt radius of the fiber bundle     ##
############################################
    XList = []
    YList = []
    ZList = []
    k=1
#    print(int((pi*(Ri+Rt)/angle)))
    for i in range(NbSeg+int((pi*(Ri+Rt)/angle)/(float(L)/float(NbSeg)))):
        if (-(L/2)+(i*L/NbSeg)) <= 0:
            XList.append(-(L/2)+(i*L/NbSeg))
            YList.append(Rf*(math.sin(Phi0+Vr*(-(L/2)+(i*L/NbSeg)))))
            ZList.append(Rf*(math.cos(Phi0+Vr*(-(L/2)+(i*L/NbSeg)))))
        elif (-(L/2)+(i*L/NbSeg))  > 0 and (-(L/2)+(i*L/NbSeg))  < (pi*(Ri+Rt)/angle):
            XList.append(0)
            YList.append(Rf*(math.sin(Phi0+Vr*(-(L/2)+((i)*L/NbSeg)))))
            ZList.append(Rf*(math.cos(Phi0+Vr*(-(L/2)+((i)*L/NbSeg)))))
        elif (-(L/2)+(i*L/NbSeg))  >= (pi*(Ri+Rt)/angle):
            XList.append((k*L/NbSeg))
            YList.append(Rf*(math.sin(Phi0+Vr*(-(L/2)+(i*L/NbSeg)))))
            ZList.append(Rf*(math.cos(Phi0+Vr*(-(L/2)+(i*L/NbSeg)))))
            k+=1
    return [XList,YList,ZList]

def pouliebasecoord(CoordList,Ri,Rt,NoPenMargin):
    XList = CoordList[0]
    YList = CoordList[1]
    ZList = CoordList[2]
    XListPoulie = []
    YListPoulie = []
    ZListPoulie = []
    for i in range(len(XList)):
        tempVect = np.array([XList[i],YList[i]+(Ri+NoPenMargin),ZList[i]])
        ThetaVal = theta(i,Ri,Rt)
        if ThetaVal >= 0 and ThetaVal <= pi/2:
           tempVect = np.array([XList[i],YList[i]+(Ri+NoPenMargin),ZList[i]])
        #print(ThetaVal*(180/pi))
        RotationMatrix = np.array([[math.cos(ThetaVal),-math.sin(ThetaVal),0],[math.sin(ThetaVal),math.cos(ThetaVal),0],[0,0,1]])
        PoulieBaseVect = np.dot(tempVect,RotationMatrix)
        XListPoulie.append(PoulieBaseVect[0])
        YListPoulie.append(PoulieBaseVect[1])
        ZListPoulie.append(PoulieBaseVect[2])
    if Abaqus == 0:
        plt.plot(XListPoulie,ZListPoulie, 'r')
        plt.plot(XListPoulie,YListPoulie, 'r')
        plt.xlim(-L/Zoom,L/Zoom)
        plt.ylim(-L/Zoom,L/Zoom)
        plt.show()
    return [XListPoulie,YListPoulie,ZListPoulie]

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
