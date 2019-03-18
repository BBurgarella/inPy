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

    Joke's aside, I needed to implement this to avoid overloading the ram on systems with
    a low amount of ram or very large projects

    """
    # Just to inform the reader
    print("There are {} frames to read".format(len(odb.steps[step].frames)))
    for i in odb.steps[step].frames:
        yield i

############################
##        Functions       ##
############################

def toFile(odb,stepName,FieldName, Filename,Ext = "txt",Separator=None,Verbose = True):

    """
    Write the chosen field output in a text file as a tableself.
    The header will specify the fieldOutput reference (for example "S" for the stress)

    [Parameters]
    ``odb`` --> odb object as defined by the abaqus API
    ``stepName`` --> String that will be used to call the step in Abaqus
    ``FieldName`` --> String that will be used to ask in the abaqus API for the fieldoutput needed
    TODO: make that if a list is given, multiple output files will be created
    ``FileName`` --> string to specify the filename

    [Optional parameters]
    ``Ext`` default to "txt", used to specify the extension of the created file
    ``Verbose`` default to True, if set to False, Remove the printed lines

    [Not yet implemented parameters]
    ``Separator`` default to None. will be used in the future to make csv files for example

    """
    FullName = FileName+"."+Ext
    file = open(FullName,"w+")

    # Frame counter
    FrameID = 0

    # The header is initialized here
    HeaderLine0 = "Case: {}, Output: {}\n".format(odb.name,FieldName)
    HeaderLine1 = "---------------------------"
    HeaderLine2 = "| Instance_Node |   ID   |"
    HeaderLine3 = "---------------------------"

    # This array is filled then called when writing the file
    PrintArray = []

    for frame in FrameGen(stepName, odb):
        # Get the field value array
        FieldValues = frame.fieldOutputs[FieldName].values

        # I need a sub array is I want to put all the results
        # for one node/element in a single line
        PrintSubArray = []
        NbFrames = len(odb.steps[stepName].frames)

        # Print if verbose
        if Verbose:
            print("{}/{}   ".format(FrameID+1,NbFrames))

        for Data in FieldValues:
            # First test: does the value
            # belong to an instance
            if Data.instance is None:
                Name = "Unknown name" # if the node / element was directly added to the assembly
            else:
                Name = Data.instance.name # Normal case

            # Second test: are we dealing with nodal results
            # or elemental results
            if Data.nodeLabel is None:
                DataLoc = Data.elementLabel # Elemental results
            else:
                DataLoc = Data.nodeLabel # Nodal results

            Dict = {"InstanceName": str(Name), "Label": DataLoc, "X":Data.data[0], "Y":Data.data[1], "Z":Data.data[2]}
            PrintSubArray.append(Dict)
        PrintArray.append(PrintSubArray)

        # Add the corresponding text to the header
        HeaderLine1 += "---------------------------------------------------------------"
        HeaderLine2 += "    X(F = {:^2})    |    Y(F = {:^2})    |    Z(F = {:^2})    |".format(FrameID,FrameID,FrameID)
        HeaderLine3 += "---------------------------------------------------------------"
        FrameID += 1

    HeaderLine1 += "\n"
    HeaderLine2 += "\n"
    HeaderLine3 += "\n"

    # Write the header in the file
    file.write(HeaderLine0)
    file.write(HeaderLine1)
    file.write(HeaderLine2)
    file.write(HeaderLine3)

    for Node in range(len(PrintArray[0])):
        # I need to separate the first frame because of the first two columns
        # (Instance name and node/element label)
        FirstFrame = PrintArray[0]

        # This command is on two lines for better readability
        file.write("{:^16}{:^9}{:^18}{:^18}{:^18}".format(\
        FirstFrame[Node]["InstanceName"],FirstFrame[Node]["Label"],FirstFrame[Node]["X"],FirstFrame[Node]["Y"],FirstFrame[Node]["Z"]))

        # Now that the first frame is written only the new directional results are needed
        for Frame in range(len(PrintArray)-1):
            file.write("{:^18}{:^18}{:^18}".format(PrintArray[Frame+1][Node]["X"],PrintArray[Frame+1][Node]["Y"],PrintArray[Frame+1][Node]["Z"]))
        file.write("\n")
    FrameID += 1

    # Never forget to close the file :P
    file.close()
