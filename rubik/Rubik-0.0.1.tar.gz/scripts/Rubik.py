#!/usr/bin/env python
""" The Rubik's Cube game.
"""

import os,sys
if os.path.exists('../Rubik'):
    sys.path.insert(0, '..')
import Rubik
from Rubik import *
#from visual import *

if __name__=='__main__':
    #print 'main'
    #box()
    #print 'box'
    rc=Rubik.Controller.RubikCube.RubikCube()
    #print 'init'
    rc.run()
    #print 'run'
    
