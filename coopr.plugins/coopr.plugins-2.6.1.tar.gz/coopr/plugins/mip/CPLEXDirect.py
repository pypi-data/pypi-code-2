#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2010 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________


import os
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

import xml.dom.minidom

import time

try:
    import cplex
    from cplex.exceptions import CplexError
    cplex_import_available=True
except ImportError:
    cplex_import_available=False


class CPLEXDirect(OptSolver):
    """The CPLEX LP/MIP solver
    """

    pyutilib.component.core.alias('cplexdirect',  doc='Direct Python interface to the CPLEX LP/MIP solver')

    def __init__(self, **kwds):
        #
        # Call base class constructor
        #
        kwds['type'] = 'cplexdirect'
        OptSolver.__init__(self, **kwds)

        # NOTE: eventually both of the following attributes should be migrated to a common base class.
        # is the current solve warm-started? a transient data member to communicate state information
        # across the _presolve, _apply_solver, and _postsolve methods.
        self.warm_start_solve = False

        # the working problem instance, via CPLEX python constructs.
        self._active_cplex_instance = None

        # Note: Undefined capabilities default to 'None'
        self._capabilities = pyutilib.misc.Options()
        self._capabilities.linear = True
        self._capabilities.quadratic = True
        self._capabilities.integer = True
        self._capabilities.sos1 = True
        self._capabilities.sos2 = True

    #
    # ultimately, this utility should go elsewhere - perhaps on the PyomoModel itself.
    # in the mean time, it is staying here.
    #
    def _hasIntegerVariables(self, instance):

       from coopr.pyomo.base import Var
       from coopr.pyomo.base.set_types import IntegerSet, BooleanSet

       for variable in instance.active_components(Var).values():

           if (isinstance(variable.domain, IntegerSet) is True) or (isinstance(variable.domain, BooleanSet) is True):

               return True

       return False

    #
    # TBD
    #
    def _evaluate_bound(self, exp):

        from coopr.pyomo.expr import is_constant
        from coopr.pyomo.base import expr

        if isinstance(exp, expr._IdentityExpression):
           return self._evaluate_bound(exp._args[0])
        elif exp.is_constant():
           return exp()
        else:
           raise ValueError, "ERROR: nonconstant bound: " + str(exp)

    #
    # CPLEX requires objective expressions to be specified via something other than a sparse pair!
    # NOTE: The returned offset is guaranteed to be a float.
    #
    def _encode_constraint_body(self, expression, as_pairs=False):

       variables = [] # string names of variables
       coefficients = [] # variable coefficients

       pairs = []

       hash_to_variable_map = expression[-1]

       for variable_hash, coefficient in expression[1].iteritems():

          variable_hash_iter = variable_hash.iterkeys()
          variable_name = hash_to_variable_map[variable_hash_iter.next()].label

          if as_pairs is True:
             pairs.append((variable_name, coefficient))
          else:
             variables.append(variable_name)
             coefficients.append(coefficient)

       offset=0.0
       if 0 in expression:
           offset = expression[0][None]

       if as_pairs is True:
          pairs.append((1, offset))
          return pairs, 0.0
       else:
          expr = cplex.SparsePair(ind=variables, val=coefficients)
          return expr, offset

    #
    # method to populate the CPLEX problem instance (interface) from the supplied Pyomo problem instance.
    #
    def _populate_cplex_instance(self, pyomo_instance):

       from coopr.pyomo.base import Var, VarStatus, Objective, Constraint, IntegerSet, BooleanSet
       from coopr.pyomo.base.numtypes import minimize, maximize
       from coopr.pyomo.expr import is_constant

       # TBD
       cplex_instance = None
       try:
          cplex_instance = cplex.Cplex()
       except CplexError, exc:
          print exc
          raise ValueError, "TBD - FAILED TO CREATE CPLEX INSTANCE!"

       # cplex wants the caller to set the problem type, which is (for current
       # purposes) strictly based on variable type counts.
       num_binary_variables = 0
       num_integer_variables = 0
       num_continuous_variables = 0

       # transfer the variables from pyomo to cplex.
       var_names = []
       var_lbs = []
       var_ubs = []
       var_types = []

       active_variables = pyomo_instance.active_components(Var)
       for var in active_variables.values():
          for ndx in var:
             if (not var[ndx].active) or (var[ndx].status is VarStatus.unused) or (var[ndx].fixed is True) :
                continue
             var_names.append(var[ndx].label)
             if var[ndx].lb is None:
                var_lbs.append(-cplex.infinity)
             else:
                var_lbs.append(var[ndx].lb())
             if var[ndx].ub is None:
                var_ubs.append(cplex.infinity)
             else:
                var_ubs.append(var[ndx].ub())
             if isinstance(var.domain, IntegerSet):
                var_types.append(cplex_instance.variables.type.integer)
                num_integer_variables += 1
             elif isinstance(var.domain, BooleanSet):
                var_types.append(cplex_instance.variables.type.binary)
                num_binary_variables += 1
             else:
                var_types.append(cplex_instance.variables.type.continuous)
                num_continuous_variables += 1

       cplex_instance.variables.add(names=var_names, lb=var_lbs, ub=var_ubs, types=var_types)

       # transfer the constraints.
       expressions = []
       senses = []
       rhss = []
       range_values = []
       names = []

       active_constraints = pyomo_instance.active_components(Constraint)
       for key in active_constraints: # TBD: xfer to more efficient looping - use itervalues, for example.

          if active_constraints[key].trivial:
             continue

          constraint = active_constraints[key]
          for cndx in constraint: # TBD: more efficient looping here.
            if not constraint[cndx].active:
                 continue

            # There are conditions, e.g., when fixing variables, under which
            # a constraint block might be empty.  Ignore these, for both
            # practical reasons and the fact that the CPLEX LP format
            # requires a variable in the constraint body.  It is also
            # possible that the body of the constraint consists of only a
            # constant, in which case the "variable" of
            if is_constant(constraint[cndx].repn):
                   continue

            names.append(constraint[cndx].label)

            expr, offset = self._encode_constraint_body(constraint[cndx].repn)

            expressions.append(expr)

            if constraint[cndx]._equality:
                # equality constraint.
                senses.append('E')
                bound_expr = constraint[cndx].lower
                bound = self._evaluate_bound(bound_expr) - offset
                rhss.append(bound)
                range_values.append(0.0)

            elif (constraint[cndx].lower is not None) and (constraint[cndx].upper is not None):
                # ranged constraint.
                senses.append('R')
                lower_bound_expr = constraint[cndx].lower # TBD - watch the offset - why not subtract?
                lower_bound = self._evaluate_bound(lower_bound_expr)
                upper_bound_expr = constraint[cndx].upper # TBD - watch the offset - why not subtract?
                upper_bound = self._evaluate_bound(upper_bound_expr)
                rhss.append(lower_bound)
                range_values.append(upper_bound-lower_bound)

            elif constraint[cndx].lower is not None:
                senses.append('G')
                bound_expr = constraint[cndx].lower
                bound = self._evaluate_bound(bound_expr) - offset
                rhss.append(bound)
                range_values.append(0.0)

            else:
                senses.append('L')
                bound_expr = constraint[cndx].upper
                bound = self._evaluate_bound(bound_expr) - offset
                rhss.append(bound)
                range_values.append(0.0)

       cplex_instance.linear_constraints.add(lin_expr=expressions, senses=senses, rhs=rhss, range_values=range_values, names=names)

       # transfer the objective.
       active_objectives = pyomo_instance.active_components(Objective)
       the_objective = active_objectives[active_objectives.keys()[0]]
       if the_objective.sense == maximize:
          cplex_instance.objective.set_sense(cplex_instance.objective.sense.maximize)
       else:
          cplex_instance.objective.set_sense(cplex_instance.objective.sense.minimize)

       objective_expression, junk = self._encode_constraint_body(the_objective[None].repn, True) # how to deal with indexed objectives?
       cplex_instance.objective.set_linear(objective_expression)
       cplex_instance.objective.set_name(the_objective.name)

       # set the problem type based on the variable counts.
       if (num_integer_variables > 0) or (num_binary_variables > 0):
          cplex_instance.set_problem_type(cplex_instance.problem_type.MILP)
       else:
          cplex_instance.set_problem_type(cplex_instance.problem_type.LP)

#       cplex_instance.write("new.lp")

       self._active_cplex_instance = cplex_instance

    #
    # cplex has a simple, easy-to-use warm-start capability.
    #
    def warm_start_capable(self):

       return True

    #
    # write a warm-start file in the CPLEX MST format.
    #
    def warm_start(self, instance):

       from coopr.pyomo.base import Var, VarStatus

       # the iteration order is identical to that used in generating
       # the cplex instance, so all should be well.
       variable_names = []
       variable_values = []
       for variable in instance.active_components(Var).values():
          for index in variable: # TBD - change iteration style.
             if (variable[index].status != VarStatus.unused) and (variable[index].value != None) and (variable[index].fixed == False):
                name = variable[index].label
                value = variable[index].value
                variable_names.append(name)
                variable_values.append(value)

       self._active_cplex_instance.MIP_starts.add([variable_names, variable_values],
                                                  self._active_cplex_instance.MIP_starts.effort_level.auto)

    # over-ride presolve to extract the warm-start keyword, if specified.
    def _presolve(self, *args, **kwds):
       from coopr.pyomo.base.PyomoModel import Model

       self.warm_start_solve = kwds.pop( 'warmstart', False )

       model = args[ 0 ]

       # Step 1: extract the pyomo instance from the input arguments,
       #         cache it, and create the corresponding (as of now empty)
       #         CPLEX problem instance.
       if len(args) != 1:
          msg = "The CPLEXDirect plugin method '_presolve' must be supplied " \
                "a single problem instance - %s were supplied"
          raise ValueError, msg % len(args)
       if not isinstance(model, Model):
          msg = "The problem instance supplied to the CPLEXDirect plugin "    \
                "method '_presolve' must be of type 'Model'"
          raise ValueError, msg

       # TBD-document.
       self._populate_cplex_instance(model)

       # if the first argument is a string (representing a filename),
       # then we don't have an instance => the solver is being applied
       # to a file.

       if (len(args) > 0) and not isinstance(model,basestring):

          # write the warm-start file - currently only supports MIPs.
          # we only know how to deal with a single problem instance.
          if self.warm_start_solve is True:

             if len(args) != 1:
                msg = "CPLEX _presolve method can only handle a single "      \
                      "problem instance - %s were supplied"
                raise ValueError, msg % len(args)

             if self._hasIntegerVariables(model) is True:
                start_time = time.time()
                self.warm_start(model)
                end_time = time.time()
                if self._report_timing is True:
                   print "Warm start write time="+str(end_time-start_time)+" seconds"

    #
    # TBD
    #
    def _apply_solver(self):

       # set up all user-specified parameters.
       if (self.options.mipgap is not None) and (self.options.mipgap > 0.0):
          self._active_cplex_instance.parameters.mip.tolerances.mipgap.set(self.options.mipgap)

       # and kick off the solve.
       self._active_cplex_instance.set_results_stream(None)
       self._active_cplex_instance.solve()

    def create_command_line(self,executable,problem_files):

        #
        # Define log file
        # The log file in CPLEX contains the solution trace, but the solver status can be found in the solution file.
        #
        self.log_file = pyutilib.services.TempfileManager.create_tempfile(suffix = '.cplex.log')

        #
        # Define solution file
        # As indicated above, contains (in XML) both the solution and solver status.
        #
        self.soln_file = pyutilib.services.TempfileManager.create_tempfile(suffix = '.cplex.sol')

        #
        # Define results file
        #
        if self._results_format is None or self._results_format == ResultsFormat.soln:
           self.results_file = self.soln_file
        elif self._results_format == ResultsFormat.sol:
           self.results_file = self.sol_file

        #
        # Write the CPLEX execution script
        #
        self.cplex_script_file_name = pyutilib.services.TempfileManager.create_tempfile(suffix = '.cplex.script')
        cplex_script_file = open(self.cplex_script_file_name,'w')
        cplex_script_file.write("set logfile "+self.log_file+"\n")
        if self._timelimit is not None and self._timelimit > 0.0:
            cplex_script_file.write("set timelimit "+`self._timelimit`+"\n")
        if (self.options.mipgap is not None) and (self.options.mipgap > 0.0):
            cplex_script_file.write("set mip tolerances mipgap "+`self.options.mipgap`+"\n")
        for key in self.options:
                if key == 'relax_integrality' or key == 'mipgap':
                    continue
                elif isinstance(self.options[key],basestring) and ' ' in self.options[key]:
                    opt = " ".join(key.split('_'))+" "+str(self.options[key])
                else:
                    opt = " ".join(key.split('_'))+" "+str(self.options[key])
                cplex_script_file.write("set "+opt+"\n")
        cplex_script_file.write("read "+problem_files[0]+"\n")

        # if we're dealing with an LP, the MST file will be empty.
        if (self.warm_start_solve is True) and (self.warm_start_file_name is not None):
            cplex_script_file.write("read "+self.warm_start_file_name+"\n")

        if 'relax_integrality' in self.options:
            cplex_script_file.write("change problem lp\n")

        cplex_script_file.write("display problem stats\n")
        cplex_script_file.write("optimize\n")
        cplex_script_file.write("write " + self.soln_file+"\n")
        cplex_script_file.write("quit\n")
        cplex_script_file.close()

        # dump the script and warm-start file names for the
        # user if we're keeping files around.
        if self.keepFiles:
           print "Solver script file=" + self.cplex_script_file_name
           if (self.warm_start_solve is True) and (self.warm_start_file_name is not None):
              print "Solver warm-start file=" + self.warm_start_file_name

        #
        # Define command line
        #
        if self._problem_format in [ProblemFormat.cpxlp, ProblemFormat.mps]:
           proc = self._timer + " " + self.executable() + " < " + self.cplex_script_file_name
        return pyutilib.misc.Bunch(cmd=proc, log_file=self.log_file, env=None)

    def process_logfile(self):

        """
        Process logfile
        """
        results = SolverResults()
        results.problem.number_of_variables = None
        results.problem.number_of_nonzeros = None
        #
        # Process logfile
        #
        OUTPUT = open(self.log_file)
        output = "".join(OUTPUT.readlines())
        OUTPUT.close()
        #
        # It is generally useful to know the CPLEX version number for logfile parsing.
        #
        cplex_version = None

        #
        # Parse logfile lines
        #
        for line in output.split("\n"):
            tokens = re.split('[ \t]+',line.strip())
            if len(tokens) > 3 and tokens[0] == "CPLEX" and tokens[1] == "Error":
                # IMPT: See below - cplex can generate an error line and then terminate fine, e.g., in CPLEX 12.1.
                #       To handle these cases, we should be specifying some kind of termination criterion always
                #       in the course of parsing a log file (we aren't doing so currently - just in some conditions).
                results.solver.status=SolverStatus.error
                results.solver.error = " ".join(tokens)
            elif len(tokens) >= 3 and tokens[0] == "ILOG" and tokens[1] == "CPLEX":
                cplex_version = tokens[2].rstrip(',')
            elif len(tokens) >= 3 and tokens[0] == "Variables":
                if results.problem.number_of_variables is None: # CPLEX 11.2 and subsequent versions have two Variables sections in the log file output.
                    results.problem.number_of_variables = eval(tokens[2])
            # In CPLEX 11 (and presumably before), there was only a single line output to
            # indicate the constriant count, e.g., "Linear constraints : 16 [Less: 7, Greater: 6, Equal: 3]".
            # In CPLEX 11.2 (or somewhere in between 11 and 11.2 - I haven't bothered to track it down
            # in that detail), there is another instance of this line prefix in the min/max problem statistics
            # block - which we don't care about. In this case, the line looks like: "Linear constraints :" and
            # that's all.
            elif len(tokens) >= 4 and tokens[0] == "Linear" and tokens[1] == "constraints":
                results.problem.number_of_constraints = eval(tokens[3])
            elif len(tokens) >= 3 and tokens[0] == "Nonzeros":
                if results.problem.number_of_nonzeros is None: # CPLEX 11.2 and subsequent has two Nonzeros sections.
                    results.problem.number_of_nonzeros = eval(tokens[2])
            elif len(tokens) >= 5 and tokens[4] == "MINIMIZE":
                results.problem.sense = ProblemSense.minimize
            elif len(tokens) >= 5 and tokens[4] == "MAXIMIZE":
                results.problem.sense = ProblemSense.maximize
            elif len(tokens) >= 4 and tokens[0] == "Solution" and tokens[1] == "time" and tokens[2] == "=":
               # technically, I'm not sure if this is CPLEX user time or user+system - CPLEX doesn't appear
               # to differentiate, and I'm not sure we can always provide a break-down.
               results.solver.user_time = eval(tokens[3])
            elif len(tokens) >= 4 and tokens[0] == "Dual" and tokens[1] == "simplex" and tokens[3] == "Optimal:":
                results.solver.termination_condition = TerminationCondition.optimal
                results.solver.termination_message = ' '.join(tokens)
            elif len(tokens) >= 4 and tokens[0] == "MIP" and tokens[2] == "Integer" and tokens[3] == "infeasible.":
                # if CPLEX has previously printed an error message, reduce it to a warning -
                # there is a strong indication it recovered, but we can't be sure.
                if results.solver.status == SolverStatus.error:
                   results.solver.status = SolverStatus.warning
                else:
                   results.solver.status = SolverStatus.ok
                results.solver.termination_condition = TerminationCondition.infeasible
                results.solver.termination_message = ' '.join(tokens)
            # for the case below, CPLEX sometimes reports "true" optimal (the first case)
            # and other times within-tolerance optimal (the second case).
            elif (len(tokens) >= 4 and tokens[0] == "MIP" and tokens[2] == "Integer" and tokens[3] == "optimal") or \
                 (len(tokens) >= 4 and tokens[0] == "MIP" and tokens[2] == "Integer" and tokens[3] == "optimal,"):
                # if CPLEX has previously printed an error message, reduce it to a warning -
                # there is a strong indication it recovered, but we can't be sure.
                if results.solver.status == SolverStatus.error:
                   results.solver.status = SolverStatus.warning
                else:
                   results.solver.status = SolverStatus.ok
                results.solver.termination_condition = TerminationCondition.optimal
                results.solver.termination_message = ' '.join(tokens)
            elif len(tokens) >= 3 and tokens[0] == "Presolve" and tokens[2] == "Infeasible.":
                # if CPLEX has previously printed an error message, reduce it to a warning -
                # there is a strong indication it recovered, but we can't be sure.
                if results.solver.status == SolverStatus.error:
                   results.solver.status = SolverStatus.warning
                else:
                   results.solver.status = SolverStatus.ok
                results.solver.termination_condition = TerminationCondition.infeasible
                results.solver.termination_message = ' '.join(tokens)
            elif len(tokens) >= 5 and tokens[0] == "Presolve" and tokens[2] == "Unbounded" and tokens[4] == "infeasible.":
                # if CPLEX has previously printed an error message, reduce it to a warning -
                # there is a strong indication it recovered, but we can't be sure.
                if results.solver.status == SolverStatus.error:
                   results.solver.status = SolverStatus.warning
                else:
                   results.solver.status = SolverStatus.ok
                # It isn't clear whether we can determine if the problem is unbounded from
                # CPLEX's output.
                results.solver.termination_condition = TerminationCondition.unbounded
                results.solver.termination_message = ' '.join(tokens)

        try:
            results.solver.termination_message = pyutilib.misc.yaml_fix(results.solver.termination_message)
        except:
            pass
        return results

    def process_soln_file(self,results):

        # the only suffixes that we extract from CPLEX are
        # constraint duals, constraint slacks, and variable
        # reduced-costs. scan through the solver suffix list
        # and throw an exception if the user has specified
        # any others.
        extract_duals = False
        extract_slacks = False
        extract_reduced_costs = False
        for suffix in self.suffixes:
           flag=False
           if re.match(suffix,"dual"):
                extract_duals = True
                flag=True
           if re.match(suffix,"slack"):
                extract_slacks = True
                flag=True
           if re.match(suffix,"rc"):
                extract_reduced_costs = True
                flag=True
           if not flag:
              raise RuntimeError,"***CPLEX solver plugin cannot extract solution suffix="+suffix

        lp_solution = False
        if not os.path.exists(self.soln_file):
           return

        soln = Solution()
        soln.objective['__default_objective__'].value=None
        INPUT = open(self.soln_file,"r")
        results.problem.number_of_objectives=1
        mip_problem=False
        for line in INPUT:
            line = line.strip()
            line = line.lstrip('<?/')
            line = line.rstrip('/>?')
            tokens=line.split(' ')

            if tokens[0] == "variable":
                variable_name = None
                variable_value = None
                variable_reduced_cost = None
                variable_status = None
                for i in range(1,len(tokens)):
                   field_name =  string.strip(tokens[i].split('=')[0])
                   field_value = (string.strip(tokens[i].split('=')[1])).lstrip("\"").rstrip("\"")
                   if field_name == "name":
                      variable_name = field_value
                   elif field_name == "value":
                      variable_value = field_value
                   elif (extract_reduced_costs is True) and (field_name == "reducedCost"):
                      variable_reduced_cost = field_value
                   elif (extract_reduced_costs is True) and (field_name == "status"):
                      variable_status = field_value

                # skip the "constant-one" variable, used to capture/retain objective offsets in the CPLEX LP format.
                if variable_name != "ONE_VAR_CONSTANT":
                   variable = None # cache the solution variable reference, as the getattr is expensive.
                   try:
                       variable = soln.variable[variable_name]
                       variable.value = eval(variable_value)
                   except:
                       variable.value = variable_value
                   if (variable_reduced_cost is not None) and (extract_reduced_costs is True):
                        try:
                            variable.rc = eval(variable_reduced_cost)
                            if variable_status is not None:
                               if variable_status == "LL":
                                  variable.lrc = eval(variable_reduced_cost)
                               else:
                                  variable.lrc = 0.0
                               if variable_status == "UL":
                                  variable.urc = eval(variable_reduced_cost)
                               else:
                                  variable.urc = 0.0
                        except:
                            raise ValueError, "Unexpected reduced-cost value="+str(variable_reduced_cost)+" encountered for variable="+variable_name
            elif (tokens[0] == "constraint") and ((extract_duals is True) or (extract_slacks is True)):
                constraint_name = None
                constraint_dual = None
                constaint = None # cache the solution constraint reference, as the getattr is expensive.
                for i in range(1,len(tokens)):
                   field_name =  string.strip(tokens[i].split('=')[0])
                   field_value = (string.strip(tokens[i].split('=')[1])).lstrip("\"").rstrip("\"")
                   if field_name == "name":
                      constraint_name = field_value
                      constraint = soln.constraint[constraint_name]
                   elif (extract_duals is True) and (field_name == "dual"): # for LPs
                      # assumes the name field is first.
                      if eval(field_value) != 0.0:
                        constraint.dual = eval(field_value)
                   elif (extract_slacks is True) and (field_name == "slack"): # for MIPs
                      # assumes the name field is first.
                      if eval(field_value) != 0.0:
                        constraint.slack = eval(field_value)
            elif tokens[0].startswith("problemName"):
                filename = (string.strip(tokens[0].split('=')[1])).lstrip("\"").rstrip("\"")
                #print "HERE",filename
                results.problem.name = os.path.basename(filename)
                if '.' in results.problem.name:
                    results.problem.name = results.problem.name.split('.')[0]
                tINPUT=open(filename,"r")
                for tline in tINPUT:
                    tline = tline.strip()
                    if tline == "":
                        continue
                    tokens = re.split('[\t ]+',tline)
                    if tokens[0][0] in ['\\', '*']:
                        continue
                    elif tokens[0] == "NAME":
                        results.problem.name = tokens[1]
                    else:
                        sense = tokens[0].lower()
                        if sense in ['max','maximize']:
                            results.problem.sense = ProblemSense.maximize
                        if sense in ['min','minimize']:
                            results.problem.sense = ProblemSense.minimize
                    break
                tINPUT.close()

            elif tokens[0].startswith("objectiveValue"):
                objective_value = (string.strip(tokens[0].split('=')[1])).lstrip("\"").rstrip("\"")
                soln.objective['__default_objective__'].value = eval(objective_value)
            elif tokens[0].startswith("solutionStatusString"):
                solution_status = (string.strip(" ".join(tokens).split('=')[1])).lstrip("\"").rstrip("\"")
                if solution_status in ["optimal", "integer optimal solution", "integer optimal, tolerance"]:
                    soln.status = SolutionStatus.optimal
                    soln.gap = 0.0
                    if results.problem.sense == ProblemSense.minimize:
                        results.problem.lower_bound = soln.objective['__default_objective__'].value
                        if "upper_bound" in dir(results.problem):
                            del results.problem.upper_bound
                    else:
                        results.problem.upper_bound = soln.objective['__default_objective__'].value
                        if "lower_bound" in dir(results.problem):
                            del results.problem.lower_bound
                    mip_problem=True
                elif solution_status in ["infeasible"]:
                    soln.status = SolutionStatus.infeasible
                    soln.gap = None
            elif tokens[0].startswith("MIPNodes"):
                if mip_problem:
                    n = eval(eval(string.strip(" ".join(tokens).split('=')[1])).lstrip("\"").rstrip("\""))
                    results.solver.statistics.branch_and_bound.number_of_created_subproblems=n
                    results.solver.statistics.branch_and_bound.number_of_bounded_subproblems=n


        if not results.solver.status is SolverStatus.error:
            results.solution.insert(soln)

        INPUT.close()

    def _postsolve(self):

        instance = self._active_cplex_instance

        results = SolverResults()
        results.problem.name = instance.get_problem_name()
        results.problem.lower_bound = None
        results.problem.upper_bound = None
        results.problem.number_of_variables = None
        results.problem.number_of_constraints = None
        results.problem.number_of_nonzeros = None
        results.problem.number_of_binary_variables = None
        results.problem.number_of_integer_variables = None
        results.problem.number_of_continuous_variables = None
        results.problem.number_of_objectives = 1

        results.solver.name = "CPLEX "+instance.get_version()
#        results.solver.status = None
        results.solver.return_code = None
        results.solver.message = None
        results.solver.user_time = None
        results.solver.system_time = None
        results.solver.wallclock_time = None
        results.solver.termination_condition = None
        results.solver.termination_message = None

        soln = Solution()
        soln.objective['__default_objective__'].value = instance.solution.get_objective_value()

        num_variables = instance.variables.get_num()
        variable_names = instance.variables.get_names()
        variable_values = instance.solution.get_values()
#        print "VARIABLE NAMES=",variable_names
#        print "VARIABLE VALUES=",variable_values
        for i in range(0,num_variables):
#           print "NAME=",variable_names[i]
           variable_name = variable_names[i]
           variable = None # cache the solution variable reference, as the getattr is expensive.
           try:
              variable = soln.variable[variable_name]
              variable.value = variable_values[i]
           except:
              variable.value = variable_values[i]

        results.solution.insert(soln)
	#print type(instance),dir(instance.objective)
	self._symbol_map = {}
	self._symbol_map['__default_objective__'] = instance.objective.get_name()

        self.results = results

        # don't know if any of this is necessary!

        # take care of the annoying (and empty) CPLEX temporary files in the current directory.
        # this approach doesn't seem overly efficient, but python os module functions don't
        # accept regular expression directly.
        filename_list = os.listdir(".")
        for filename in filename_list:
           # CPLEX temporary files come in two flavors - cplex.log and clone*.log.
           # the latter is the case for multi-processor environments.
           # IMPT: trap the possible exception raised by the file not existing.
           #       this can occur in pyro environments where > 1 workers are
           #       running CPLEX, and were started from the same directory.
           #       these logs don't matter anyway (we redirect everything),
           #       and are largely an annoyance.
           try:
              if  re.match('cplex\.log', filename) != None:
                  os.remove(filename)
              elif re.match('clone\d+\.log', filename) != None:
                  os.remove(filename)
           except OSError:
              pass

        # let the base class deal with returning results.
        return OptSolver._postsolve(self)


if cplex_import_available is False:
   SolverFactory().deactivate('cplexdirect')
   SolverFactory().deactivate('_mock_cplexdirect')

