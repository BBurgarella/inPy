<<<<<<< HEAD:AbaqusScripting/inPy_Abq_Classes.py
from __init__ import *


class ASnode(node):

    """
    This class is the inPy.AbaqusScripting equivalent of the
    node class in inPy. All the attributes are similar
    and the methods are herited from the inPy.node class

    A new method is introduced to generate a node directly in abaqus

    """

    def __init__(self,X,Y,Z,ID):
        super.__init__(X,Y,Z,ID)


    def Generate(self):
        None
        #TBD


class ASBeamMesh(BeamMesh):

    """
    This class is the inPy.AbaqusScripting equivalent of the
    BeamMesh class in inPy. All the attributes are similar
    and the methods are herited from the inPy.node class

    A new method is introduced to generate a beam directly in abaqus

    """

    def __init__(self,Namestr,ElemType,Radius,TypeStr,PosStr,NodeList=[],ElemList=[],Node0 = 1,Elem0 = 1):
        super.__init__(Namestr,ElemType,Radius,TypeStr,PosStr,NodeList=[],ElemList=[],Node0 = 1,Elem0 = 1)



    def Generate(self):
        fiberModel = mdb.models['Model-1'].Part(name=self.Namestr, dimensionality=THREE_D, type=DEFORMABLE_BODY)
        for node in range(len(self.NodeList)):
            dtmCCCW = fiberModel.DatumPointByCoordinate(coords=[node.X,node.Y,node.Z])
            d = fiberModel.datums
        fiberModel.WirePolyLine(mergeType=IMPRINT, meshable=ON, points=d.values())
=======
from __init__ import *


class ASnode(node):

    """
    This class is the inPy.AbaqusScripting equivalent of the
    node class in inPy. All the attributes are similar
    and the methods are herited from the inPy.node class

    A new method is introduced to generate a node directly in abaqus

    """

    def __init__(self,X,Y,Z,ID):
        super.__init__(X,Y,Z,ID)


    def Generate(self):
        None
        #TBD


class ASBeamMesh(BeamMesh):

    """
    This class is the inPy.AbaqusScripting equivalent of the
    BeamMesh class in inPy. All the attributes are similar
    and the methods are herited from the inPy.node class

    A new method is introduced to generate a beam directly in abaqus

    """

    def __init__(self,Namestr,ElemType,Radius,TypeStr,PosStr,NodeList=[],ElemList=[],Node0 = 1,Elem0 = 1):
        super.__init__(Namestr,ElemType,Radius,TypeStr,PosStr,NodeList=[],ElemList=[],Node0 = 1,Elem0 = 1)



    def Generate(self):
        fiberModel = mdb.models['Model-1'].Part(name=self.Namestr, dimensionality=THREE_D, type=DEFORMABLE_BODY)
        for node in range(len(self.NodeList)):
            dtmCCCW = fiberModel.DatumPointByCoordinate(coords=[node.X,node.Y,node.Z])
            d = fiberModel.datums
        fiberModel.WirePolyLine(mergeType=IMPRINT, meshable=ON, points=d.values())
>>>>>>> b40c07d8ccef4f6a82e1e7fd4d1c83a0dbf6863e:inPy/AbaqusScripting/inPy_Abq_Classes.py
