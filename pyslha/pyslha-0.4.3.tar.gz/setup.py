#! /usr/bin/env python

#from distutils.core import setup
from distribute_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

## Setup definition
import pyslha
__doc__ = pyslha.__doc__

setup(name = 'pyslha',
      version = pyslha.__version__,
      py_modules = ["pyslha"],
      scripts = ["slhaplot", "slha2isawig", "isawig2slha"],
      author = 'Andy Buckley',
      author_email = 'andy@insectnation.org',
      #url = 'http://projects.hepforge.org/pyslha/',
      description = 'Parsing, manipulating, and visualising SUSY Les Houches Accord data',
      long_description = __doc__,
      keywords = 'supersymmetry susy slha simulation mass decay hep physics particle',
      license = 'GPL',
      )
