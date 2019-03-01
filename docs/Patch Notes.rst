Patch Notes V0.3
================

2019 - 03 - 01
--------------

TODO
    - update the Draw methods of the Wired_Structures objects - 50%, braid is done, strand is not
    - Write an assembly class to simplify inp generation
    - Implement a Preview method for the model

  - Implemented two new classes in a new inPy.Classes.Assembly file. These classes are respectively the Model class, gathering a series of instances to simplify the generation of inp file and the Instance class that should be used as a master class for anything having a Generate_PartINP_String and Generate_AssemblyINP_String method.

  status: implemented,tested and validated

  - Created the documentation with sphinc

2019 - 02 -28
-------------

TODO
    - update the Draw methods of the Wired_Structures objects - 50%, braid is done, strand is not
    - Write an assembly class to simplify inp generation

- Made the Braid class compatible with both backends for plot3d

  Status: implemented, tested and validated

- Fixed a bug that caused the contact surface to be on the inside a generated SquareSectionBar instead of the outside

- Added a SquareSectionBar rigid body, defined by a lengh and two dimensions L1 and L2 status implemented, tested and validated

- added two new methods to the Rigid_body object:

  Generate_PartINP_String(self): Returns the part definition as it should be written in the inp file
  Generate_AssemblyINP_String(self): Returns the assembly definition as it should be written in the inp files

  These two new methods require the definition of another method, currently handled by subclasses: PolygonString()
  This method is used to generate the shape used for the part generation (for example a rectangle that will be extruded
  to make a recangular-section rigid body)

  If GenMethod is "Revolution", PolygonString should return the definition of the surface that will be revoluted
  if GenMethod is "Extrusion", PolygonString should return the definiton of the surface that will be extruded

status: implemented, tested and validated


2019 - 02 -27
-------------

- Started the implementation of a backend option, either matplotlib or Mayavi
  Mayavi is way more efficient, but relies on complex dependencies
  matplotlib is widely available but might be very slow.

  For example, Mayavi seems to crash when used on remote desktop

  two functions are now implemented for both backends:
  - Plot_surface(x,y,z,**kwargs), used to plot a surface (duh), this is used
  to preview the pulleys for example
  - show(), simple call to mlab.show() or matplotlib.pyplot.show()

  TODO:
    - implement a plot_path function for both backends
    - update the Draw methods of the Wired_Structures objects

  status: being implemented

- Added a RotVect_to_RotMat function to inPy.Functions.linalg, this function
  takes a rotation vector as entry (rad) and returns the corresponding rotation matrix

status: implemented, tested and validated
