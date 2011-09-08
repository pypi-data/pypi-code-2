# -*- coding: utf-8 -*-
'''run on win: py2exe_setup py2exe'''
from distutils.core import setup
import py2exe

setup(
    windows=[{"script":"zenpad.py"}], 
    options={"py2exe": {"includes":["sip"]}}
)