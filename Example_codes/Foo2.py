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
    CirclesDistrib = iP.circlespacking(13,0.0325,0)
    R = 0.0025
    print("{} filaments".format(len(CirclesDistrib)))
    XBd = (-np.max(CirclesDistrib)*1.2,np.max(CirclesDistrib)*1.2)
    YBd = (-np.max(CirclesDistrib)*1.2,np.max(CirclesDistrib)*1.2)
    print("Real diameter: {}".format((XBd[1]-XBd[0])))
    D1 = 10
    D2 = 10
    iP.PlotCircles(CirclesDistrib,R,XBd,YBd,D1,D2)
