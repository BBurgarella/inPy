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

if __name__=="__main__":
    File = open("Bar.inp","w")
    ValidModel = iP.Model()

    Vector1 = [0,1,0]
    Vector2 = [0,0,1]

    RotInertiaMatrix = np.array([[1,0,0],[0,1,0],[0,0,0]])
    Center = [2,2,2]
    Rotation  =  [iP.PI/4,0,0]
    Name = "Square Section Bar"
    Density = 1
    ShapeTuple = (1,1,10) # (L1,L2, Lengh)

    ValidModel.InstanceList.append(iP.SquareSectionBar(Name,Density,ShapeTuple,RotInertiaMatrix,CenterPoint = Center,RotVect = Rotation))

    Center = [1,0,0]
    Rotation  =  [iP.PI/4,iP.PI/4,iP.PI/4]
    Name = "Pulley"
    Density = 1
    PulleyShape = "Cyl"
    ShapeTuple = (0.5,10)
    ValidModel.InstanceList.append(iP.Pulley(Name,Density,PulleyShape,ShapeTuple,RotInertiaMatrix,CenterPoint=Center,RotVect = Rotation))


    # Variable the defines the pitch of the braid
    # Pitch = 0 means that the fibers will form a 90°
    # angle with the axis of the braid
    Pitch = 2*iP.PI

    # Number of strands in the braid
    Nby = 10

    # internal radius of the braid
    Dbyin = 0.5

    # Number of layers in each strand
    # Calculating following one diameter
    R = 3

    # Thickness of the braid (duh)
    BraidThickness = 0.1

    # Sampling of the filaments
    PlaitSegments = 15

    ValidModel.InstanceList.append(iP.Braid(Pitch,Nby,Dbyin,BraidThickness,PlaitSegments,R))

    File.write(ValidModel.GenerateINP())
    File.close()

    ValidModel.Preview()
