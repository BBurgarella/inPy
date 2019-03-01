# -*- coding: utf-8 -*-
from __future__ import print_function
try:
    import numpy as np
    import copy
    import sys
    from math import *

except:
    print("Unable to import some modules\nfunctions and classes might not work properly")


class Instance:

    def __init__(self,ElementType=None,FirstNode = 1):
        """
        This class will be used as master class for all the instances in abaqus. This include
        - All the wired structures,
        - all the rigid bodies etcself.

        """


        self.ElementType = None
        self.FirstNode = FirstNode
        self.CurrentNode = FirstNode

    def Get_NodeID(self):
        """
        A simple method to get the current node number and automatically increment to the next number

        """

        self.CurrentNode += 1
        return self.CurrentNode -1


class Model:

    def __init__(self,InstanceList=[],FirstNode=1):
        """

        Gather a series of instances as a model to simplify the generation of the inp file
        self.InstanceList is a simple list of the different instances

        """


        self.InstanceList = InstanceList
        self.INPString = ""
        self.CurrentNode = FirstNode


    def GenerateINP(self):

        """
        Takes all the instances in the InstanceList and
        call their respective Generate_PartINP_String keeping track of the node numbers

        Then all all their respective Generate_AssemblyINP_String

        """

        # First, initialise the inp for the part section
        self.INPString += "**\n** PARTS\n"
        CurrentNode = 1
        for Instance in self.InstanceList:
            Instance.FirstNode = self.CurrentNode
            self.INPString += Instance.Generate_PartINP_String()
            self.CurrentNode = Instance.CurrentNode

        print("------------------------------------------------------------------\
             \n--------------------------Parts Generated-------------------------")

        self.INPString += "**\n**\n** ASSEMBLY\n**\n*Assembly, name=Assembly\n"
        for Instance in self.InstanceList:
            Instance.CurrentNode = self.CurrentNode
            self.INPString += Instance.Generate_AssemblyINP_String()
            self.CurrentNode = Instance.CurrentNode

        print("------------------------------------------------------------------\
             \n------------------Assembly Instructions Generated-----------------")

        for Instance in self.InstanceList:
            if "Generate_CouplingINP_String" in dir(Instance):
                Instance.CurrentNode = self.CurrentNode
                self.INPString += Instance.Generate_CouplingINP_String()
                self.CurrentNode = Instance.CurrentNode

                print("------------------------------------------------------------------\
                     \n------------------Coupling Instructions Generated-----------------")

        for Instance in self.InstanceList:
            if "Create_BCINP_String" in dir(Instance):
                Instance.CurrentNode = self.CurrentNode
                self.INPString += Instance.Create_BCINP_String(-10,0.16)
                self.CurrentNode = Instance.CurrentNode

                print("------------------------------------------------------------------\
                     \n---------------------BC Instructions Generated--------------------")

        return self.INPString

    def Preview(self):
        Fig = self.InstanceList[0].Draw(standalone = False)
        for o in range(len(self.InstanceList)-2):
            Fig = self.InstanceList[o+1].Draw(standalone = False,fig=Fig)
        self.InstanceList[-1].Draw(fig =Fig)
