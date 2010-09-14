#! /usr/bin/env python

"""\
A parser/writer module for particle physics SUSY Les Houches Accord (SLHA)
supersymmetric spectrum/decay files, and a collection of scripts which use the
interface, e.g. for conversion to and from the legacy ISAWIG format, or to plot
the mass spectrum and decay chains.

The current release supports SLHA version 1. Assistance with supporting version
2 will be gladly accepted!
"""

#from distutils.core import setup
from distribute_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

## Setup definition
import pyslha
setup(name = 'pyslha',
      version = pyslha.__version__,
      py_modules = ["pyslha"],
      scripts = ["slhaplot", "slha2isawig", "isawig2slha"],
      author = ['Andy Buckley'],
      author_email = 'andy@insectnation.org',
      #url = 'http://projects.hepforge.org/pyslha/',
      description = 'Parsing, manipulating, and visualising SUSY Les Houches Accord data',
      long_description = __doc__,
      keywords = 'supersymmetry susy slha simulation mass decay hep physics particle',
      license = 'GPL',
      )
