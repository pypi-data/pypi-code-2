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
from coopr.pyomo.base.var import *
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

    #
    # GUROBI warm-start capability is not implemented
    #
    def warm_start_capable(self):

       return False

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
        if sys.platform == 'win32':
           problem_filename  = problem_filename.replace('\\', r'\\')
           solution_filename = solution_filename.replace('\\', r'\\')

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
        script += "gurobi_run%s\n" % str((problem_filename, solution_filename, self.mipgap, options_dict))
        script += "quit()\n"

        self.gurobi_script_file_name = pyutilib.services.TempfileManager.create_tempfile(suffix = '.gurobi.script')
        gurobi_script_file = open(self.gurobi_script_file_name, 'w')
        gurobi_script_file.write( script )
        gurobi_script_file.close()

        # dump the script and warm-start file names for the
        # user if we're keeping files around.
        if self.keepFiles:
           print "Solver script file: '%s'" % self.gurobi_script_file_name

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
            for i in range(0,len(tokens)):
                tokens[i] = tokens[i].strip()

            if (tokens[0] == 'section'):
                if (tokens[1] == 'problem'):
                    section = 'problem'
                elif (tokens[1] == 'solution'):
                    section = 'solution'
                elif (tokens[1] == 'solver'):
                    section = 'solver'
            else:
                if (section == 'problem'):
                    setattr(results.problem, tokens[0], tokens[1])
                elif (section == 'solver'):
                    if (tokens[0] == 'status'):
                        results.solver.status = getattr(SolverStatus, tokens[1])
                    elif (tokens[0] == 'termination_condition'):
                        results.solver.termination_condition = getattr(TerminationCondition, tokens[1])
                    else:
                        setattr(results.solver, tokens[0], tokens[1])
                elif (section == 'solution'):
                    if (tokens[0] == 'status'):
                        soln.status = getattr(SolutionStatus, tokens[1])
                    elif (tokens[0] == 'objective'):
                        soln.objective['f'].vale=eval(tokens[1])
                    elif (tokens[0] == 'constraint'):
                        soln_constraints[tokens[1]].value = eval(tokens[2])
                    elif (tokens[0] == 'variable'):
                        soln_variables[tokens[1]].value = eval(tokens[2])
                    else:
                        setattr(soln, tokens[0], tokens[1])


        INPUT.close()
        results.solution.insert(soln)

if sys.platform == 'win32':
   pyutilib.services.register_executable(name='gurobi.bat')
else:
   pyutilib.services.register_executable(name='gurobi.sh')
