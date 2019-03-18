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

"""
To try this example code, you need an odb file. You can then set the
``odbname`` variable and ``odbPath``
the odb name should be entered without the extension

"""

######################
#		Main		 #
######################
# Set this to your own odb file name
odbname = "Braid_Coords"

# Set this to the path to your odb file
odbPath = "C:/Temp/"+odbname+".odb"

# Now this is a wrapped call to the
# abaqus API openOdb function
odb = iP.openOdb(odbPath)

# if you reach this, it means that your odb file
# exists in the specified location
# Yay much !
print("Odb sccessfully loaded")

# Simple call the the iP.toFileFunction
# Change the third field with a field Output
# that you required in the abaqus calutation
# if you used the defaults, "S" should work
iP.toFile(odb,"Step-1","COORD", "Test.txt")
