# -*- coding: utf-8 -*-
from __future__ import print_function
try:
    import numpy as np
    import copy
    import sys
    from math import *

except:
    print("Unable to import some modules\nfunctions and classes might not work properly")


class Strand:
    # Local imports
    from inPy.Classes.Path import path

    def __init__(self,InitShapeFunction,PathGenerationFunction,Line,Shargs = None,Shkwargs = None,Pthargs = None,Pthkwargs = None,**kwargs):
        """
        The init shape function will be used to determine the starting points of the
        bundle (For example, in the case of a perfectly circular packing arrangemet)
        you can use the inPy circlespacking() function. This function should return a
        matrix with shape (Nx2) with N the number of filaments

        The PathGenerationFunction will be used to determine how to grow fibers from these
        seeds, and example function could be the inPy.Path.init3Dsinus() method.
        This function will be called on the matrix returned by the shape function


        Shapeargs should be a tuple of arguments to give to the shape generation funcion
        Pathargs the same but for the path generation.

        X0 gives the x coordinate of the plan that will be normal to the fibers
        the fiber axis is for now assumed to be along x

        """
        self.ShapeFunction = InitShapeFunction
        self.PathGenerationFunction = PathGenerationFunction
        self.KwargsDict = kwargs
        self.pathTable = []
        self.Shargs = Shargs
        self.Shkwargs = Shkwargs
        self.Pthargs = Pthargs
        self.Pthkwargs = Pthkwargs

    def GeneratePaths(self):
        self.SeedMatrix = self.ShapeFunction(*self.Shargs,**self.Shkwargs)
        self.pathTable = [copy.deepcopy(self.PathGenerationFunction("Sinus",*self.Pthargs,**{"OffY": Seed[0], "OffZ": Seed[1]})) for Seed in self.SeedMatrix]

    def Draw(self):
        import random
        from mayavi import mlab
        for path in self.pathTable:
            mlab.plot3d(path.Lx, path.Ly, path.Lz,line_width=self.Shargs[0],tube_sides=50,color=(random.random(),random.random(),random.random()))
        mlab.show()

    def GenerateInpString(self,Config = ["Truss","Beam"],FileName=None):
        BeamList = []
        FileString = ''
        ID = 1
        for Path in self.pathTable:
            NodeList = Path.MakeNodeList(ID0 = 100*ID)[0]
            BeamList.append(BeamMesh("Beam{}".format(ID),'B31',self.Shargs[0],"Beam","Out",NodeList=NodeList))
            FileString = FileString + BeamList[-1].InpPart()
            ID = ID + 1
        print("Beam0: {} Beam1: {}".format(BeamList[0].NodeList[0].Z,BeamList[100].NodeList[0].Z))
        if FileName != None:
            File = open(FileName,"w")
            File.write(FileString)
            File.close()
        return FileString


class Braid:
    from inPy.Functions.Geometry import circlespacking

    def __init__(self,Pitch,Nby,Dbyin,BraidThickness,PlaitSegments,R):
        # Local imports
        from inPy.inPy_Constants import PI
        from inPy.Classes.Path import path

        """ Credits to Louis for most of the code in this class
        """

        self.Pitch = Pitch
        self.R = R
        self.BundleR = BraidThickness/2
        self.FilR = self.BundleR/self.R
        self.Nby = Nby
        self.Dbyin = Dbyin
        self.BraidThickness = BraidThickness
        self.Dbyout = Dbyin+BraidThickness*2
        self.CCWpath = []
        self.CWpath = []
        self.inpString = ""
        self.PlaitSegments = PlaitSegments;

        for k in range(int(Nby/2)):
            theta = 2*PI*(k-1)/(self.Nby/2)
            self.CCWpath.append(path())
            self.CCWpath[-1].Init3DHelix(theta,"CCW",self.Pitch,self.Nby,self.Dbyin,self.Dbyout,self.PlaitSegments)

            self.CWpath.append(path())
            self.CWpath[-1].Init3DHelix(theta,"CW",self.Pitch,self.Nby,self.Dbyin,self.Dbyout,self.PlaitSegments)


    def Draw(self,SectionFunction=circlespacking,Secargs = None,standalone=True,fig = None):
        import random
        import inPy.Backend.BackendPlot as PlotBundle

        if Secargs == None:
            Secargs = (self.R,self.BundleR)

        # R = 0 should not be Used
        # but just in case
        if self.R == 0:
            Rprime = 1
        else:
            Rprime = self.R
        if Rprime == 1:
            for path in self.CCWpath:
                fig = PlotBundle.Plot_Path(path.Lx, path.Ly, path.Lz,fig,tube_radius=self.FilR)
            for path in self.CWpath:
                fig = PlotBundle.Plot_Path(path.Lx, path.Ly, path.Lz,fig,tube_radius=self.FilR)
        else:
            Coords = SectionFunction(*Secargs)
            for path in self.CCWpath:
                for Position in Coords:
                    fig = PlotBundle.Plot_Path(np.array(path.Lx)+Position[0], np.array(path.Ly)+Position[1], path.Lz,fig,tube_radius=self.FilR)
            for path in self.CWpath:
                for Position in Coords:
                    fig = PlotBundle.Plot_Path(np.array(path.Lx)+Position[0], np.array(path.Ly)+Position[1], path.Lz,fig,tube_radius=self.FilR)
        if standalone:
            PlotBundle.show()
        else:
            return fig


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
                    BeamList.append(BeamMesh(string,"T3D2",self.BundleR/Rprime,Config[0],"OUT",NodeList=NodeListCCW[k],Elem0 = 10000*k+1))
                if Config[0] == "Beam":
                    BeamList.append(BeamMesh(string,"B31",self.BundleR/Rprime,Config[0],"OUT",NodeList=NodeListCCW[k],Elem0 = 10000*k+1))
            else:
                MakeNodeListRes = self.CCWpath[k].MakeNodeList(ID0=10000*k+1,R=self.R,YarnR=self.BundleR)
                for i in range(len(MakeNodeListRes[0])):
                    NodeListCCW.append(MakeNodeListRes[0][i])
                    LastId = MakeNodeListRes[1]

                    #Mesh Generation
                    string = "BeamCCW"+str(k)+"_"+str(i)
                    if Config[0] == "Truss":
                        BeamList.append(BeamMesh(string,"T3D2",self.BundleR/Rprime,Config[0],"OUT",NodeList=NodeListCCW[i+(k*len(MakeNodeListRes[0]))],Elem0 = 10000*k+1))
                    if Config[0] == "Beam":
                        BeamList.append(BeamMesh(string,"B31",self.BundleR/Rprime,Config[0],"OUT",NodeList=NodeListCCW[i+(k*len(MakeNodeListRes[0]))],Elem0 = 10000*k+1))

        print("------------------------------------------------------------------\n------------------------CCW Beams Generated-----------------------")
        for k in range(int(self.Nby/2)):
            if self.R == 0:
                MakeNodeListRes = self.CWpath[k].MakeNodeList(ID0=10000*k+1)
                NodeListCW.append(MakeNodeListRes[0])
                LastId = MakeNodeListRes[1]

                #Mesh Generation
                string = "BeamCW"+str(k)
                if Config[0] == "Truss":
                    BeamList.append(BeamMesh(string,"T3D2",self.BundleR/Rprime,Config[0],"OUT",NodeList=NodeListCW[k],Elem0 = 10000*k+1))
                if Config[0] == "Beam":
                    BeamList.append(BeamMesh(string,"B31",self.BundleR/Rprime,Config[0],"OUT",NodeList=NodeListCW[k],Elem0 = 10000*k+1))
            else:
                MakeNodeListRes = self.CWpath[k].MakeNodeList(ID0=1000*k+1,R=self.R,YarnR=self.BundleR)
                for i in range(len(MakeNodeListRes[0])):
                    NodeListCW.append(MakeNodeListRes[0][i])
                    LastId = MakeNodeListRes[1]

                    #Mesh Generation
                    string = "BeamCW"+str(k)+"_"+str(i)
                    if Config[0] == "Truss":
                        BeamList.append(BeamMesh(string,"T3D2",self.BundleR/Rprime,Config[0],"OUT",NodeList=NodeListCW[i+(k*len(MakeNodeListRes[0]))],Elem0 = 10000*k+1))
                    if Config[0] == "Beam":
                        BeamList.append(BeamMesh(string,"B31",self.BundleR/Rprime,Config[0],"OUT",NodeList=NodeListCW[i+(k*len(MakeNodeListRes[0]))],Elem0 = 10000*k+1))

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
