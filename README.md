# inPy

[![Documentation Status](https://readthedocs.org/projects/inpy/badge/?version=latest)](https://inpy.readthedocs.io/en/latest/?badge=latest) [![DOI](https://zenodo.org/badge/171340690.svg)](https://zenodo.org/badge/latestdoi/171340690)

You can find the documentation by clicking on the documentation badge just above or following this link: --> [inPy Documentation](https://inpy.readthedocs.io/en/latest/?badge=latest)

**if you use inPy in one of your projects, please cite the code using the DOI as specified above, thanks !**

inPy is a python library that was developped by Boris Burgarella during his post-doc
under the supervision of Prof. Louis Laberge Lebel at the LabSFCA, Polytechnique Montréal.

The goal of the library is to simplify the interaction between python and abaqus,
its first goal is to be able to generate complex braids and tissue path in python and
then easily export these path as beams in abaqus

it can work both on python 3.0+ and python 2.6 and 2.7 (mostly imposed by the abaqus 6.14
version of python). Two options are available for the users:

Scripting mode -> directly generate in abaqus, might be long and very limitated in terms of libraries
(to use scripting mode, you need to copy the inPy folder in $SIMULIA\Abaqus614\6.14-1\tools\SMApy\python2.7\Lib,
it should also work with $SIMULIA\Abaqus614\6.14-1\tools\SMApy\python2.6\Lib)

Native python mode -> Generate your geometry and then creates a .inp file that can be used by abaqus

The scripting mode can also be used to access to the odb, get results and export these results to different files

Dependencies:
- python 2.6+
- numpy
- abaqus 6.0+
- matplotlib (or Mayavi)

