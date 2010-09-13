# -*- coding:utf-8 -*-
#-----------------------------------------------------------------------------
# Name:        setup.py
# Project:	Model-Builder-Qt
# Purpose:     
#
# Author:      Flávio Codeço Coelho<fccoelho@gmail.com>
#
# Created:     2010-04-12
# Copyright:   (c) 2010 by the Author
# Licence:     GPL
#-----------------------------------------------------------------------------
__docformat__ = "restructuredtext en"
#from setuptools import setup, find_packages
from setuptools import find_packages
from cx_Freeze import setup, Executable
from model_builder.__version__ import version
import sys

if sys.platform == 'win32':
    print "==> Building for Windows..."
    exe = Executable(
        script="model_builder/PyMB.py",
        base="Win32GUI",
        icon='model_builder/MB.ico'
        )
elif sys.platform == 'linux2':
    print "==> Building for Linux..."
    exe = Executable(script="model_builder/PyMB.py",icon='model_builder/MB.ico')

buildOptions = dict(
    compressed = True,
    includes = ["wxFrame1"],
    path = sys.path + ["model_builder"])

setup(name='Model-Builder', 
        version  = version, 
        author = 'Flavio Codeco Coelho', 
        author_email = 'fccoelho@gmail.com', 
        url = 'http://model-builder.sourceforge.net',
        description = 'Graphical ODE Simulator',
        zip_safe = True,
        packages = find_packages(),
        options = dict(build_exe = buildOptions),
        executables = [exe], 
        install_requires = ["numpy >= 1.4", "scipy >= 0.7", "matplotlib >=1.0"], 
        test_suite = 'nose.collector', 
        license = 'GPL',  
      )
