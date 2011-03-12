#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2010 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

import logging

from coopr.opt.base import *
from coopr.opt.results import *
from coopr.opt.solver import *

import mockmip
from pyutilib.misc import Options
from pyutilib.component.core import alias
from pyutilib.services import TempfileManager

logger = logging.getLogger('coopr.plugins')

try:
   # import all the glp_* functions
   from gurobipy import *
   gurobi_python_api_exists = True
except ImportError:
   gurobi_python_api_exists = False

GRB_MAX = -1
GRB_MIN = 1

class gurobi_direct ( OptSolver ):
   """The Gurobi optimization solver (direct API plugin)

The gurobi_direct plugin offers an API interface to Gurobi.  It requires the
Python Gurobi API interface (gurobipy) be in Coopr's lib/ directory.  Generally, if you can run Coopr's Python instance, and execute

>>> import gurobipy
>>>

with no errors, then this plugin will be enabled.

Because of the direct connection with the Gurobi, no temporary files need be
written or read.  That ostensibly makes this a faster plugin than the file-based
Gurobi plugin.  However, you will likely not notice any speed up unless you are
using the GLPK solver with PySP problems (due to the rapid re-solves).

One downside to the lack of temporary files, is that there is no LP file to
inspect for clues while debugging a model.  For that, use the 'write' solver
option:

$ pyomo model.{py,dat} \
  --solver=gurobi_direct \
  --solver-options  write=/path/to/some/file.lp

This is a direct interface to Gurobi's Model.write function, the extension of the file is important.  You could, for example, write the file in MPS format:

$ pyomo model.{py,dat} \
  --solver=gurobi_direct \
  --solver-options  write=/path/to/some/file.mps

   """

   alias('gurobi_direct', doc='Direct Python interface to the Gurobi optimization solver.')

   def __init__(self, **kwds):
      #
      # Call base class constructor
      #
      kwds['type'] = 'gurobi_direct'
      OptSolver.__init__(self, **kwds)

      self._model = None

      # NOTE: eventually both of the following attributes should be migrated
      # to a common base class.  Is the current solve warm-started?  A
      # transient data member to communicate state information across the
      # _presolve, _apply_solver, and _postsolve methods.
      self.warm_start_solve = False

      # Note: Undefined capabilities default to 'None'
      self._capabilities = Options()
      self._capabilities.linear = True
      self._capabilities.quadratic = True
      self._capabilities.integer = True
      self._capabilities.sos1 = True
      self._capabilities.sos2 = True


   def _populate_gurobi_instance ( self, model ):
      from coopr.pyomo.base import Var, VarStatus, Objective, Constraint, \
                                   IntegerSet, BooleanSet
      from coopr.pyomo.expr import is_constant

      try:
         grbmodel = Model( name=model.name )
      except Exception, e:
         msg = 'Unable to create Gurobi model.  Have you installed the Python'\
         '\n       bindings for Gurobi?\n\n\tError message: %s'
         raise Exception, msg % e

      objective = sorted( model.active_components( Objective ).values() )[0]
      sense = GRB_MAX
      if objective.is_minimizing(): sense = GRB_MIN

      constraint_list = model.active_components( Constraint )
      variable_list   = model.active_components( Var )

      grbmodel.ModelSense = sense

      objvar_map = dict()
      var_map    = dict()

      for key in objective:
         expression = objective[ key ].repn
         if is_constant( expression ):
            msg = "Ignoring objective '%s[%s]' which is constant"
            logger.warning( msg % (str(objective), str(key)) )
            continue

         if 1 in expression: # first-order terms
            keys = expression[1].keys()
            for var_key in keys:
               index = var_key.keys()[0]
               label = expression[-1][ index ].label
               coef  = expression[ 1][ var_key ]
               objvar_map[ label ] = coef
               # the coefficients are attached to the model when creating the
               # variables, below


      # In matrix parlance, variables are columns
      for name in variable_list.keys():
         var_set = variable_list[ name ]
         for ii in var_set.keys():
            var = var_set[ ii ]
            if (not var.active) or (var.status is VarStatus.unused) \
               or (var.fixed is True):
               continue

            lb = -GRB.INFINITY
            ub = GRB.INFINITY
            if var.lb is not None:
               lb = var.lb()
            if var.ub is not None:
               ub = var.ub()

            obj_coef = 0
            vlabel = var.label
            if vlabel in objvar_map: obj_coef = objvar_map[ vlabel ]

            # Be sure to impart the integer and binary nature of any variables
            if isinstance(var.domain, IntegerSet):
               var_type = GRB.INTEGER
            elif isinstance(var.domain, BooleanSet):
               var_type = GRB.BINARY
            else:
               var_type = GRB.CONTINUOUS

            var_map[ vlabel ] = grbmodel.addVar(
              lb=lb,
              ub=ub,
              obj=obj_coef,
              vtype=var_type,
              name=vlabel
            )

      grbmodel.update()  # "activate" variables, set up objective function

      for name in constraint_list.keys():
         constraint_set = constraint_list[ name ]
         if constraint_set.trivial: continue

         for ii in constraint_set.keys():
            constraint = constraint_set[ ii ]
            if not constraint.active: continue
            elif constraint.lower is None and constraint.upper is None:
               continue  # not binding at all, don't bother

            expression = constraint.repn
            if 1 in expression: # first-order terms
               linear_coefs = list()
               linear_vars = list()

               keys = expression[1].keys()
               for var_key in keys:
                  index = var_key.keys()[0]
                  var = expression[-1][ index ]
                  coef  = expression[ 1][ var_key ]
                  linear_coefs.append( coef )
                  linear_vars.append( var_map[ var.label ] )

               expr = LinExpr( coeffs=linear_coefs, vars=linear_vars )

            clabel = constraint.label
            #other_bound = float('inf')

            offset = 0.0
            if 0 in constraint.repn:
               offset = constraint.repn[0][None]
            bound = -offset

            if constraint._equality:
               sense = GRB.EQUAL    # Fixed
               bound = constraint.lower() - offset
               grbmodel.addConstr(
                  lhs=expr, sense=sense, rhs=bound, name=clabel )
            else:
               sense = GRB.LESS_EQUAL
               if constraint.upper is not None:
                  bound = constraint.upper() - offset
                  if bound < float('inf'):
                     grbmodel.addConstr(
                       lhs=expr,
                       sense=sense,
                       rhs=bound,
                       name='%s_Upper' % clabel
                     )

               if constraint.lower is not None:
                  bound = constraint.lower() - offset
                  if bound > -float('inf'):
                     grbmodel.addConstr(
                       lhs=bound,
                       sense=sense,
                       rhs=expr,
                       name=clabel
                     )

      grbmodel.update()

      self._gurobi_instance = grbmodel


   def warm_start_capable(self):
      msg = "Gurobi has the ability to use warmstart solutions.  However, it "\
            "has not yet been implemented into the Coopr gurobi_direct plugin."
      logger.info( msg )
      return False


   def warm_start(self, instance):
      pass


   def _presolve(self, *args, **kwargs):
      from coopr.pyomo.base.PyomoModel import Model

      self.warm_start_solve = kwargs.pop( 'warmstart', False )

      model = args[0]
      if len(args) != 1:
         msg = "The gurobi_direct plugin method '_presolve' must be supplied "\
               "a single problem instance - %s were supplied"
         raise ValueError, msg % len(args)
      elif not isinstance(model, Model):
         raise ValueError, "The problem instance supplied to the "            \
              "gurobi_direct plugin '_presolve' method must be of type 'Model'"

      self._populate_gurobi_instance( model )
      grbmodel = self._gurobi_instance

      if 'write' in self.options:
         fname = self.options.write
         grbmodel.write( fname )

      # Scaffolding in place
      if self.warm_start_solve is True:

         if len(args) != 1:
            msg = "The gurobi_direct _presolve method can only handle a single"\
                  "problem instance - %s were supplied"
            raise ValueError, msg % len(args)

         self.warm_start( model )


   def _apply_solver(self):
      # TODO apply appropriate user-specified parameters

      prob = self._gurobi_instance
      prob.setParam( 'OutputFlag', False )

      # Actually solve the problem.
      prob.optimize()


   def _gurobi_get_solution_status ( self ):
      status = self._gurobi_instance.Status
      if   GRB.OPTIMAL         == status: return SolutionStatus.optimal
      elif GRB.INFEASIBLE      == status: return SolutionStatus.infeasible
      elif GRB.CUTOFF          == status: return SolutionStatus.other
      elif GRB.INF_OR_UNBD     == status: return SolutionStatus.other
      elif GRB.INTERRUPTED     == status: return SolutionStatus.other
      elif GRB.LOADED          == status: return SolutionStatus.other
      elif GRB.SUBOPTIMAL      == status: return SolutionStatus.other
      elif GRB.UNBOUNDED       == status: return SolutionStatus.other
      elif GRB.ITERATION_LIMIT == status: return SolutionStatus.stoppedByLimit
      elif GRB.NODE_LIMIT      == status: return SolutionStatus.stoppedByLimit
      elif GRB.SOLUTION_LIMIT  == status: return SolutionStatus.stoppedByLimit
      elif GRB.TIME_LIMIT      == status: return SolutionStatus.stoppedByLimit
      elif GRB.NUMERIC         == status: return SolutionStatus.error
      raise RuntimeError, 'Unknown solution status returned by Gurobi solver'


   def _postsolve(self):
      gprob = self._gurobi_instance
      pvars = gprob.getVars()
      pcons = gprob.getConstrs()

      results = SolverResults()
      soln = Solution()
      problem = results.problem
      solver  = results.solver

      solver.name = "Gurobi %s.%s%s" % gurobi.version()
      # solver.memory_used =
      # solver.user_time = None
      # solver.system_time = None
      solver.wallclock_time = gprob.Runtime
      # solver.termination_condition = None
      # solver.termination_message = None

      problem.name = gprob.ModelName
      problem.lower_bound = None
      problem.upper_bound = None
      problem.number_of_constraints          = gprob.NumConstrs
      problem.number_of_nonzeros             = gprob.NumNZs
      problem.number_of_variables            = gprob.NumVars
      problem.number_of_binary_variables     = gprob.NumBinVars
      problem.number_of_integer_variables    = gprob.NumIntVars
      problem.number_of_continuous_variables = gprob.NumVars \
                                              - gprob.NumIntVars \
                                              - gprob.NumBinVars
      problem.number_of_objectives = 1
      problem.number_of_solutions = gprob.SolCount

      problem.sense = ProblemSense.minimize
      if problem.sense == GRB_MAX: problem.sense = ProblemSense.maximize

      soln.status = self._gurobi_get_solution_status()

      if soln.status in (SolutionStatus.optimal, SolutionStatus.stoppedByLimit):
         obj_val = gprob.ObjVal
         if problem.sense == ProblemSense.minimize:
            problem.lower_bound = obj_val
         else:
            problem.upper_bound = obj_val

         soln.objective['__default_objective__'].value = obj_val

         for var in pvars:
            soln.variable[ var.VarName ] = var.X

         # for con in pcons:
                 # Having an issue correctly getting the constraints
                 # so punting for now
            # soln.constraint[ con.ConstrName ] = con.


      results.solution.insert(soln)

      self.results = results

      # Done with the model object; free up some memory.
      del gprob, self._gurobi_instance

      # let the base class deal with returning results.
      return OptSolver._postsolve(self)


if not gurobi_python_api_exists:
   SolverFactory().deactivate('gurobi_direct')
   SolverFactory().deactivate('_mock_gurobi_direct')
