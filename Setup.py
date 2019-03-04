#!/usr/bin/env python

from distutils.core import setup

setup(name='inPy',
      version='0.3',
      description='Textile generation using python for abaqus',
      author='Boris Burgarella',
      author_email='boris.burgarella@polymtl.ca',
      url='https://github.com/BBurgarella/inPy',
      packages=['inPy', 'inPy.Functions','inPy.Backend','inPy.Classes','inPy.AbaqusScripting'],
     )
