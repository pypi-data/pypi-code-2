#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2010 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  Fr more information, see the Coopr README.txt file.
#  _________________________________________________________________________


import gc         # garbage collection control.
import os
import pickle
import pstats     # for profiling
import sys
import time
import traceback

from optparse import OptionParser

# for profiling
try:
    import cProfile as profile
except ImportError:
    import profile

# Coopr
from coopr.opt.base import SolverFactory
from coopr.pysp.scenariotree import *

from pyutilib.misc import import_file
from pyutilib.services import TempfileManager

# Pyro
import Pyro.core
import Pyro.naming
from Pyro.errors import PyroError, NamingError

from phutils import *
from phobjective import *

# disable multi-threading. for a solver server, this
# would truly be a bad idea, as you (1) likely have limited
# solver licenses and (2) likely want to dedicate all compute
# resources on this node to a single solve.
Pyro.config.PYRO_MULTITHREADED=0

#
# the class responsible for executing all solution server requests.
#
class PHSolverServer(object):

   def __init__(self, scenario_instances, solver, scenario_tree):

      # the obvious stuff!
      self._instances = scenario_instances # a map from scenario name to pyomo model instance
      self._solver = solver
      self._scenario_tree = scenario_tree

      # the objective functions are modified throughout the course of PH iterations.
      # save the original, as a baseline to modify in subsequent iterations. reserve
      # the original objectives, for subsequent modification.
      self._original_objective_expression = {}
      for instance_name, instance in self._instances.items():
         objective_name = instance.active_components(Objective).keys()[0]
         expr = instance.active_components(Objective)[objective_name]._data[None].expr
         if isinstance(expr, Expression) is False:
            expr = _IdentityExpression(expr)
         self._original_objective_expression[instance_name] = expr

      # the server is in one of two modes - solve the baseline instances, or
      # those augmented with the PH penalty terms. default is standard.
      # NOTE: This is currently a global flag for all scenarios handled
      #       by this server - easy enough to extend if we want.
      self._solving_standard_objective = True

   def enable_standard_objective(self):

#      print "RECEIVED REQUEST TO ENABLE STANDARD OBJECTIVE FOR ALL SCENARIOS"

      self._solving_standard_objective = True

   def enable_ph_objective(self):

#      print "RECEIVED REQUEST TO ENABLE PH OBJECTIVE FOR ALL SCENARIOS"

      self._solving_standard_objective = False

   def solve(self, scenario_name):

#      print "RECEIVED REQUEST TO SOLVE SCENARIO INSTANCE="+scenario_name
#      if self._solving_standard_objective is True:
#         print "OBJECTIVE=STANDARD"
#      else:
#         print "OBJECTIVE=PH"

      if scenario_name not in self._instances:
         print "***ERROR: Requested instance to solve not in PH solver server instance collection!"
         return None
      scenario_instance = self._instances[scenario_name]

      # form the desired objective, depending on the solve mode.
      if self._solving_standard_objective is True:
         form_standard_objective(scenario_name, scenario_instance, self._original_objective_expression[scenario_name], self._scenario_tree)
      else:
         # TBD - command-line drive the various options (integer tolerance, breakpoint strategies, etc.)
         form_ph_objective(scenario_name, scenario_instance, \
                           self._original_objective_expression[scenario_name], self._scenario_tree, \
                           False, False, False, 0, 0.00001)

      # IMPT: You have to re-presolve, as the simple presolver collects the linear terms together. If you
      # don't do this, you won't see any chance in the output files as you vary the problem parameters!
      # ditto for instance fixing!
      scenario_instance.preprocess()

      results = self._solver.solve(scenario_instance)

      print "Successfully solved scenario instance="+scenario_name
#      print "RESULTS:"
#      results.write(num=1)
      encoded_results = pickle.dumps(results)

      return encoded_results

   def update_weights_and_averages(self, scenario_name, new_weights, new_averages):

#      print "RECEIVED REQUEST TO UPDATE WEIGHTS AND AVERAGES FOR SCENARIO=",scenario_name

      if scenario_name not in self._instances:
         print "***ERROR: Received request to update weights for instance not in PH solver server instance collection!"
         return None
      scenario_instance = self._instances[scenario_name]

      for weight_update in new_weights:

         weight_index = weight_update._index

         target_weight_parameter = getattr(scenario_instance, weight_update.name)

         for index in weight_index:
            target_weight_parameter[index] = value(weight_update[index])

      for average_update in new_averages:

         average_index = average_update._index

         target_average_parameter = getattr(scenario_instance, average_update.name)

         for index in average_index:
            target_average_parameter[index] = value(average_update[index])

   def update_rhos(self, scenario_name, new_rhos):

#      print "RECEIVED REQUEST TO UPDATE RHOS FOR SCENARIO=",scenario_name

      if scenario_name not in self._instances:
         print "***ERROR: Received request to update weights for instance not in PH solver server instance collection!"
         return None
      scenario_instance = self._instances[scenario_name]

      for rho_update in new_rhos:

         rho_index = rho_update._index

         target_rho_parameter = getattr(scenario_instance, rho_update.name)

         for index in rho_index:
            target_rho_parameter[index] = value(rho_update[index])

   def update_tree_node_statistics(self, scenario_name, new_node_minimums, new_node_maximums):

#      print "RECEIVED REQUEST TO UPDATE TREE NODE STATISTICS SCENARIO=",scenario_name

      for tree_node_name, tree_node_minimums in new_node_minimums.items():

         tree_node = self._scenario_tree._tree_node_map[tree_node_name]
         tree_node._minimums = tree_node_minimums

      for tree_node_name, tree_node_maximums in new_node_maximums.items():

         tree_node = self._scenario_tree._tree_node_map[tree_node_name]
         tree_node._maximums = tree_node_maximums


#
# utility method to construct an option parser for ph arguments, to be
# supplied as an argument to the runph method.
#

def construct_options_parser(usage_string):

   solver_list = SolverFactory.services()
   solver_list = sorted( filter(lambda x: '_' != x[0], solver_list) )
   solver_help = \
   "Specify the solver with which to solve scenario sub-problems.  The "      \
   "following solver types are currently supported: %s; Default: cplex"
   solver_help %= ', '.join( solver_list )

   parser = OptionParser()
   parser.add_option("--verbose",
                     help="Generate verbose output for both initialization and execution. Default is False.",
                     action="store_true",
                     dest="verbose",
                     default=False)
   parser.add_option("--scenario",
                     help="Specify a scenario that this server is responsible for solving",
                     action="append",
                     dest="scenarios",
                     default=[])
   parser.add_option("--all-scenarios",
                     help="Indicate that the server is responsible for solving all scenarios",
                     action="store_true",
                     dest="all_scenarios",
                     default=False)
   parser.add_option("--report-solutions",
                     help="Always report PH solutions after each iteration. Enabled if --verbose is enabled. Default is False.",
                     action="store_true",
                     dest="report_solutions",
                     default=False)
   parser.add_option("--report-weights",
                     help="Always report PH weights prior to each iteration. Enabled if --verbose is enabled. Default is False.",
                     action="store_true",
                     dest="report_weights",
                     default=False)
   parser.add_option('-m',"--model-directory",
                     help="The directory in which all model (reference and scenario) definitions are stored. Default is \".\".",
                     action="store",
                     dest="model_directory",
                     type="string",
                     default=".")
   parser.add_option('-i',"--instance-directory",
                     help="The directory in which all instance (reference and scenario) definitions are stored. Default is \".\".",
                     action="store",
                     dest="instance_directory",
                     type="string",
                     default=".")
   parser.add_option("--solver",
                     help=solver_help,
                     action="store",
                     dest="solver_type",
                     type="string",
                     default="cplex")
   parser.add_option("--scenario-solver-options",
                     help="Solver options for all PH scenario sub-problems",
                     action="append",
                     dest="scenario_solver_options",
                     type="string",
                     default=[])
   parser.add_option("--scenario-mipgap",
                     help="Specifies the mipgap for all PH scenario sub-problems",
                     action="store",
                     dest="scenario_mipgap",
                     type="float",
                     default=None)
   parser.add_option('-k',"--keep-solver-files",
                     help="Retain temporary input and output files for scenario sub-problem solves",
                     action="store_true",
                     dest="keep_solver_files",
                     default=False)
   parser.add_option("--output-solver-logs",
                     help="Output solver logs during scenario sub-problem solves",
                     action="store_true",
                     dest="output_solver_logs",
                     default=False)
   parser.add_option("--output-solver-results",
                     help="Output solutions obtained after each scenario sub-problem solve",
                     action="store_true",
                     dest="output_solver_results",
                     default=False)
   parser.add_option("--output-times",
                     help="Output timing statistics for various PH components",
                     action="store_true",
                     dest="output_times",
                     default=False)
   parser.add_option("--disable-warmstarts",
                     help="Disable warm-start of scenario sub-problem solves in PH iterations >= 1. Default is False.",
                     action="store_true",
                     dest="disable_warmstarts",
                     default=False)
   parser.add_option("--profile",
                     help="Enable profiling of Python code.  The value of this option is the number of functions that are summarized.",
                     action="store",
                     dest="profile",
                     type="int",
                     default=0)
   parser.add_option("--disable-gc",
                     help="Disable the python garbage collecter. Default is False.",
                     action="store_true",
                     dest="disable_gc",
                     default=False)

   parser.usage=usage_string

   return parser

#
# Create the reference model / instance and scenario tree instance for PH.
#

def load_reference_and_scenario_models(options):

   #
   # create and populate the reference model/instance pair.
   #

   reference_model = None
   reference_instance = None

   try:
      reference_model_filename = os.path.expanduser(options.model_directory)+os.sep+"ReferenceModel.py"
      if options.verbose is True:
         print "Scenario reference model filename="+reference_model_filename
      model_import = import_file(reference_model_filename)
      if "model" not in dir(model_import):
         print ""
         print "***ERROR: Exiting test driver: No 'model' object created in module "+reference_model_filename
         return None, None, None, None

      if model_import.model is None:
         print ""
         print "***ERROR: Exiting test driver: 'model' object equals 'None' in module "+reference_model_filename
         return None, None, None, None

      reference_model = model_import.model
   except IOError:
      print "***ERROR: Failed to load scenario reference model from file="+reference_model_filename
      return None, None, None, None

   try:
      reference_instance_filename = os.path.expanduser(options.instance_directory)+os.sep+"ReferenceModel.dat"
      if options.verbose is True:
         print "Scenario reference instance filename="+reference_instance_filename
      reference_instance = reference_model.create(reference_instance_filename)
   except IOError:
      print "***ERROR: Failed to load scenario reference instance data from file="+reference_instance_filename
      return None, None, None, None

   #
   # create and populate the scenario tree model
   #

   from coopr.pysp.util.scenariomodels import scenario_tree_model
   scenario_tree_instance = None

   try:
      scenario_tree_instance_filename = os.path.expanduser(options.instance_directory)+os.sep+"ScenarioStructure.dat"
      if options.verbose is True:
         print "Scenario tree instance filename="+scenario_tree_instance_filename
      scenario_tree_instance = scenario_tree_model.create(scenario_tree_instance_filename)
   except IOError:
      print "***ERROR: Failed to load scenario tree reference instance data from file="+scenario_tree_instance_filename
      return None, None, None

   #
   # construct the scenario tree
   #
   scenario_tree = ScenarioTree(scenarioinstance=reference_instance,
                                scenariotreeinstance=scenario_tree_instance)

   return reference_model, reference_instance, scenario_tree, scenario_tree_instance

#
# Execute the PH solver server daemon.
#

def run_server(options, scenario_instances, solver, scenario_tree):

   start_time = time.time()

   Pyro.core.initServer(banner=0)

   locator = Pyro.naming.NameServerLocator()
   ns = None
   try:
      ns = locator.getNS()
   except Pyro.errors.NamingError:
      raise RuntimeError, "PH solver server failed to locate Pyro name server"

   solver_daemon = Pyro.core.Daemon()
   solver_daemon.useNameServer(ns)

   daemon_object = PHSolverServer(scenario_instances, solver, scenario_tree)
   delegator_object = Pyro.core.ObjBase()
   delegator_object.delegateTo(daemon_object)

   # register an entry in the nameserver for
   # each scenario processed by this daemon.
   for scenario_name, scenario_instance in scenario_instances.items():
      # first, see if it's already registered - if no, cull the old entry.
      # NOTE: This is a hack, as the cleanup / disconnect code doesn't
      #       seem to be invoked when the daemon is killed.
      try:
         ns.unregister(scenario_name)
      except NamingError:
         pass

      try:
         solver_daemon.connect(delegator_object, scenario_name)
      except Pyro.errors.NamingError:
         raise RuntimeError, "Entry in name server already exists for scenario="+scenario_name

   try:
      solver_daemon.requestLoop()
   except KeyboardInterrupt, SystemExit:
      pass

   solver_daemon.disconnect(delegator_object)
   solver_daemon.shutdown()

   end_time = time.time()

#
# The main daemon initialization / runner routine.
#

def exec_server(options):

   # we need the base model (not so much the reference instance, but that
   # can't hurt too much - until proven otherwise, that is) to construct
   # the scenarios that this server is responsible for.
   reference_model, reference_instance, scenario_tree, scenario_tree_instance = load_reference_and_scenario_models(options)
   if reference_model is None or reference_instance is None or scenario_tree is None:
      print "***Unable to launch PH solver server"
      return

   # construct the set of scenario instances based on the command-line.
   scenario_instances = {}
   if (options.all_scenarios is True) and (len(options.scenarios) > 0):
      print "***WARNING: Both individual scenarios and all-scenarios were specified on the command-line; proceeding using all scenarios"

   if (len(options.scenarios) == 0) and (options.all_scenarios is False):
      print "***Unable to launch PH solver server - no scenario(s) specified!"
      return

   scenarios_to_construct = []
   if options.all_scenarios is True:
      scenarios_to_construct.extend(scenario_tree._scenario_map.keys())
   else:
      scenarios_to_construct.extend(options.scenarios)

   for scenario_name in scenarios_to_construct:
      print "Creating instance for scenario="+scenario_name
      if scenario_tree.contains_scenario(scenario_name) is False:
         print "***Unable to launch PH solver server - unknown scenario specified with name="+scenario_name
         return

      # create the baseline scenario instance
      scenario_instance = construct_scenario_instance(scenario_tree,
                                                      options.instance_directory,
                                                      scenario_name,
                                                      reference_model,
                                                      options.verbose)
      if scenario_instance is None:
         print "***Unable to launch PH solver server - failed to create instance for scenario="+scenario_name
         return

      # augment the instance with PH-specific parameters (weights, rhos, etc).
      # TBD: The default rho of 1.0 is kind of bogus. Need to somehow propagate
      #      this value and the linearization parameter as a command-line argument.
      new_penalty_variable_names = create_ph_parameters(scenario_instance, scenario_tree, 1.0, False)

      scenario_instances[scenario_name] = scenario_instance

   # the solver instance is persistent, applicable to all instances here.
   if options.verbose is True:
      print "Constructing solver type="+options.solver_type
   solver = SolverFactory(options.solver_type)
   if solver == None:
      raise ValueError, "Unknown solver type=" + options.solver_type + " specified"
   if options.keep_solver_files is True:
      solver.keepFiles = True
   if len(options.scenario_solver_options) > 0:
      if options.verbose is True:
         print "Initializing scenario sub-problem solver with options="+str(options.scenario_solver_options)
      solver.set_options("".join(options.scenario_solver_options))
   if options.output_times is True:
      solver._report_timing = True

   # spawn the daemon.
   run_server(options, scenario_instances, solver, scenario_tree)

def run(args=None):

    #
    # Top-level command that executes the ph solver server daemon.
    # This is segregated from phsolverserver to faciliate profiling.
    #

    #
    # Parse command-line options.
    #
    try:
       options_parser = construct_options_parser("phsolverserver [options]")
       (options, args) = options_parser.parse_args(args=args)
    except SystemExit:
       # the parser throws a system exit if "-h" is specified - catch
       # it to exit gracefully.
       return

    # for a one-pass execution, garbage collection doesn't make
    # much sense - so it is disabled by default. Because: It drops
    # the run-time by a factor of 3-4 on bigger instances.
    if options.disable_gc is True:
       gc.disable()
    else:
       gc.enable()

    if options.profile > 0:
        #
        # Call the main PH routine with profiling.
        #
        tfile = TempfileManager.create_tempfile(suffix=".profile")
        tmp = profile.runctx('exec_ph(options)',globals(),locals(),tfile)
        p = pstats.Stats(tfile).strip_dirs()
        p.sort_stats('time', 'cum')
        p = p.print_stats(options.profile)
        p.print_callers(options.profile)
        p.print_callees(options.profile)
        p = p.sort_stats('cum','calls')
        p.print_stats(options.profile)
        p.print_callers(options.profile)
        p.print_callees(options.profile)
        p = p.sort_stats('calls')
        p.print_stats(options.profile)
        p.print_callers(options.profile)
        p.print_callees(options.profile)
        TempfileManager.clear_tempfiles()
        ans = [tmp, None]
    else:
        #
        # Call the main PH routine without profiling.
        #
        ans = exec_server(options)

    gc.enable()

    return ans

def main():
    try:
        run()
    except IOError, str:
        print "IO ERROR:"
        print str
    except pyutilib.common.ApplicationError, str:
        print "APPLICATION ERROR:"
        print str
    except RuntimeError, str:
        print "RUN-TIME ERROR:"
        print str
    except:
        print "Encountered unhandled exception"
        traceback.print_exc()

