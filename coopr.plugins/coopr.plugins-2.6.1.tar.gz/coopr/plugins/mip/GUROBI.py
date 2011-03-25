#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

import os
import sys
import re
from coopr.opt.base import *
from coopr.opt.results import *
from coopr.opt.solver import *
import mockmip
import pyutilib.services
import pyutilib.common
import pyutilib.misc
import pyutilib.component.core
import string
import re

import xml.dom.minidom

import time

class GUROBI(ILMLicensedSystemCallSolver):
    """The GUROBI LP/MIP solver
    """

    pyutilib.component.core.alias('gurobi',  doc='Shell interface to the GUROBI LP/MIP solver')

    def __init__(self, **kwds):
        #
        # Call base class constructor
        #
        kwds['type'] = 'gurobi'
        ILMLicensedSystemCallSolver.__init__(self, **kwds)

        # We are currently invoking GUROBI via the command line, with input re-direction.
        # Consequently, we need to define an attribute to retain the execution script name.
        self.gurobi_script_file_name = None

        # NOTE: eventually both of the following attributes should be migrated to a common base class.
        # is the current solve warm-started? a transient data member to communicate state information
        # across the _presolve, _apply_solver, and _postsolve methods.
        self.warm_start_solve = False
        # related to the above, the temporary name of the MST warm-start file (if any).
        self.warm_start_file_name = None

        #
        # Define valid problem formats and associated results formats
        #
        self._valid_problem_formats=[ProblemFormat.cpxlp, ProblemFormat.mps]
        self._valid_result_formats={}
        self._valid_result_formats[ProblemFormat.cpxlp] = [ResultsFormat.soln]
        self._valid_result_formats[ProblemFormat.mps] = [ResultsFormat.soln]

        # Note: Undefined capabilities default to 'None'
        self._capabilities = pyutilib.misc.Options()
        self._capabilities.linear = True
        self._capabilities.quadratic = True
        self._capabilities.integer = True
        self._capabilities.sos1 = True
        self._capabilities.sos2 = True

    def warm_start_capable(self):

       return True

    #
    # write a warm-start file in the GUROBI MST format, which is *not* the same as the CPLEX MST format.
    #
    def warm_start(self, instance):

       from coopr.pyomo.base import Var, VarStatus

       self.warm_start_file_name = pyutilib.services.TempfileManager.create_tempfile(suffix = '.gurobi.mst')

       mst_file = open(self.warm_start_file_name,'w')

       for variable in instance.active_components(Var).values():

          for varvalue in variable._varval.itervalues():

             if (varvalue.status != VarStatus.unused) and (varvalue.value != None) and (varvalue.fixed == False):

                name = varvalue.label
                name = name.replace('[','(')
                name = name.replace(']',')')
                print >>mst_file, name, varvalue.value

       mst_file.close()

    # over-ride presolve to extract the warm-start keyword, if specified.
    def _presolve(self, *args, **kwds):

       # if the first argument is a string (representing a filename),
       # then we don't have an instance => the solver is being applied
       # to a file.

       self.warm_start_solve = False               
       if "warmstart" in kwds:
          self.warm_start_solve = kwds["warmstart"]
          del kwds["warmstart"]

       if (len(args) > 0) and (isinstance(args[0],basestring) is False):

          # write the warm-start file - currently only supports MIPs.
          # we only know how to deal with a single problem instance.       
          if self.warm_start_solve is True:

             if len(args) != 1:
                raise ValueError, "GUROBI _presolve method can only handle a single problem instance - "+str(len(args))+" were supplied"                  

             if args[0].has_discrete_variables() is True:
                start_time = time.time()
                self.warm_start(args[0])
                end_time = time.time()
                if self._report_timing is True:
                   print "Warm start write time="+str(end_time-start_time)+" seconds"
          
       # let the base class handle any remaining keywords/actions.
       ILMLicensedSystemCallSolver._presolve(self, *args, **kwds)

    def executable(self):

        if sys.platform == 'win32':
           executable = pyutilib.services.registered_executable("gurobi.bat")
        else:
           executable = pyutilib.services.registered_executable("gurobi.sh")
        if executable is None:
            pyutilib.component.core.PluginGlobals.env().log.error("Could not locate the 'gurobi' executable, which is required for solver %s" % self.name)
            self.enable = False
            return None
        return executable.get_path()

    def create_command_line(self,executable,problem_files):

        #
        # Define log file
        # The log file in CPLEX contains the solution trace, but the solver status can be found in the solution file.
        #
        self.log_file = pyutilib.services.TempfileManager.create_tempfile(suffix = '.gurobi.log')

        #
        # Define solution file
        # As indicated above, contains (in XML) both the solution and solver status.
        #
        self.soln_file = pyutilib.services.TempfileManager.create_tempfile(suffix = '.gurobi.txt')
        self.results_file = self.soln_file

        #
        # Write the GUROBI execution script
        #

        problem_filename = self._problem_files[0]
        solution_filename = self.soln_file
        warmstart_filename = self.warm_start_file_name
        if sys.platform == 'win32':
           problem_filename  = problem_filename.replace('\\', r'\\')
           solution_filename = solution_filename.replace('\\', r'\\')
           if self.warm_start is True:
              warmstart_filename = warmstart_filename.replace('\\', r'\\')

        # translate the options into a normal python dictionary, from a 
        # pyutilib.component.config.options.SectionWrapper - the 
        # gurobi_run function doesn't know about coopr, so the translation
        # is necessary.
        options_dict = {}
        for key in self.options:
           options_dict[key] = self.options[key]

        # NOTE: the gurobi shell is independent of Coopr python virtualized environment, so any
        #       imports - specifically that required to get GUROBI_RUN - must be handled explicitly.
        # NOTE: The gurobi plugin (GUROBI.py) and GUROBI_RUN.py live in the same directory.
        script  = "import sys\n"
        script += "from gurobipy import *\n"
        script += "sys.path.append('%s')\n" % os.path.dirname(__file__)
        script += "from GUROBI_RUN import *\n"
        script += "gurobi_run%s\n" % str((problem_filename, warmstart_filename, solution_filename, self.options.mipgap, options_dict, self.suffixes))
        script += "quit()\n"

        self.gurobi_script_file_name = pyutilib.services.TempfileManager.create_tempfile(suffix = '.gurobi.script')
        gurobi_script_file = open(self.gurobi_script_file_name, 'w')
        gurobi_script_file.write( script )
        gurobi_script_file.close()

        # dump the script and warm-start file names for the
        # user if we're keeping files around.
        if self.keepFiles:
           print "Solver script file: '%s'" % self.gurobi_script_file_name
           if (self.warm_start_solve is True) and (self.warm_start_file_name is not None):
              print "Solver warm-start file: " + self.warm_start_file_name

        #
        # Define command line
        #
        proc = self._timer + " " + self.executable() + " < " + self.gurobi_script_file_name
        return pyutilib.misc.Bunch(cmd=proc, log_file=self.log_file, env=None)

    def process_logfile(self):

        return ILMLicensedSystemCallSolver.process_logfile(self)

    def process_soln_file(self,results):

        # check for existence of the solution file
        # not sure why we just return - would think that we
        # would want to indicate some sort of error
        if not os.path.exists(self.soln_file):
           return

        soln = Solution()

        soln_variables = soln.variable
        soln_constraints = soln.constraint

        section = 'unknown'

        INPUT = open(self.soln_file,"r")
        for line in INPUT:
            line = line.strip()
            line = line.lstrip()
            line = line.rstrip()
            tokens = line.split(":")
            #print "LINE", line
            for i in range(0,len(tokens)):
                tokens[i] = tokens[i].strip()

            #print tokens
            if (tokens[0] == 'section'):
                if (tokens[1] == 'problem'):
                    section = 'problem'
                elif (tokens[1] == 'solution'):
                    section = 'solution'
                elif (tokens[1] == 'solver'):
                    section = 'solver'
            else:
                if (section == 'problem'):
                    if tokens[0] == 'sense':
                        if tokens[1] == 'minimize':
                            results.problem.sense = ProblemSense.minimize
                        elif tokens[1] == 'maximize':
                            results.problem.sense = ProblemSense.maximize
                    else:
                        try:
                           val = eval(tokens[1])
                        except:
                           val = tokens[1]
                        setattr(results.problem, tokens[0], val)
                elif (section == 'solver'):
                    try:
                       val = eval(tokens[1])
                    except:
                       val = tokens[1]
                    if (tokens[0] == 'status'):
                        results.solver.status = getattr(SolverStatus, val)
                    elif (tokens[0] == 'termination_condition'):
                        results.solver.termination_condition = getattr(TerminationCondition, val)
                    else:
                        setattr(results.solver, tokens[0], val)
                elif (section == 'solution'):
                    if (tokens[0] == 'status'):
                        soln.status = getattr(SolutionStatus, tokens[1])
                    elif (tokens[0] == 'gap'):
                        soln.gap = float(tokens[1])
                    elif (tokens[0] == 'objective'):
                        soln.objective['__default_objective__'].value=float(tokens[1])
                        if results.problem.sense == ProblemSense.minimize:
                            results.problem.upper_bound = float(tokens[1])
                        else:
                            results.problem.lower_bound = float(tokens[1])
                    elif (tokens[0] == 'constraintdual'):
                       if tokens[1] != "c_e_ONE_VAR_CONSTANT":
                           soln_constraints[tokens[1]].dual = float(tokens[2])
                    elif (tokens[0] == 'constraintslack'):
                       if tokens[1] != "c_e_ONE_VAR_CONSTANT":
                           soln_constraints[tokens[1]].slack = float(tokens[2])
                    elif (tokens[0] == 'variable'):
                       if tokens[1] != "ONE_VAR_CONSTANT":
                         soln_variables[tokens[1]].value = float(tokens[2])
                    elif (tokens[0] == 'variablerc'):
                       if tokens[1] != "ONE_VAR_CONSTANT":
                         soln_variables[tokens[1]].rc = float(tokens[2])
                    else:
                        setattr(soln, tokens[0], tokens[1])

        INPUT.close()
        results.solution.insert(soln)

if sys.platform == 'win32':
   pyutilib.services.register_executable(name='gurobi.bat')
else:
   pyutilib.services.register_executable(name='gurobi.sh')
