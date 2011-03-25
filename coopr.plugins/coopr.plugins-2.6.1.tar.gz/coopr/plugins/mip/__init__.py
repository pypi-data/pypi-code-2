#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

import pyutilib.component.core
pyutilib.component.core.PluginGlobals.push_env( 'coopr.opt' )

from PICO import PICO, MockPICO
from CBCplugin import CBC, MockCBC
from GLPK import GLPK, MockGLPK
from glpk_file import GLPKLP
from glpk_direct import GLPKDirect
from CPLEX import CPLEX, MockCPLEX
from CPLEXDirect import CPLEXDirect
from GUROBI import GUROBI
from gurobi_direct import gurobi_direct
from ASL import ASL, MockASL
from ossolver import OSSolver
#from NLWRITE import NLWRITE

#
# Interrogate the CBC executable to see if it recognizes the -AMPL flag
#
import CBCplugin
CBCplugin.configure()

pyutilib.component.core.PluginGlobals.pop_env()

