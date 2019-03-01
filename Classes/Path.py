# -*- coding: utf-8 -*-
from __future__ import print_function
try:
    import numpy as np
    import copy
    import sys
    from math import *

except:
    print("Unable to import some modules\nfunctions and classes might not work properly")

class path:

    def __init__(self,Lx=[],Ly=[],Lz=[]):
        self.Lx = copy.deepcopy(Lx)
        self.Ly = copy.deepcopy(Ly)
        self.Lz = copy.deepcopy(Lz)
        self.NbPoints = len(Lx)

    def InitLinear(self,LinearMatrix,Lengh,NbPoints,OffX = 0, OffY = 0, OffZ = 0):
        """
            Équation paramétrique de la droite
            {x = Cx*t+Ax;y = Cy*t+Ay;z = Cz*t+Az}
        """

        self.NbPoints = NbPoints
        self.Lengh = Lengh
        Cx = LinearMatrix[0][0]
        Cy = LinearMatrix[0][1]
        Cz = LinearMatrix[0][2]
        Ax = LinearMatrix[1][0]
        Ay = LinearMatrix[1][1]
        Az = LinearMatrix[1][2]

        # Increments, max and min of the "t" parameter
        tMax = Lengh/(np.sqrt(Cx**2+Cy**2+Cz**2))
        tMin = 0
        tInc = tMax/(NbPoints-1)

        #Generation of the tables
        tTemp = 0
        for i in range(NbPoints):
            self.Lx.append(Cx*tTemp+Ax)
            self.Ly.append(Cy*tTemp+Ay)
            self.Lz.append(Cz*tTemp+Az)
            tTemp +=tInc

    def Init3DSinus(self,LinearMatrix,Lengh,NbPoints,Omega,Phi,R0,Cth,Th0,OffX = 0, OffY = 0, OffZ = 0):
        """

            The linear matrix parameter
            is defined as follow:
            [[Cx,Cy,Cz],
             [Ax,Ay,Az]]

            Équation paramétrique de la droite
            {x = Cx*t+Ax;y = Cy*t+Ay;z = Cz*t+Az}

            Équation du sinus:
            définie en coordonées cylindriques autour de x
            x -> x ; y -> r sin(theta) ; y -> r cos(theta)
            {r = R0*sin(Omega*x+Phi), theta = Cth*x+Th0}

            OffX, OffY and OffZ are used to add offset to the
            filaments generate (between each filament in a strand
            for example)
        """

        self.NbPoints = NbPoints
        self.Lengh = Lengh
        Cx = LinearMatrix[0][0]
        Cy = LinearMatrix[0][1]
        Cz = LinearMatrix[0][2]
        Ax = LinearMatrix[1][0] + OffX
        Ay = LinearMatrix[1][1] + OffY
        Az = LinearMatrix[1][2] + OffZ


        # Increments, max and min of the "t" parameter
        tMax = Lengh
        tMin = 0
        tInc = tMax/(NbPoints-1)

        Base1 = Order3Base(e1 = [Cx,Cy,Cz], BuildFromThis = True)
        RotMat = ExtractRotationMatrix(Base1)

        #Generation of the tables
        tTemp = 0
        for i in range(NbPoints):
            # X coordinate
            self.Lx.append(Cx*tTemp+Ax)

            # Y coordinate
            Rtemp = R0*sin(tTemp+Phi)
            Thetatemp = Cth*tTemp + Th0
            SinusContribution = Rtemp * sin(Thetatemp)
            self.Ly.append(SinusContribution)

            # Z coordinate
            Rtemp = R0*sin(tTemp+Phi)
            Thetatemp = Cth*tTemp + Th0
            SinusContribution = Rtemp * cos(Thetatemp)
            self.Lz.append(SinusContribution)

            # Increment
            tTemp +=tInc

        coordinatesMatrix = np.array([self.Lx,self.Ly,self.Lz]).T
        RotatedCoordinateMatrix = np.dot(coordinatesMatrix,RotMat)
        self.Lx,self.Ly,self.Lz = RotatedCoordinateMatrix.T + np.array([[Ax],[Ay],[Az]]) #search for numby broadcasting if you
        # don't understand the sum

    def Init3DHelix(self,theta,DirectionParam,Pitch,Nby,Dbyin,Dbyout,PlaitSegments):
        from inPy.inPy_Constants import PI
        if DirectionParam == "CCW":
            DirectionCoeff = -1
        elif DirectionParam == "CW":
            DirectionCoeff = 1

        #Discretisation
        NumberOfPlaits = Nby/2; #Plait is defined as yarn path returning to its
        #initial value, there are two cross-overs in one plait.
        NumberOfPlaitsModelled = NumberOfPlaits #1 for only one plait or NumberOfPlaits for full pitch

        nodenum = [i+1 for i in range(int(NumberOfPlaitsModelled*PlaitSegments+1))]
        incr = 2*PI/(NumberOfPlaits*PlaitSegments)
        nodeangle = np.arange(0, (2*PI+incr),(incr))
        YarnPath = []

        for i in range(PlaitSegments+1):
            YarnPath.append((1+DirectionCoeff*np.cos(2*PI/PlaitSegments*(i-1)))*0.5)

        #in
        xIn = []
        yIn = []
        zIn = []

        #out
        xOut = []
        yOut = []
        zOut = []


        i = 0
        for j in range(int(NumberOfPlaitsModelled*PlaitSegments)+1):
            i=i+1
            if j==NumberOfPlaitsModelled*PlaitSegments+1:
                i = PlaitSegments+1

            #Inside Helix Points
            xIn.append(Dbyin/2*np.cos((-1*DirectionCoeff)*nodeangle[j]))
            yIn.append(Dbyin/2*np.sin((-1*DirectionCoeff)*nodeangle[j]))
            zIn.append(Pitch/(2*PI)*nodeangle[j])
            #rotation
            RotX=xIn[j]
            RotY=yIn[j]
            xIn[j] = RotX*np.cos(theta)-RotY*np.sin(theta);
            yIn[j] = RotY*np.cos(theta)+RotX*np.sin(theta);

            #Ouside Helix Points
            xOut.append(Dbyout/2*np.cos((-1*DirectionCoeff)*nodeangle[j]))
            yOut.append(Dbyout/2*np.sin((-1*DirectionCoeff)*nodeangle[j]))
            zOut.append(Pitch/(2*PI)*nodeangle[j])
            #rotation
            RotX=xOut[j]
            RotY=yOut[j]
            xOut[j] = RotX*np.cos(theta)-RotY*np.sin(theta);
            yOut[j] = RotY*np.cos(theta)+RotX*np.sin(theta);

            # Define vector linking inside and outside helix points
            Vx = xOut[j]-xIn[j];
            Vy = yOut[j]-yIn[j];
            Vz = zOut[j]-zIn[j];
            Length = np.sqrt(Vx**2+Vy**2+Vz**2);

            #Yarn centerline points xYC, yYC and zYC: These are the nodes of the
            #beam elements.
            self.Lx.append(xIn[j]+Vx*YarnPath[i])
            self.Ly.append(yIn[j]+Vy*YarnPath[i])
            self.Lz.append(zIn[j]+Vz*YarnPath[i])
            if i == PlaitSegments:
                i=0
        self.NbPoints = len(self.Lx)

    def MakeNodeList(self,ID0=0,R=0,YarnR=0):

        from inPy.Functions.Geometry import circlespacking
        from inPy.Classes.FEM import node,BeamMesh

        if R == 0:
            Rsup0 = False
            NodeList = []
            LastID = ID0
            for i in range(self.NbPoints):
                NodeList.append(node(self.Lx[i],self.Ly[i],self.Lz[i],ID0+i))
                LastID  = ID0+i
            return NodeList,LastID,Rsup0
        else:
            Rsup0 = True
            NodeListTable = []
            layers = int(((2*R)-(R+1))/2)
            number_of_filaments = sum([(i+1)*6 for i in range(layers)])
            FilamentCoord = circlespacking(R,YarnR)
            CurrentID = ID0
            for filament in range(len(FilamentCoord)):
                NodeList = []
                for i in range(self.NbPoints):
                    NodeList.append(node(self.Lx[i]+FilamentCoord[filament][0],self.Ly[i]+FilamentCoord[filament][1],self.Lz[i],ID0+i))
                    LastID  = CurrentID
                    CurrentID += 1
                NodeListTable.append(copy.deepcopy(NodeList))
            return NodeListTable,LastID,Rsup0
