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

class BeamMesh():

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

    def __init__(self,BeamMesh,BundleR,FilR):
        self.source = copy.deepcopy(BeamMesh)
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
            self.IN = BeamMesh(self.source.Namestr+"IN","B31",self.FilR,Config[1],"IN",NodeList=NewNodeList,ElemList=[],Elem0 = self.source.MaxElemID+1)
            return self.OUT.InpPart()+self.IN.InpPart()
        if Config[1]=="Truss":
            self.IN = BeamMesh(self.source.Namestr+"IN","T3D2",self.FilR,Config[1],"IN",NodeList=NewNodeList,ElemList=[],Elem0 = self.source.MaxElemID+1)
            return self.OUT.InpPart()+self.IN.InpPart()
        if Config[1]==None:
            return self.OUT.InpPart()
