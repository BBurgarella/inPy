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


######################
#		Main		 #
######################

if __name__ == "__main__":

    # Variable the defines the pitch of the braid
    # Pitch = 0 means that the fibers will form a 90°
    # angle with the axis of the braid
    Pitch = 2*iP.PI

    # Number of strands in the braid
    Nby = 10

    # internal radius of the braid
    Dbyin = 0.5

    # Number of layers in the strand
    # Calculating following one diameter
    R = 7

    # Thickness of the braid (duh)
    BraidThickness = 0.1

    # Sampling of the filaments
    PlaitSegments = 15

    Test1 = iP.Braid(Pitch,Nby,Dbyin,BraidThickness,PlaitSegments,R)
    Test1.Draw()
