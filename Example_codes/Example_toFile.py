# import sys and update the sys path
# this is here to load inPy in case
# it is not installed

try:
    import inPy as iP
except:
    print("inPy not found in python default path\nTrying the parent directory")
    import sys
    sys.path.insert(0, "../")
    sys.path.insert(0, "./")
    import inPy as iP

# Now inPy should be loaded
import numpy as np
import threading as thread

######################
#		Main		 #
######################
odbname = "Braid_Coords"
NbFilaments = 7
#odbname = "3DFullScaleRigid"
odbPath = "C:/Temp/"+odbname+".odb"
#odb = session.openOdb(name=odbPath,readOnly=FALSE)
#odb = session.odbs[odbPath]
odb = iP.openOdb(odbPath)

print("Odb sccessfully loaded")
iP.toFile(odb,"Step-1","COORD", "Test.txt",InitFrame=True)
