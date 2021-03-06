# -*- coding: utf-8 -*-
from __future__ import print_function
try:
    import numpy as np
    import copy
    import sys
    from math import *
    from inPy.Classes.Assembly import Instance
    from inPy.inPy_Constants import PyVersion

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
        from inPy.Classes.FEM import BeamMesh

        self.BeamList = []
        FileString = ''
        ID = 1
        for Path in self.pathTable:
            NodeList = Path.MakeNodeList(ID0 = 100*ID)[0]
            self.BeamList.append(BeamMesh("Beam{}".format(ID),'B31',self.Shargs[0],"Beam","Out",NodeList=NodeList))
            FileString = FileString + self.BeamList[-1].InpPart()
            ID = ID + 1
        print("Beam0: {} Beam1: {}".format(self.BeamList[0].NodeList[0].Z,self.BeamList[100].NodeList[0].Z))
        if FileName != None:
            File = open(FileName,"w")
            File.write(FileString)
            File.close()
        return FileString


class Braid(Instance):
    """
        Class used to represent a braid, mandatory parameters are Pitch, Nby (number of strands, must always be even), Dbyin (internal radius)
        BraidThickness (Thickness of the braid), PlaitSegments (discretization of each beam) and R (number of radiuses in each strand).

        Valid optional paramters are:
        ``Config`` ---> Array used to configure the embeded beams configuration [2x1], Config[0] gives the external elements type, Config[1] give the internal element Type
        For example ``Config = ["Truss",None]`` will configure inPy to only use Truss elements, ``Config = ["Truss","Beam"]`` is the default embeded beam situation
        with external truss and internal beams, default to ["Beam",None]

        ``SparsingCoeff`` this parameter will be changed in future version, right now, it controlls the circlespacking call and defines the gap between each filaments center
        the smallest distance between each filament is defined as d = (1 + Filament_Diameter)*SparsingCoeff, default to 0

        ``Imposed_FilR`` allows the user to specify a filament radius, default to None and in this case, the filament radius is defined as BraidThickness/2*R

        ``**kwargs`` --> used to defined the Instance master-class attributes if needed

    """

    from inPy.Functions.Geometry import circlespacking

    def __init__(self,Pitch,Nby,Dbyin,BraidThickness,PlaitSegments,R,Config =  ["Beam",None],SparsingCoeff=0,Imposed_FilR=None,**kwargs):
        # Local imports
        from inPy.inPy_Constants import PI
        from inPy.Classes.Path import path

        # Initialise the Instance attributes
        super().__init__(**kwargs)

        self.Pitch = Pitch # controls the angle of the braid
        self.R = R #number of radiuses in each strand
        self.BundleR = BraidThickness/2 # Radius of each strand
        if Imposed_FilR == None:
            # If the filament radius is not imposed, the program
            # can't know the inside radius and therefore takes
            # BundleR/R as default
            self.FilRIn = self.BundleR/self.R
            self.FilROut = self.BundleR/self.R
        else:
            # Filament radius (embeded beams radius)
            self.FilRIn = Imposed_FilR
            # external filament radius
            self.FilROut = self.BundleR/self.R
        if Nby %2 != 0:
            raise ValueError('Error: braid defined with un-even Nby')
        else:
            self.Nby = Nby # number of strands, should always be even
        self.Dbyin = Dbyin # internal radius of the braid
        self.BraidThickness = BraidThickness
        self.Dbyout = Dbyin+BraidThickness*2 # external radius of the Braid
        # Init the path tables
        self.CCWpath = []
        self.CWpath = []
        # ini the inp String
        self.inpString = ""
        self.PlaitSegments = PlaitSegments
        self.Config = Config
        self.SparsingCoeff = SparsingCoeff

        for k in range(int(Nby/2)):
            # Fill the path tables with path objects
            theta = 2*PI*(k-1)/(self.Nby/2)
            self.CCWpath.append(path())
            # The Init3DHelix function of path objects
            # was developped for this purpose
            # Counter clockwise paths
            self.CCWpath[-1].Init3DHelix(theta,"CCW",self.Pitch,self.Nby,self.Dbyin,self.Dbyout,self.PlaitSegments)

            # Clockwise paths
            self.CWpath.append(path())
            self.CWpath[-1].Init3DHelix(theta,"CW",self.Pitch,self.Nby,self.Dbyin,self.Dbyout,self.PlaitSegments)


    def Draw(self,SectionFunction=circlespacking,Secargs = None,standalone=True,fig = None):

        """
        Draws the braid for preview purposes,
        depends on the plot backend chosen by the end-user

        Valid parameters:
        ``SectionFunction``  --> python function that will be call on ``**Sceargs``
        The section function should remains as default for now since the braid object is not yet compatible with
        other section shapes.

        ``Secargs`` --> tuple of arguments for the section function, if None, this will be set to
        (self.R,self.BundleR,self.SparsingCoeff)

        ``standalone`` ---> parameter that should always appear in draw functions for inPy.Instance subclasses, if True (default)
        the plot will be shown directly, if False, a figure object is returned

        ``fig`` ---> this is used if you want to add the braid to a previously existing figure object

        """
        # Local imports
        import random
        import inPy.Backend.BackendPlot as PlotBundle

        # if the user did not specify Secargs, set to
        # (self.R,self.BundleR,self.SparsingCoeff)
        if Secargs == None:
            Secargs = (self.R,self.BundleR,self.SparsingCoeff)

        # R = 0 should not be Used
        # but just in case
        if self.R == 0:
            Rprime = 1
        else:
            Rprime = self.R

        # if Rprime == 1
        # this means only one filament in the strands
        if Rprime == 1:
            for path in self.CCWpath:
                fig = PlotBundle.Plot_Path(path.Lx, path.Ly, path.Lz,fig,tube_radius=self.FilR)
            for path in self.CWpath:
                fig = PlotBundle.Plot_Path(path.Lx, path.Ly, path.Lz,fig,tube_radius=self.FilR)
        else:
            # multiple filaments
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

    def Generate_PartINP_String(self,R=0,AddDummy = True):
        from inPy.Classes.FEM import BeamMesh, EmbededBeam
        from inPy.Functions.FEM import CreateDummyString
        NodeListCCW = []
        NodeListCW = []
        self.BeamList = []
        if R == 0:
            Rprime = 1
        else:
            Rprime = R
        for k in range(int(self.Nby/2)):
            #Node Generation CCW
            if self.R == 0:
                MakeNodeListRes = self.CCWpath[k].MakeNodeList(ID0=self.CurrentNode)
                NodeListCCW.append(MakeNodeListRes[0])
                self.CurrentNode = MakeNodeListRes[1]

                #Mesh Generation CCW
                string = "BeamCCW"+str(k)
                if self.Config[0] == "Truss":
                    self.BeamList.append(BeamMesh(string,"T3D2",self.FilROut,self.Config[0],"OUT",NodeList=NodeListCCW[k],Elem0 = 10000*k+1))
                if self.Config[0] == "Beam":
                    self.BeamList.append(BeamMesh(string,"B31",self.FilROut,self.Config[0],"OUT",NodeList=NodeListCCW[k],Elem0 = 10000*k+1))
            else:
                MakeNodeListRes = self.CCWpath[k].MakeNodeList(ID0=self.CurrentNode,R=self.R,YarnR=self.BundleR,SparsingCoeff=self.SparsingCoeff)
                for i in range(len(MakeNodeListRes[0])):
                    NodeListCCW.append(MakeNodeListRes[0][i])
                    self.CurrentNode = MakeNodeListRes[1]

                    #Mesh Generation CCW
                    string = "BeamCCW"+str(k)+"_"+str(i)
                    if self.Config[0] == "Truss":
                        self.BeamList.append(BeamMesh(string,"T3D2",self.FilROut,self.Config[0],"OUT",NodeList=NodeListCCW[i+(k*len(MakeNodeListRes[0]))],Elem0 = 10000*k+1))
                    if self.Config[0] == "Beam":
                        self.BeamList.append(BeamMesh(string,"B31",self.FilROut,self.Config[0],"OUT",NodeList=NodeListCCW[i+(k*len(MakeNodeListRes[0]))],Elem0 = 10000*k+1))
        print("------------------------------------------------------------------\n------------------------CCW Beams Generated------------------------")
        for k in range(int(self.Nby/2)):
            #Node Generation CW
            if self.R == 0:
                MakeNodeListRes = self.CWpath[k].MakeNodeList(ID0=self.CurrentNode)
                NodeListCW.append(MakeNodeListRes[0])
                self.CurrentNode = MakeNodeListRes[1]

            #Mesh Generation CW
                string = "BeamCW"+str(k)
                if self.Config[0] == "Truss":
                    self.BeamList.append(BeamMesh(string,"T3D2",self.FilROut,self.Config[0],"OUT",NodeList=NodeListCW[k],Elem0 = 10000*k+1))
                if self.Config[0] == "Beam":
                    self.BeamList.append(BeamMesh(string,"B31",self.FilROut,self.Config[0],"OUT",NodeList=NodeListCW[k],Elem0 = 10000*k+1))
            else:
                MakeNodeListRes = self.CWpath[k].MakeNodeList(ID0=self.CurrentNode,R=self.R,YarnR=self.BundleR,SparsingCoeff=self.SparsingCoeff)
                for i in range(len(MakeNodeListRes[0])):
                    NodeListCW.append(MakeNodeListRes[0][i])
                    self.CurrentNode = MakeNodeListRes[1]

                    #Mesh Generation
                    string = "BeamCW"+str(k)+"_"+str(i)
                    if self.Config[0] == "Truss":
                        self.BeamList.append(BeamMesh(string,"T3D2",self.FilROut,self.Config[0],"OUT",NodeList=NodeListCW[i+(k*len(MakeNodeListRes[0]))],Elem0 = 10000*k+1))
                    if self.Config[0] == "Beam":
                        self.BeamList.append(BeamMesh(string,"B31",self.FilROut,self.Config[0],"OUT",NodeList=NodeListCW[i+(k*len(MakeNodeListRes[0]))],Elem0 = 10000*k+1))

        if AddDummy == True:
                self.inpString += CreateDummyString()
        for i in self.BeamList:
                Validation = EmbededBeam(i,self.FilROut,self.FilRIn)
                self.inpString += Validation.Generate(Config = self.Config)
        self.CurrentNode += 1
        print("------------------------------------------------------------------\n------------------------CW Beams Generated------------------------")
        return self.inpString

    def Generate_AssemblyINP_String(self,R=0,AddDummy = True):
        from inPy.inPy_Constants import PyVersion
        #Assembly
        self.inpString = ""
        if AddDummy == True:
            self.inpString += "**\n*Instance, name = DummyInstance, part  = dummy\n*End Instance\n"
            self.inpString += "*Node\n      {},           0.,           0.,           0.\n".format(self.CurrentNode)
            self.inpString += "*Nset, nset=DummySet, internal\n{},\n".format(self.CurrentNode)
            self.inpString += "*Nset, nset=DummySet\n{},\n".format(self.CurrentNode)
            self.CurrentNode += 1
        for i in self.BeamList:
            if self.Config[1] != None:
                self.inpString += "**\n"
                self.inpString += "*Instance, name="+i.Namestr+"IN,part="+i.Namestr+"IN\n"
                self.inpString += "*End Instance\n"
            self.inpString += "**\n"
            self.inpString += "*Instance, name="+i.Namestr+"OUT,part="+i.Namestr+"OUT\n"
            self.inpString += "*End Instance\n"
        return self.inpString

    def Generate_CouplingINP_String(self,R=0,AddDummy = True):
        #Set creation for Embeded beams
        self.inpString = ""
        if self.Config[1] != None:
            self.inpString += "**\n"
            temp=0
            for beam in self.BeamList:
                for node in beam.NodeList:
                    self.inpString += "*Nset, nset=m_"+beam.Namestr+"_"+str(int(node.ID))+", instance="+beam.Namestr+"IN\n "
                    self.inpString += str(int(node.ID+(len(beam.NodeList))))+",\n"
                    self.inpString += "*Nset, nset=s_"+beam.Namestr+"_"+str(int(node.ID))+", instance="+beam.Namestr+"OUT\n "
                    self.inpString += str(int(node.ID))+",\n"
                    self.inpString += "*Surface, type=NODE, name ="+beam.Namestr+"_"+str(int(node.ID))+"_CNS, internal\ns_"+beam.Namestr+"_"+str(int(node.ID))+", 1\n"
                    temp+=1
                    if PyVersion >= 3:
                        print("\rSet creation for embeded beams: "+str(int(temp/(len(self.BeamList)*len(beam.NodeList))*1000)/10)+"%",end="\r")
                    else:
                        print("\rSet creation for embeded beams: "+str(int(temp/(len(self.BeamList)*len(beam.NodeList))*1000)/10)+"%")

        #Set creation for PBCs
        self.inpString += "**\n"
        temp=0
        for beam in self.BeamList:
            #############################
            # By convention, I always take the first node as the master
            # and the last as the Slave
            #############################
            # Master node, Inside beam
            if self.Config[1] != None:
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
            print("\rSet creation for PBCs: "+str(int(temp/(len(self.BeamList))*1000)/10)+"%",end="\r")

        print("------------------------------------------------------------------\n---------------------------Sets created---------------------------")
        #Coupling
        if self.Config[1] != None:
            count = 1
            temp=0
            for beam in self.BeamList:
                for node in beam.NodeList:
                    self.inpString += "** Constraint"+str(count)+"\n"
                    self.inpString += "*Coupling, constraint name=Constraint-"+str(count)+", ref node=m_"+beam.Namestr+"_"+str(int(node.ID))+", surface="+beam.Namestr+"_"+str(int(node.ID))+"_CNS\n"
                    self.inpString += "*Kinematic\n"
                    count+=1
                    temp+=1
                    if PyVersion >= 3:
                        print("\rCoupling creation for embeded beams: "+str(int(temp/(len(self.BeamList)*len(beam.NodeList))*1000)/10)+"%",end="\r")
                    else:
                        print("\rCoupling creation for embeded beams: "+str(int(temp/(len(self.BeamList)*len(beam.NodeList))*1000)/10)+"%")

        count = 1
        temp = 0
        for beam in self.BeamList:
            for DL in range(6):
                # Outside Beams
                if DL == 2:
                    self.inpString += "** Constraint: PBC_OUT_"+beam.Namestr+"_"+str(DL+1)+"\n"
                    self.inpString += "*Equation\n3\nM_"+beam.Namestr+"_OUT_PBC,"+str(DL+1)+",-1.\nS_"+beam.Namestr+"_OUT_PBC,"+str(DL+1)+",1.\nDUMMYSET,"+str(DL+1)+",1\n"

                    #Inside Beams
                    if self.Config[1] != None:
                        self.inpString += "** Constraint: PBC_IN_"+beam.Namestr+"_"+str(DL+1)+"\n"
                        self.inpString += "*Equation\n3\nM_"+beam.Namestr+"_IN_PBC,"+str(DL+1)+",-1.\nS_"+beam.Namestr+"_IN_PBC,"+str(DL+1)+",1.\nDUMMYSET,"+str(DL+1)+",1\n"

                elif DL == 1:
                    self.inpString += "** Constraint: PBC_OUT_"+beam.Namestr+"_"+str(DL+1)+"\n"
                    self.inpString += "*Equation\n3\nM_"+beam.Namestr+"_OUT_PBC,"+str(DL+1)+",-1.\nS_"+beam.Namestr+"_OUT_PBC,"+str(DL+1)+",1.\nDUMMYSET,"+str(DL+1)+",1\n"

                    #Inside Beams
                    if self.Config[1] != None:
                        self.inpString += "** Constraint: PBC_IN_"+beam.Namestr+"_"+str(DL+1)+"\n"
                        self.inpString += "*Equation\n3\nM_"+beam.Namestr+"_IN_PBC,"+str(DL+1)+",-1.\nS_"+beam.Namestr+"_IN_PBC,"+str(DL+1)+",1.\nDUMMYSET,"+str(DL+1)+",1\n"

                else:
                    self.inpString += "** Constraint: PBC_OUT_"+beam.Namestr+"_"+str(DL+1)+"\n"
                    self.inpString += "*Equation\n3\nM_"+beam.Namestr+"_OUT_PBC,"+str(DL+1)+",-1.\nS_"+beam.Namestr+"_OUT_PBC,"+str(DL+1)+",1.\nDUMMYSET,"+str(DL+1)+",1\n"

                    #Inside Beams
                    if self.Config[1] != None:
                        self.inpString += "** Constraint: PBC_IN_"+beam.Namestr+"_"+str(DL+1)+"\n"
                        self.inpString += "*Equation\n3\nM_"+beam.Namestr+"_IN_PBC,"+str(DL+1)+",-1.\nS_"+beam.Namestr+"_IN_PBC,"+str(DL+1)+",1.\nDUMMYSET,"+str(DL+1)+",1\n"


            count+=1
            temp+=1
            if PyVersion >= 3:
                print("\rCoupling creation for PBCs: "+str(int(temp/(len(self.BeamList))*1000)/10)+"%",end="\r")
            else:
                print("\rCoupling creation for PBCs: "+str(int(temp/(len(self.BeamList))*1000)/10)+"%")



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
        for beam in self.BeamList:
            # First End, to apply BCs
            self.inpString +="*Nset, nset=BCSet, instance="+str(beam.Namestr)+beam.Position+"\n"
            self.inpString +=str(int(beam.NodeList[0].ID))+"\n"

            # Second End, to apply Forces
            self.inpString +="*Nset, nset=ForceSet, instance="+str(beam.Namestr)+beam.Position+"\n"
            self.inpString +=str(int(beam.NodeList[-1].ID))+"\n"
        return self.inpString

    def Create_BCINP_String(self,Value,FrictionCoef,Type="Force"):
        self.inpString = ""
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

        return self.inpString
