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

######################
#		Main		 #
######################

Model = iP.Model()

if __name__ == "__main__":

    # Variable the defines the pitch of the braid
    # Pitch = 0 means that the fibers will form a 90°
    # angle with the axis of the braid
    Pitch = 2*iP.PI

    # Number of strands in the braid
    Nby = 15

    # internal radius of the braid
    Dbyin = 0.5

    # Number of layers in each strand
    # Calculating following one diameter
    R = 3

    # Thickness of the braid (duh)
    BraidThickness = 0.1

    # Sampling of the filaments
    PlaitSegments = 15

    # Create a braid with the chosen parameters
    Model.InstanceList.append(iP.Braid(Pitch,Nby,Dbyin,BraidThickness,PlaitSegments,R))

    # Calculate the middle point of the braid to center the bar
    MiddlePointz = float((np.max(np.array(Model.InstanceList[-1].CCWpath[0].Lz))-np.min(np.array(Model.InstanceList[-1].CCWpath[0].Lz)))/2)
    CenterPoint_Braid = [0,0,MiddlePointz]

    # Define the Rotary intertia matrix
    RotInertiaMatrix = np.array([[1,0,0],[0,1,0],[0,0,0]])

    # Generate a bar, named "MiddleBar"
    # of density 1, with a 0.1x0.1mm square section and 10mm long
    Model.InstanceList.append(iP.SquareSectionBar("MiddleBar",1,(0.1,0.1,10),RotInertiaMatrix,CenterPoint = CenterPoint_Braid,RotVect = [0,0,0]))

    Model.Preview()
    File = open("Braid_Example.inp","w")
    File.write(Model.GenerateINP())
    File.close()
