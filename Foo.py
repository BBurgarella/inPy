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
from mayavi import mlab

Vector1 = [0,1,0]
Vector2 = [0,0,1]

RotInertiaMatrix = np.array([[1,0,0],[0,1,0],[0,0,0]])

New_Body = iP.Pulley("Test",1,"Cyl",(1,10),RotInertiaMatrix)
fig = New_Body.Draw(standalone=False)

New_Body2 = iP.Pulley("Test",1,"Cyl",(0.5,10),RotInertiaMatrix,TransVect=[1,0,0])
fig = New_Body2.Draw(standalone=False,fig = fig,backend="Matplotlib")
mlab.show()
