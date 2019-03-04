# -*- coding: utf-8 -*-

from __init__ import *

#########################################
## 			Frame Generator            ##
#########################################

def FrameGen(step, odb):
    """

    RAM, RAM never changes, The end of the program occurred pretty much as we had predicted.
    Too many steps, too many nodes, not enough space or resources to go around.
    The details are trivial and pointless, the reasons, as always, purely computational ones.

    """
    # Just to inform the reader
    print("There are {} frames to read".format(len(odb.steps[step].frames)))
    for i in odb.steps[step].frames:
        yield i

############################
##        Functions       ##
############################

def toFile(odb,stepName,FieldName, Filename,InitFrame=True):

    for frame in FrameGen(stepName, odb):
        FieldValues = frame.fieldOutputs[FieldName].values
        PrintArray = []
        Curseur = 0
        count = 0

        if InitFrame == True:
            for Element in FieldValues:
                print("{}/{}".format(count,1*len(FieldValues)))
                Dict = {"InstanceName": str(Element.instance.name), "NodeLabel": Element.elementLabel, "X":Element.data[0], "Y":Element.data[1], "Z":Element.data[2]}
                PrintArray.append(Dict)
                count+=1
                InitFrame = False


    if InitFrame == True:
        file = open(Filename,"w+")
        file.write("------------------------------------------------------------------------------\n")
        file.write("| Instance_Node | Node ID |    X(t = 0)    |    Y(t = 0)    |    Z(t = 0)    |\n")
        file.write("------------------------------------------------------------------------------\n")
        for i in DictionaryList:
            file.write("{:^16}  {:^9}  {:^15} {:^15}  {:^15} \n".format(i["InstanceName"],i["NodeLabel"],i["X"],i["Y"],i["Z"]))
    file.close()



def GatherCoordinatesInTable():

    """

    The coordinates are stored in a numpy array with the structure:
    | Instance_Node | Node ID | X(t = 0) | Y(t = 0) | Z(t = 0) | ... ... ... | X(t = i) | Y(t = i) | Z(t = i) |

    """

    UValues = []

    self.XMatrix = [[Element.data[0] for Element in frame] for frame in UValues]
    self.YMatrix = [[Element.data[1] for Element in frame] for frame in UValues]
    self.ZMatrix = [[Element.data[2] for Element in frame] for frame in UValues]

    np.savetxt('X'+str(self.ID)+'.csv', self.XMatrix, delimiter=',')
    np.savetxt('Y'+str(self.ID)+'.csv', self.YMatrix, delimiter=',')
    np.savetxt('Z'+str(self.ID)+'.csv', self.ZMatrix, delimiter=',')
