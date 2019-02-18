# -*- coding: utf-8 -*-
from __future__ import print_function
try:
    import numpy as np
    import copy
    import sys
except:
    print("Unable to import some modules\nfunctions and classes might not work properly")

from inPy.inPy_Constants import *
from inPy.inPy_Functions import *


##################################
#		Class definitions		 #
##################################

class node():

    def __init__(self,X,Y,Z,ID):
        """
            class definition, to enter a node, one need to give three coordinates and an ID
            The coordinates should be entered as follow: X,Y,Z
            using the syntax Foonode = node(X,Y,Z,ID)
        """
        self.X = X
        self.Y = Y
        self.Z = Z
        self.ID = ID

    def string(self):
        """
            This method is used to generate the inp instructions to generate the node in abaqus
            no parameter is required and the output is directly a string that can be added
            to an inp file
        """
        string = ""
        string += str(int(self.ID))
        string += ", "+str(self.X)
        string += ", "+str(self.Y)
        string += ", "+str(self.Z)
        return string

class LineElement():
    def __init__(self,Node1,Node2,ID):
        self.N1 = copy.deepcopy(Node1)
        self.N2 = copy.deepcopy(Node2)
        self.ID = ID

    def string(self):
        string = ""
        string += str(int(self.ID))
        string += ", "+str(self.N1.ID)
        string += ", "+str(self.N2.ID)
        return string

class PartMesh():

    def __init__(self,Namestr,ElemType,Radius,TypeStr,PosStr,NodeList=[],ElemList=[],Node0 = 1,Elem0 = 1):
        self.NodeList = []
        self.Type = TypeStr
        self.Position = PosStr
        self.NodeList = copy.deepcopy(NodeList)
        self.ElemList = []
        self.ElemList = copy.deepcopy(ElemList)
        self.Namestr = Namestr
        self.ElemType=ElemType
        self.Radius = Radius
        self.Elem0 = Elem0

        # if the used mistakingly forgot to enter either an element list or a node list
        if len(NodeList)==0 and len(ElemList)==0:
            print("Erreur #01, please enter at least a list of nodes or a list of elements")

        # if the user only gives an element list
        elif len(NodeList)==0:
            for i in range(len(ElemList)):
                self.NodeList.append(ElemList[i].node1)
            self.NodeList.append(ElemList[i].node2)

        # if the use only gives a node list
        elif len(self.ElemList)==0:
            for i in range(len(self.NodeList)-1):
                self.ElemList.append(LineElement(self.NodeList[i],self.NodeList[i+1],i+self.Elem0))

        self.MinNodeID = self.NodeList[0].ID
        self.MaxNodeID = self.NodeList[-1].ID
        self.MinElemID = self.ElemList[0].ID
        self.MaxElemID = self.ElemList[-1].ID


    def InpPart(self):
        FileStr = "*PART, NAME="+self.Namestr+"\n*NODE, NSET="+str(self.Namestr)+"\n"
        for i in (self.NodeList):
            FileStr += i.string()+"\n"
        FileStr += "*ELEMENT, type="+self.ElemType+", ELSET="+str(self.Namestr)+"\n"
        for i in (self.ElemList):
            FileStr += i.string()+"\n"


        if self.Type == "Beam":
            FileStr += "** Section: "+str(self.Namestr)+"  Profile:"+str(self.Namestr)+"\n"
            FileStr += "*Beam Section,  elset="+str(self.Namestr)+", material=FiberMat, temperature=GRADIENTS, section=CIRC\n"
            FileStr += str(self.Radius*0.9)+"\n"
            FileStr += "0.,0.,-1\n"


        if self.Type == "Truss":
            FileStr += "** Section: "+str(self.Namestr)+"  Profile:"+str(self.Namestr)+"\n"
            FileStr += "*Solid Section,  elset="+str(self.Namestr)+", material=FiberMat\n"
            FileStr += str(PI*(self.Radius*0.9)**2)+"\n"

            FileStr += "*Rotary Inertia, elset="+str(self.Namestr)+"\n"
            FileStr += str(RotInertia)+", "+str(RotInertia)+", "+str(RotInertia)+", 0., 0., 0.\n"

        FileStr +="*END PART\n**\n"
        return FileStr

class EmbededBeam():

    def __init__(self,PartMesh,BundleR,FilR):
        self.source = copy.deepcopy(PartMesh)
        self.BundleRadius = BundleR
        self.FilR = FilR
        self.OUT = copy.deepcopy(self.source)
        self.OUT.Namestr = self.source.Namestr+"OUT"
        self.IN = []

    def Generate(self,Config = ["Truss","Beam"]):
        Startcount = self.source.MaxNodeID
        NewNodeList = copy.deepcopy(self.source.NodeList)
        count = 1
        for i in NewNodeList:
            i.ID = Startcount+count
            count+=1
        if Config[1]=="Beam":
            self.IN = PartMesh(self.source.Namestr+"IN","B31",self.FilR,Config[1],"IN",NodeList=NewNodeList,ElemList=[],Elem0 = self.source.MaxElemID+1)
            return self.OUT.InpPart()+self.IN.InpPart()
        if Config[1]=="Truss":
            self.IN = PartMesh(self.source.Namestr+"IN","T3D2",self.FilR,Config[1],"IN",NodeList=NewNodeList,ElemList=[],Elem0 = self.source.MaxElemID+1)
            return self.OUT.InpPart()+self.IN.InpPart()
        if Config[1]==None:
            return self.OUT.InpPart()


class path:

    def __init__(self,Lx=[],Ly=[],Lz=[]):
        self.Lx = copy.deepcopy(Lx)
        self.Ly = copy.deepcopy(Ly)
        self.Lz = copy.deepcopy(Lz)
        self.NbPoints = len(Lx)

    def InitLinear(self,LinearMatrix,Lengh,NbPoints):
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



    def MakeNodeList(self,ID0=0,R=0,YarnR=0):
        if R == 0:
            Rsup0 = False
            NodeList = []
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


class Braid:

    def __init__(self,Pitch,Nby,Dbyin,BraidThickness,PlaitSegments,BundleR,FilR,R):

        """ Credits to Louis for most of the code in this class
        """

        self.Pitch = Pitch
        self.R = R
        self.BundleR = BundleR
        self.FilR = FilR
        self.Nby = Nby
        self.Dbyin = Dbyin
        self.BraidThickness = BraidThickness
        self.Dbyout = Dbyin+BraidThickness*2
        self.CCWpath = []
        self.CWpath = []
        self.inpString = ""

        #Discretisation
        self.NumberOfPlaits = self.Nby/2; #Plait is defined as yarn path returning to its
        #initial value, there are two cross-overs in one plait.
        self.NumberOfPlaitsModelled = self.NumberOfPlaits #1 for only one plait or NumberOfPlaits for full pitch
        self.PlaitSegments = PlaitSegments;

        self.nodenum = [i+1 for i in range(int(self.NumberOfPlaitsModelled*self.PlaitSegments+1))]
        incr = 2*PI/(self.NumberOfPlaits*self.PlaitSegments)
        self.nodeangle = np.arange(0, (2*PI+incr),(incr))

        #Define yarn path multiplicator of the length between the inside and outside
        #Helix. Yarnpath is defined for one plait only for CCW and CW yarns. It has n=PlaitSegments+1 values.
        #Note that YarnPath(1) is equal to YarnPath(PlaitSegments+1). Value
        #of Yarnpath changes between 0 at inside helix to 1 at outside helix.

        self.YarnPathCCW = []   #Counter ClockWise
        self.YarnPathCW = []    #ClockWise

        for i in range(self.PlaitSegments+1):
            self.YarnPathCCW.append((1-np.cos(2*PI/self.PlaitSegments*(i-1)))*0.5)
            self.YarnPathCW.append((1+np.cos(2*PI/self.PlaitSegments*(i-1)))*0.5)


        #######################
        #CounterClockwiseYarns#
        #######################

        #in
        xInCCW = []
        yInCCW = []
        zInCCW = []

        #out
        xOutCCW = []
        yOutCCW = []
        zOutCCW = []

        xYCCCW = []
        yYCCCW = []
        zYCCCW = []

        for k in range(int(self.Nby/2)):
            # Python specificity, I need to initiate the new table
            xInCCW.append([])
            yInCCW.append([])
            zInCCW.append([])

            xOutCCW.append([])
            yOutCCW.append([])
            zOutCCW.append([])

            xYCCCW.append([])
            yYCCCW.append([])
            zYCCCW.append([])

            theta = 2*PI*(k-1)/(self.Nby/2) #rotation angle for the yarn
            i = 0
            for j in range(int(self.NumberOfPlaitsModelled*self.PlaitSegments)+1):
                i=i+1
                if j==self.NumberOfPlaitsModelled*self.PlaitSegments+1:
                    i = self.PlaitSegments+1

                #Inside Helix Points
                xInCCW[k].append(self.Dbyin/2*np.cos(self.nodeangle[j]))
                yInCCW[k].append(self.Dbyin/2*np.sin(self.nodeangle[j]))
                zInCCW[k].append(self.Pitch/(2*PI)*self.nodeangle[j])
                #rotation
                RotX=xInCCW[k][j]
                RotY=yInCCW[k][j]
                xInCCW[k][j] = RotX*np.cos(theta)-RotY*np.sin(theta);
                yInCCW[k][j] = RotY*np.cos(theta)+RotX*np.sin(theta);

                #Ouside Helix Points
                xOutCCW[k].append(self.Dbyout/2*np.cos(self.nodeangle[j]))
                yOutCCW[k].append(self.Dbyout/2*np.sin(self.nodeangle[j]))
                zOutCCW[k].append(self.Pitch/(2*PI)*self.nodeangle[j])
                #rotation
                RotX=xOutCCW[k][j]
                RotY=yOutCCW[k][j]
                xOutCCW[k][j] = RotX*np.cos(theta)-RotY*np.sin(theta);
                yOutCCW[k][j] = RotY*np.cos(theta)+RotX*np.sin(theta);

                # Define vector linking inside and outside helix points
                Vx = xOutCCW[k][j]-xInCCW[k][j];
                Vy = yOutCCW[k][j]-yInCCW[k][j];
                Vz = zOutCCW[k][j]-zInCCW[k][j];
                Length = np.sqrt(Vx**2+Vy**2+Vz**2);

                #Yarn centerline points xYC, yYC and zYC: These are the nodes of the
                #beam elements.
                xYCCCW[k].append(xInCCW[k][j]+Vx*self.YarnPathCCW[i])
                yYCCCW[k].append(yInCCW[k][j]+Vy*self.YarnPathCCW[i])
                zYCCCW[k].append(zInCCW[k][j]+Vz*self.YarnPathCCW[i])
                if i == PlaitSegments:
                    i=0
            self.CCWpath.append(path(Lx=xYCCCW[k],Ly=yYCCCW[k],Lz=zYCCCW[k]))

        #######################
        #ClockwiseYarns#
        #######################

        #in
        xInCW = []
        yInCW = []
        zInCW = []

        #out
        xOutCW = []
        yOutCW = []
        zOutCW = []

        xYCCW = []
        yYCCW = []
        zYCCW = []

        for k in range(int(self.Nby/2)):
            # Python specificity, I need to initiate the new table
            xInCW.append([])
            yInCW.append([])
            zInCW.append([])

            xOutCW.append([])
            yOutCW.append([])
            zOutCW.append([])

            xYCCW.append([])
            yYCCW.append([])
            zYCCW.append([])

            theta = 2*PI*(k-1)/(self.Nby/2) #rotation angle for the yarn
            i = 0
            for j in range(int(self.NumberOfPlaitsModelled*self.PlaitSegments)+1):
                i=i+1
                if j==self.NumberOfPlaitsModelled*self.PlaitSegments+1:
                    i = self.PlaitSegments+1

                #Inside Helix Points
                xInCW[k].append(self.Dbyin/2*np.cos(-1*self.nodeangle[j]))
                yInCW[k].append(self.Dbyin/2*np.sin(-1*self.nodeangle[j]))
                zInCW[k].append(self.Pitch/(2*PI)*self.nodeangle[j])
                #rotation
                RotX=xInCW[k][j]
                RotY=yInCW[k][j]
                xInCW[k][j] = RotX*np.cos(theta)-RotY*np.sin(theta);
                yInCW[k][j] = RotY*np.cos(theta)+RotX*np.sin(theta);

                #Ouside Helix Points
                xOutCW[k].append(self.Dbyout/2*np.cos(-1*self.nodeangle[j]))
                yOutCW[k].append(self.Dbyout/2*np.sin(-1*self.nodeangle[j]))
                zOutCW[k].append(self.Pitch/(2*PI)*self.nodeangle[j])

                #rotation
                RotX=xOutCW[k][j]
                RotY=yOutCW[k][j]
                xOutCW[k][j] = RotX*np.cos(theta)-RotY*np.sin(theta);
                yOutCW[k][j] = RotY*np.cos(theta)+RotX*np.sin(theta);

                # Define vector linking inside and outside helix points
                Vx = xOutCW[k][j]-xInCW[k][j];
                Vy = yOutCW[k][j]-yInCW[k][j];
                Vz = zOutCW[k][j]-zInCW[k][j];
                Length = np.sqrt(Vx**2+Vy**2+Vz**2);

                #Yarn centerline points xYC, yYC and zYC: These are the nodes of the
                #beam elements.
                xYCCW[k].append(xInCW[k][j]+Vx*self.YarnPathCW[i])
                yYCCW[k].append(yInCW[k][j]+Vy*self.YarnPathCW[i])
                zYCCW[k].append(zInCW[k][j]+Vz*self.YarnPathCW[i])
                if i == PlaitSegments:
                    i=0
            self.CWpath.append(path(Lx=xYCCW[k],Ly=yYCCW[k],Lz=zYCCW[k]))

    def GenerateInpString(self,R=0,AddDummy = True,Config = ["Truss","Beam"]):
        NodeListCCW = []
        NodeListCW = []
        BeamList = []
        if R == 0:
            Rprime = 1
        else:
            Rprime = R
        LastId = 1
        FirstNode = 2
        for k in range(int(self.Nby/2)):
            #Node Generation CCW
            if self.R == 0:
                MakeNodeListRes = self.CCWpath[k].MakeNodeList(ID0=10000*k+FirstNode)
                NodeListCCW.append(MakeNodeListRes[0])
                LastId = MakeNodeListRes[1]

                #Mesh Generation
                string = "BeamCCW"+str(k)
                if Config[0] == "Truss":
                    BeamList.append(PartMesh(string,"T3D2",self.BundleR/Rprime,Config[0],"OUT",NodeList=NodeListCCW[k],Elem0 = 10000*k+1))
                if Config[0] == "Beam":
                    BeamList.append(PartMesh(string,"B31",self.BundleR/Rprime,Config[0],"OUT",NodeList=NodeListCCW[k],Elem0 = 10000*k+1))
            else:
                MakeNodeListRes = self.CCWpath[k].MakeNodeList(ID0=10000*k+1,R=self.R,YarnR=self.BundleR)
                for i in range(len(MakeNodeListRes[0])):
                    NodeListCCW.append(MakeNodeListRes[0][i])
                    LastId = MakeNodeListRes[1]

                    #Mesh Generation
                    string = "BeamCCW"+str(k)+"_"+str(i)
                    if Config[0] == "Truss":
                        BeamList.append(PartMesh(string,"T3D2",self.BundleR/Rprime,Config[0],"OUT",NodeList=NodeListCCW[i+(k*len(MakeNodeListRes[0]))],Elem0 = 10000*k+1))
                    if Config[0] == "Beam":
                        BeamList.append(PartMesh(string,"B31",self.BundleR/Rprime,Config[0],"OUT",NodeList=NodeListCCW[i+(k*len(MakeNodeListRes[0]))],Elem0 = 10000*k+1))

        print("------------------------------------------------------------------\n------------------------CCW Beams Generated-----------------------")
        for k in range(int(self.Nby/2)):
            if self.R == 0:
                MakeNodeListRes = self.CWpath[k].MakeNodeList(ID0=10000*k+1)
                NodeListCW.append(MakeNodeListRes[0])
                LastId = MakeNodeListRes[1]

                #Mesh Generation
                string = "BeamCW"+str(k)
                if Config[0] == "Truss":
                    BeamList.append(PartMesh(string,"T3D2",self.BundleR/Rprime,Config[0],"OUT",NodeList=NodeListCW[k],Elem0 = 10000*k+1))
                if Config[0] == "Beam":
                    BeamList.append(PartMesh(string,"B31",self.BundleR/Rprime,Config[0],"OUT",NodeList=NodeListCW[k],Elem0 = 10000*k+1))
            else:
                MakeNodeListRes = self.CWpath[k].MakeNodeList(ID0=1000*k+1,R=self.R,YarnR=self.BundleR)
                for i in range(len(MakeNodeListRes[0])):
                    NodeListCW.append(MakeNodeListRes[0][i])
                    LastId = MakeNodeListRes[1]

                    #Mesh Generation
                    string = "BeamCW"+str(k)+"_"+str(i)
                    if Config[0] == "Truss":
                        BeamList.append(PartMesh(string,"T3D2",self.BundleR/Rprime,Config[0],"OUT",NodeList=NodeListCW[i+(k*len(MakeNodeListRes[0]))],Elem0 = 10000*k+1))
                    if Config[0] == "Beam":
                        BeamList.append(PartMesh(string,"B31",self.BundleR/Rprime,Config[0],"OUT",NodeList=NodeListCW[i+(k*len(MakeNodeListRes[0]))],Elem0 = 10000*k+1))

        if AddDummy == True:
                self.inpString += CreateDummyString(1,0,0,0)
        for i in BeamList:
                Validation = EmbededBeam(i,self.BundleR/Rprime,self.FilR)
                self.inpString += Validation.Generate(Config = Config)
        print("------------------------------------------------------------------\n------------------------CW Beams Generated------------------------")
        #Assembly
        self.inpString += "**ASSEMBLY\n**\n*Assembly, name = Assembly\n"
        if AddDummy == True:
            self.inpString += "**\n*Instance, name = DummyInstance, part  = dummy\n*End Instance\n"
            self.inpString += "*Node\n      1,           0.,           0.,           0.\n"
            self.inpString += "*Nset, nset=DummySet, internal\n1,\n"
            self.inpString += "*Nset, nset=DummySet\n1,\n"
        for i in BeamList:
            if Config[1] != None:
                self.inpString += "**\n"
                self.inpString += "*Instance, name="+i.Namestr+"IN,part="+i.Namestr+"IN\n"
                self.inpString += "*End Instance\n"
            self.inpString += "**\n"
            self.inpString += "*Instance, name="+i.Namestr+"OUT,part="+i.Namestr+"OUT\n"
            self.inpString += "*End Instance\n"
        print("------------------------------------------------------------------\n---------------------------Assembly done--------------------------")

        #Set creation for Embeded beams
        if Config[1] != None:
            self.inpString += "**\n"
            temp=0
            for beam in BeamList:
                for node in beam.NodeList:
                    self.inpString += "*Nset, nset=m_"+beam.Namestr+"_"+str(int(node.ID))+", instance="+beam.Namestr+"IN\n "
                    self.inpString += str(int(node.ID+(len(beam.NodeList))))+",\n"
                    self.inpString += "*Nset, nset=s_"+beam.Namestr+"_"+str(int(node.ID))+", instance="+beam.Namestr+"OUT\n "
                    self.inpString += str(int(node.ID))+",\n"
                    self.inpString += "*Surface, type=NODE, name ="+beam.Namestr+"_"+str(int(node.ID))+"_CNS, internal\ns_"+beam.Namestr+"_"+str(int(node.ID))+", 1\n"
                    temp+=1
                    if PyVersion >= 3:
                        print("\rSet creation for embeded beams: "+str(int(temp/(len(BeamList)*len(beam.NodeList))*1000)/10)+"%",end="\r")
                    else:
                        print("\rSet creation for embeded beams: "+str(int(temp/(len(BeamList)*len(beam.NodeList))*1000)/10)+"%")

        #Set creation for PBCs
        self.inpString += "**\n"
        temp=0
        for beam in BeamList:
            #############################
            # By convention, I always take the first node as the master
            # and the last as the Slave
            #############################
            # Master node, Inside beam
            if Config[1] != None:
                self.inpString += "*Nset, nset=m_"+beam.Namestr+"_IN_PBC, instance="+beam.Namestr+"IN\n "
                self.inpString += str(int(beam.MinNodeID+(len(beam.NodeList))))+",\n"
                # Slave node, Inside beam
                self.inpString += "*Nset, nset=s_"+beam.Namestr+"_IN_PBC, instance="+beam.Namestr+"IN\n "
                self.inpString += str(int(beam.MaxNodeID+(len(beam.NodeList))))+",\n"
                # Surface creation
                self.inpString += "*Surface, type=NODE, name ="+beam.Namestr+"_IN_CNS, internal\ns_"+beam.Namestr+"_IN_PBC, 1\n"

            self.inpString += "**\n"
            # Master node, Inside beam
            self.inpString += "*Nset, nset=m_"+beam.Namestr+"_OUT_PBC, instance="+beam.Namestr+"OUT\n "
            self.inpString += str(int(beam.MinNodeID))+",\n"
            # Slave node, Inside beam
            self.inpString += "*Nset, nset=s_"+beam.Namestr+"_OUT_PBC, instance="+beam.Namestr+"OUT\n "
            self.inpString += str(int(beam.MaxNodeID))+",\n"
            # Surface creation
            self.inpString += "*Surface, type=NODE, name ="+beam.Namestr+"_OUT_CNS, internal\ns_"+beam.Namestr+"_OUT_PBC, 1\n"

            temp+=1
            print("\rSet creation for PBCs: "+str(int(temp/(len(BeamList))*1000)/10)+"%",end="\r")

        print("------------------------------------------------------------------\n---------------------------Sets created---------------------------")
        #Coupling
        if Config[1] != None:
            count = 1
            temp=0
            for beam in BeamList:
                for node in beam.NodeList:
                    self.inpString += "** Constraint"+str(count)+"\n"
                    self.inpString += "*Coupling, constraint name=Constraint-"+str(count)+", ref node=m_"+beam.Namestr+"_"+str(int(node.ID))+", surface="+beam.Namestr+"_"+str(int(node.ID))+"_CNS\n"
                    self.inpString += "*Kinematic\n"
                    count+=1
                    temp+=1
                    if PyVersion >= 3:
                        print("\rCoupling creation for embeded beams: "+str(int(temp/(len(BeamList)*len(beam.NodeList))*1000)/10)+"%",end="\r")
                    else:
                        print("\rCoupling creation for embeded beams: "+str(int(temp/(len(BeamList)*len(beam.NodeList))*1000)/10)+"%")

        count = 1
        temp = 0
        for beam in BeamList:
            for DL in range(6):
                # Outside Beams
                if DL == 2:
                    self.inpString += "** Constraint: PBC_OUT_"+beam.Namestr+"_"+str(DL+1)+"\n"
                    self.inpString += "*Equation\n3\nM_"+beam.Namestr+"_OUT_PBC,"+str(DL+1)+",-1.\nS_"+beam.Namestr+"_OUT_PBC,"+str(DL+1)+",1.\nDUMMYSET,"+str(DL+1)+",1\n"

                    #Inside Beams
                    if Config[1] != None:
                        self.inpString += "** Constraint: PBC_IN_"+beam.Namestr+"_"+str(DL+1)+"\n"
                        self.inpString += "*Equation\n3\nM_"+beam.Namestr+"_IN_PBC,"+str(DL+1)+",-1.\nS_"+beam.Namestr+"_IN_PBC,"+str(DL+1)+",1.\nDUMMYSET,"+str(DL+1)+",1\n"

                elif DL == 1:
                    self.inpString += "** Constraint: PBC_OUT_"+beam.Namestr+"_"+str(DL+1)+"\n"
                    self.inpString += "*Equation\n2\nM_"+beam.Namestr+"_OUT_PBC,"+str(DL+1)+",-1.\nS_"+beam.Namestr+"_OUT_PBC,"+str(DL+1)+",1.\n"

                    #Inside Beams
                    if Config[1] != None:
                        self.inpString += "** Constraint: PBC_IN_"+beam.Namestr+"_"+str(DL+1)+"\n"
                        self.inpString += "*Equation\n2\nM_"+beam.Namestr+"_IN_PBC,"+str(DL+1)+",-1.\nS_"+beam.Namestr+"_IN_PBC,"+str(DL+1)+",1.\n"

                else:
                    self.inpString += "** Constraint: PBC_OUT_"+beam.Namestr+"_"+str(DL+1)+"\n"
                    self.inpString += "*Equation\n2\nM_"+beam.Namestr+"_OUT_PBC,"+str(DL+1)+",-1.\nS_"+beam.Namestr+"_OUT_PBC,"+str(DL+1)+",1.\n"

                    #Inside Beams
                    if Config[1] != None:
                        self.inpString += "** Constraint: PBC_IN_"+beam.Namestr+"_"+str(DL+1)+"\n"
                        self.inpString += "*Equation\n2\nM_"+beam.Namestr+"_IN_PBC,"+str(DL+1)+",-1.\nS_"+beam.Namestr+"_IN_PBC,"+str(DL+1)+",1.\n"


            count+=1
            temp+=1
            if PyVersion >= 3:
                print("\rCoupling creation for PBCs: "+str(int(temp/(len(BeamList))*1000)/10)+"%",end="\r")
            else:
                print("\rCoupling creation for PBCs: "+str(int(temp/(len(BeamList))*1000)/10)+"%")


        print("------------------------------------------------------------------\n------------------------------Coupling done-----------------------")

        self.inpString += "*Element, type=MASS, elset=DUMMYSET\n1, 1\n*Mass, elset=DUMMYSET\n1e-05,\n"
        self.inpString += "*End Assembly\n"

        #Materials
        self.inpString +="**\n"
        self.inpString +="** MATERIALS\n"
        self.inpString +="**\n"
        self.inpString +="*Material, name=FiberMat\n"
        self.inpString +="*Density\n"
        self.inpString +=" 3.21,\n"
        self.inpString +="*Elastic\n"
        self.inpString +="420000., 0.3\n"
        self.inpString +="** \n"

        #Set definitions
        for beam in BeamList:
            # First End, to apply BCs
            self.inpString +="*Nset, nset=BCSet, instance="+str(beam.Namestr)+beam.Position+"\n"
            self.inpString +=str(int(beam.NodeList[0].ID))+"\n"

            # Second End, to apply Forces
            self.inpString +="*Nset, nset=ForceSet, instance="+str(beam.Namestr)+beam.Position+"\n"
            self.inpString +=str(int(beam.NodeList[-1].ID))+"\n"

    def CreateBCString(self,Value,FrictionCoef,Type="Force"):

        self.inpString += "*Amplitude, name=Amp-1, definition=SMOOTH STEP\n             0.,              0.,              1.,              1.\n**\n"
        self.inpString += "** INTERACTION PROPERTIES\n**\n*Surface Interaction, name=IntProp-1\n*Friction\n "+str(FrictionCoef)+",\n** ----------------------------------------------------------------\n**\n"
        self.inpString += "*Step, name=Step-1, nlgeom=YES\n*Dynamic, Explicit\n, 1.\n*Bulk Viscosity\n0.06, 1.2\n**\n"
        self.inpString += "** BOUNDARY CONDITIONS\n**\n** Name: BC-1 Type: Displacement/Rotation\n*Boundary, amplitude=Amp-1\n"
        self.inpString += "DUMMYSET, 1, 1\n"
        self.inpString += "DUMMYSET, 2, 2\n"
        self.inpString += "DUMMYSET, 4, 4\n"
        self.inpString += "DUMMYSET, 5, 5\n"
        self.inpString += "DUMMYSET, 6, 6\n**\n"
        if Type == "Displacement":
            self.inpString += "**\n** Name: BC-Imposed Type: Displacement/Rotation\n*Boundary, amplitude=Amp-1\n"
            self.inpString += "DUMMYSET, 3, 3, "+str(Value)+"\n**\n"

        elif Type == "Force":
            self.inpString += "** LOADS\n"
            self.inpString += "**\n"
            self.inpString += "** Name: Load-1   Type: Concentrated force\n"
            self.inpString += "*Cload, amplitude=AMP-1\n"
            self.inpString += "DUMMYSET, 3, "+str(Value)+"\n**\n"

        self.inpString += "** INTERACTIONS\n**\n** Interaction: general_contact\n*Contact, op=NEW\n*Contact Inclusions, ALL EXTERIOR\n"
        self.inpString += "*Contact Property Assignment\n ,  , INTPROP-1\n** \n"

        return 0
