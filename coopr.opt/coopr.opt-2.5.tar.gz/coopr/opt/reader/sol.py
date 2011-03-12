#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

#
# Class for reading an AMPL *.sol file
#

import os
import sys
import re

from coopr.opt.base import results
from coopr.opt.base.formats import *
from coopr.opt import SolverResults
from pyutilib.component.core import alias
import pyutilib.misc

class ResultsReader_sol(results.AbstractResultsReader):
    """
    Class that reads in a *.sol results file and generates a 
    SolverResults object.
    """

    alias(str(ResultsFormat.sol))

    def __init__(self, name=None):
        results.AbstractResultsReader.__init__(self,ResultsFormat.sol)
        if not name is None:
            self.name = name

    def __call__(self, filename, res=None, soln=None):
        """
        Parse a *.sol file
        """
        if res is None:
            res = SolverResults()  
        #
        IN = open(filename,"r")
        msg = ""
        line = IN.readline()
        while line:
            if line[0] == '\n' or (line[0] == '\r' and line[1] == '\n'):
                break
            msg += line
            line = IN.readline()
        z = []
        line = IN.readline()
        if line[:7] == "Options":
            line = IN.readline()
            nopts = int(line)
            need_vbtol = False
            if nopts > 4:           # WEH - when is this true?
                nopts -= 2
                need_vbtol = True
            for i in xrange(nopts + 4):
                line = IN.readline()
                z += [int(line)]
            if need_vbtol:          # WEH - when is this true?
                line = IN.readline()
                z += [float(line)]
        else:
            raise ValueError,"Error reading \"" + filename + "\": no Options line found."
        n = z[nopts + 3] # variables
        m = z[nopts + 1] # constraints
        x = []
        y = []
        for i in xrange(m):
            line = IN.readline()
            y += [float(line)]
        for i in xrange(n):
            line = IN.readline()
            x += [float(line)]
        objno = [0,0]
        line = IN.readline()
        if line:                    # WEH - when is this true?
            if line[:5] != "objno":         #pragma:nocover
                raise ValueError, "Error reading \"" + filename + "\": expected \"objno\", found", line
            t = line.split()
            if len(t) != 3:
                raise ValueError, "Error reading \"" + filename + "\": expected two numbers in objno line, but found", line
            objno = [int(t[1]), int(t[2])]
        IN.close()
        res.solver.message = msg.strip()
        res.solver.message = res.solver.message.replace("\n","; ")
        res.solver.message = pyutilib.misc.yaml_fix(res.solver.message)
        ##res.solver.instanceName = osrl.header.instanceName
        ##res.solver.systime = osrl.header.time
        res.solver.id = objno[1]
        ##res.problem.name = osrl.header.instanceName
        if soln is None:
            soln = res.solution.add()
        ##soln.status = Solution.SolutionStatus(soln.status_type)
        ##soln.status_description = soln.status_description
        soln.message = msg.strip()
        soln.message = res.solver.message.replace("\n","; ")        
        for i in range(0,len(x)):
            #soln.variable.add("_svar["+str(i)+"]", x[i])
            soln.variable["v"+str(i)].value = x[i]
        for i in range(0,len(y)):
            #soln.dual.add("_scon["+str(i)+"]", y[i])
            soln.constraint["c"+str(i)].dual = y[i]
        #
        # This is a bit of a hack to accommodate PICO.  If 
        # the PICO parser has parsed the # of constraints, then
        # don't try to read it in from the *.sol file.  The reason
        # is that these may be inconsistent values!
        #
        #print "HERE", res.problem.number_of_constraints, type(res.problem.number_of_constraints)
        if res.problem.number_of_constraints == 0:
            res.problem.number_of_constraints = m
        res.problem.number_of_variables = n
        res.problem.number_of_objectives = 1
        return res

