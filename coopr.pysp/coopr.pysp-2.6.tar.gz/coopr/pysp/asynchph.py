#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

import sys
import pyutilib.component.core
import types
from coopr.pyomo import *
import copy
import os.path
import traceback
import copy
from coopr.opt import SolverResults,SolverStatus
from coopr.opt.base import SolverFactory
from coopr.opt.parallel import SolverManagerFactory
import time
import types

from scenariotree import *
from phutils import *

from pyutilib.component.core import ExtensionPoint

from coopr.pysp.phextension import IPHExtension

class AsyncProgressiveHedging(object):

   #
   # a utility intended for folks who are brave enough to script rho setting in a python file.
   #

   def setRhoAllScenarios(self, variable_value, rho_expression):

      variable_name = None
      variable_index = None

      if isVariableNameIndexed(variable_value.name) is True:

         variable_name, variable_index = extractVariableNameAndIndex(variable_value.name)

      else:

         variable_name = variable_value.name
         variable_index = None
      
      new_rho_value = rho_expression()

      if self._verbose is True:
         print "Setting rho="+str(new_rho_value)+" for variable="+variable_value.name

      for instance_name, instance in self._instances.items():

         rho_param = getattr(instance, "PHRHO_"+variable_name)
         rho_param[variable_index] = new_rho_value

   #
   # a simple utility to count the number of continuous and discrete variables in a set of instances.
   # unused variables are ignored, and counts include all active indices. returns a pair - num-discrete,
   # num-continuous.
   #

   def compute_variable_counts(self):

      num_continuous_vars = 0
      num_discrete_vars = 0
      
      for stage in self._scenario_tree._stages:
         
         if stage != self._scenario_tree._stages[-1]: # no blending over the final stage
            
            for tree_node in stage._tree_nodes:

               for (variable, index_template, variable_indices) in stage._variables:

                  variable_name = variable.name

                  variable_type = variable.domain

                  for index in variable_indices:

                     # determine if this index is used - otherwise, don't waste time
                     # fixing and cycle checking. for one, the code will crash :-) with
                     # None values during the cycle checking computation!

                     is_used = True # until proven otherwise                     
                     for scenario in tree_node._scenarios:
                        instance = self._instances[scenario._name]
                        if getattr(instance,variable_name)[index].status == VarStatus.unused:
                           is_used = False

                     if is_used is True:                        

                        # JPW TBD: ideally, we want an "is-discrete" check in the logic below, which COOPR doesn't currently support.
                        if isinstance(variable_type, IntegerSet) or isinstance(variable_type, BooleanSet):
                           num_discrete_vars = num_discrete_vars + 1
                        else:
                           num_continuous_vars = num_continuous_vars + 1

      return (num_discrete_vars, num_continuous_vars)

   """ Constructor
       Arguments:
          max_iterations        the maximum number of iterations to run PH (>= 0). defaults to 0.
          rho                   the global rho value (> 0). defaults to 0.
          rho_setter            an optional name of a python file used to set particular variable rho values.
          solver                the solver type that PH uses to solve scenario sub-problems. defaults to "cplex".
          solver_manager        the solver manager type that coordinates scenario sub-problem solves. defaults to "serial".
          keep_solver_files     do I keep intermediate solver files around (for debugging)? defaults to False.
          output_solver_log     do I dump the solver log (as it is being generated) to the screen? defaults to False.
          output_solver_results do I output (for debugging) the detailed solver results, including solutions, for scenario solves? defaults to False.
          verbose               does the PH object stream debug/status output? defaults to False.
          output_times          do I output timing statistics? defaults to False (e.g., useful in the case where you want to regression test against baseline output).

   """
   def __init__(self, *args, **kwds):

      # PH configuration parameters
      # TBD - shift rho to a parameter of the instances (probably keep it here, and in the model)
      self._rho = 0.0 # TBD morph to per-variable later, and possibly per-variable, per-scenario.
      self._rho_setter = None # filename for the modeler to set rho.
      self._max_iterations = 0

      # PH reporting parameters
      self._verbose = False # do I flood the screen with status output?
      self._output_continuous_variable_stats = True # when in verbose mode, do I output weights/averages for continuous variables?
      self._output_solver_results = False
      self._output_times = False

      # PH run-time variables
      self._current_iteration = 0 # the 'k'
      self._xbar = {} # current per-variable averages. maps (node_id, variable_name) -> value
      self._initialized = False # am I ready to call "solve"? Set to True by the initialize() method.

      # PH solver information / objects.
      self._solver_type = "cplex"
      self._solver_manager_type = "pyro" # only pyro makes sense for async currently.
      
      self._solver = None # will eventually be unnecessary once Bill eliminates the need for a solver in the solver manager constructor.
      self._solver_manager = None 
      
      self._keep_solver_files = False
      self._output_solver_log = False

      # PH convergence computer/updater.
      self._converger = None

      # PH history
      self._solutions = {}

      # all information related to the scenario tree (implicit and explicit).
      self._model = None # not instantiated
      self._model_instance = None # instantiated

      self._scenario_tree = None
      
      self._scenario_data_directory = "" # this the prefix for all scenario data
      self._instances = {} # maps scenario name to the corresponding model instance

      # for various reasons (mainly hacks at this point), it's good to know whether we're minimizing or maximizing.
      self._is_minimizing = None

      # global handle to ph extension plugin
      self._ph_plugin = ExtensionPoint(IPHExtension)

      # PH timing statistics - relative to last invocation.
      self._init_start_time = None # for initialization() method
      self._init_end_time = None
      self._solve_start_time = None # for solve() method
      self._solve_end_time = None
      self._cumulative_solve_time = None # seconds, over course of solve()
      self._cumulative_xbar_time = None # seconds, over course of update_xbars()
      self._cumulative_weight_time = None # seconds, over course of update_weights()

      # PH default tolerances - for use in fixing and testing equality across scenarios,
      # and other stuff.
      self._integer_tolerance = 0.00001

      # process the keyword options
      for key in kwds.keys():
         if key == "max_iterations":
            self._max_iterations = kwds[key]
         elif key == "rho":
            self._rho = kwds[key]
         elif key == "rho_setter":
            self._rho_setter = kwds[key]            
         elif key == "solver":
            self._solver_type = kwds[key]
         elif key == "solver_manager":
            self._solver_manager_type = kwds[key]            
         elif key == "keep_solver_files":
            self._keep_solver_files = kwds[key]
         elif key == "output_solver_results":
            self._output_solver_results = kwds[key]
         elif key == "output_solver_log":
            self._output_solver_log = kwds[key]
         elif key == "verbose":
            self._verbose = kwds[key]
         elif key == "output_times":
            self._output_times = kwds[key]            
         else:
            print "Unknown option=" + key + " specified in call to PH constructor"

      # validate all "atomic" options (those that can be validated independently)
      if self._max_iterations < 0:
         raise ValueError, "Maximum number of PH iterations must be non-negative; value specified=" + `self._max_iterations`
      if self._rho <= 0.0:
         raise ValueError, "Value of rho paramter in PH must be non-zero positive; value specified=" + `self._rho`

      # validate rho setter file if specified.
      if self._rho_setter is not None:
         if os.path.exists(self._rho_setter) is False:
            raise ValueError, "The rho setter script file="+self._rho_setter+" does not exist"

      # construct the sub-problem solver.
      self._solver = SolverFactory(self._solver_type)
      if self._solver == None:
         raise ValueError, "Unknown solver type=" + self._solver_type + " specified in call to PH constructor"
      if self._keep_solver_files is True:
         # TBD - this is a bit kludgy, as it requires PH to know/assume that
         #       it is dealing with a system call solver. the solver factory should take keyword options as a fix.
         self._solver.keepFiles = True

      # construct the solver manager.
      if self._solver_manager_type != "pyro":
         raise ValueError, "Only the pyro solver manager makes sense for asynch PH!"
      print "SOLVER MANAGER TYPE=",self._solver_manager_type
      self._solver_manager = SolverManagerFactory(self._solver_manager_type)
      if self._solver_manager is None:
         raise ValueError, "Failed to create solver manager of type="+self._solver_manager_type+" specified in call to PH constructor"

      # a set of all valid PH iteration indicies is generally useful for plug-ins, so create it here.
      self._iteration_index_set = Set(name="PHIterations")
      for i in range(0,self._max_iterations + 1):
         self._iteration_index_set.add(i)      

      # spit out parameterization if verbosity is enabled
      if self._verbose == True:
         print "PH solver configuration: "
         print "   Max iterations=" + `self._max_iterations`
         print "   Rho=" + `self._rho`
         print "   Sub-problem solver type=" + `self._solver_type`

   """ Initialize PH with model and scenario data, in preparation for solve().
       Constructs and reads instances.
   """
   def initialize(self, scenario_data_directory_name=".", model=None, model_instance=None, scenario_tree=None, converger=None):

      self._init_start_time = time.time()

      if self._verbose == True:
         print "Initializing PH"
         print "   Scenario data directory=" + scenario_data_directory_name

      if not os.path.exists(scenario_data_directory_name):
         raise ValueError, "Scenario data directory=" + scenario_data_directory_name + " either does not exist or cannot be read"

      self._scenario_data_directory_name = scenario_data_directory_name

      # IMPT: The input model should be an *instance*, as it is very useful (critical!) to know
      #       the dimensions of sets, be able to store suffixes on variable values, etc.
      # TBD: There may be a way to see if a model is initialized - throw an exception if it is not!
      if model is None:
         raise ValueError, "A model must be supplied to the PH initialize() method"

      if scenario_tree is None:
         raise ValueError, "A scenario tree must be supplied to the PH initialize() method"

      if converger is None:
         raise ValueError, "A convergence computer must be supplied to the PH initialize() method"

      self._model = model
      self._model_instance = model_instance
      self._scenario_tree = scenario_tree
      self._converger = converger

      model_objective = model.active_components(Objective)
      self._is_minimizing = (model_objective[ model_objective.keys()[0] ].sense == minimize)

      self._converger.reset()

      # construct instances for each scenario
      if self._verbose is True:
         if self._scenario_tree._scenario_based_data == 1:
            print "Scenario-based instance initialization enabled"
         else:
            print "Node-based instance initialization enabled"
         
      for scenario in self._scenario_tree._scenarios:

         scenario_instance = None

         if self._verbose is True:
            print "Creating instance for scenario=" + scenario._name

         try:
            if self._scenario_tree._scenario_based_data == 1:
               scenario_data_filename = self._scenario_data_directory_name + os.sep + scenario._name + ".dat"
               if self._verbose is True:
                  print "Data for scenario=" + scenario._name + " loads from file=" + scenario_data_filename
               scenario_instance = (self._model).create(scenario_data_filename)
            else:
               scenario_instance = self._model.clone()
               scenario_data = ModelData()
               current_node = scenario._leaf_node
               while current_node is not None:
                  node_data_filename = self._scenario_data_directory_name + os.sep + current_node._name + ".dat"
                  if self._verbose is True:
                     print "Node data for scenario=" + scenario._name + " partially loading from file=" + node_data_filename
                  scenario_data.add_data_file(node_data_filename)
                  current_node = current_node._parent
               scenario_data.read(model=scenario_instance)
               scenario_instance.load(scenario_data)
               scenario_instance.preprocess()
         except:
            print "Encountered exception in model instance creation - traceback:"
            traceback.print_exc()
            raise RuntimeError, "Failed to create model instance for scenario=" + scenario._name

         self._instances[scenario._name] = scenario_instance
         self._instances[scenario._name].name = scenario._name

      if self._verbose is True:
         print "PH successfully created model instances for all scenarios"

      # TBD - Technically, we don't need to add these parameters to the models until after the iteration 0 solve (move later).

      # create PH weight and xbar vectors, on a per-scenario basis, for each variable that is not in the 
      # final stage, i.e., for all variables that are being blended by PH. the parameters are created
      # in the space of each scenario instance, so that they can be directly and automatically
      # incorporated into the (appropriately modified) objective function.

      if self._verbose is True:
         print "Creating weight, average, and rho parameter vectors for scenario instances"

      for (instance_name, instance) in self._instances.items():

         # first, gather all unique variables referenced in any stage
         # other than the last, independent of specific indices. this
         # "gather" step is currently required because we're being lazy
         # in terms of index management in the scenario tree - which
         # should really be done in terms of sets of indices.
         # NOTE: technically, the "instance variables" aren't really references
         # to the variable in the instance - instead, the reference model. this
         # isn't an issue now, but it could easily become one (esp. in avoiding deep copies).
         instance_variables = {}
         
         for stage in self._scenario_tree._stages:
            
            if stage != self._scenario_tree._stages[-1]:
               
               for (reference_variable, index_template, reference_indices) in stage._variables:
                  
                  if reference_variable.name not in instance_variables.keys():
                     
                     instance_variables[reference_variable.name] = reference_variable

         # for each blended variable, create a corresponding ph weight and average parameter in the instance.
         # this is a bit wasteful, in terms of indices that might appear in the last stage, but that is minor
         # in the grand scheme of things.

         for (variable_name, reference_variable) in instance_variables.items():

            new_w_index = reference_variable._index # TBD - need to be careful with the shallow copy here
            new_w_parameter_name = "PHWEIGHT_"+reference_variable.name
            new_w_parameter = Param(new_w_index, name=new_w_parameter_name)
            setattr(instance,new_w_parameter_name,new_w_parameter)

            # if you don't explicitly assign values to each index, the entry isn't created - instead, when you reference
            # the parameter that hasn't been explicitly assigned, you just get the default value as a constant. I'm not
            # sure if this has to do with the model output, or the function of the model, but I'm doing this to avoid the
            # issue in any case for now.
            for index in new_w_index:
               new_w_parameter[index] = 0.0

            new_avg_index = reference_variable._index # TBD - need to be careful with the shallow copy here
            new_avg_parameter_name = "PHAVG_"+reference_variable.name
            new_avg_parameter = Param(new_avg_index, name=new_avg_parameter_name)
            setattr(instance,new_avg_parameter_name,new_avg_parameter)

            for index in new_avg_index:
               new_avg_parameter[index] = 0.0

            new_rho_index = reference_variable._index # TBD - need to be careful with the shallow copy here
            new_rho_parameter_name = "PHRHO_"+reference_variable.name
            new_rho_parameter = Param(new_rho_index, name=new_rho_parameter_name)
            setattr(instance,new_rho_parameter_name,new_rho_parameter)

            for index in new_rho_index:
               new_rho_parameter[index] = self._rho

      # if specified, run the user script to initialize variable rhos at their whim.
      if self._rho_setter is not None:

         print "Executing user rho set script from filename=", self._rho_setter
         execfile(self._rho_setter)

      # create parameters to store variable statistics (of general utility) at each node in the scenario tree.

      if self._verbose is True:
         print "Creating variable statistic (min/avg/max) parameter vectors for scenario tree nodes"

      for stage in self._scenario_tree._stages:
         if stage != self._scenario_tree._stages[-1]:

            # first, gather all unique variables referenced in this stage
            # this "gather" step is currently required because we're being lazy
            # in terms of index management in the scenario tree - which
            # should really be done in terms of sets of indices.
            stage_variables = {}
            for (reference_variable, index_template, reference_index) in stage._variables:
               if reference_variable.name not in stage_variables.keys():
                  stage_variables[reference_variable.name] = reference_variable

            # next, create min/avg/max parameters for each variable in the corresponding tree node.
            # NOTE: the parameter names below could really be empty, as they are never referenced
            #       explicitly.
            for (variable_name, reference_variable) in stage_variables.items():
               for tree_node in stage._tree_nodes:

                  new_min_index = reference_variable._index # TBD - need to be careful with the shallow copy here (and below)
                  new_min_parameter_name = "NODEMIN_"+reference_variable.name
                  new_min_parameter = Param(new_min_index, name=new_min_parameter_name)
                  for index in new_min_index:
                     new_min_parameter[index] = 0.0
                  tree_node._minimums[reference_variable.name] = new_min_parameter                                    

                  new_avg_index = reference_variable._index 
                  new_avg_parameter_name = "NODEAVG_"+reference_variable.name
                  new_avg_parameter = Param(new_avg_index, name=new_avg_parameter_name)
                  for index in new_avg_index:
                     new_avg_parameter[index] = 0.0
                  tree_node._averages[reference_variable.name] = new_avg_parameter

                  new_max_index = reference_variable._index 
                  new_max_parameter_name = "NODEMAX_"+reference_variable.name
                  new_max_parameter = Param(new_max_index, name=new_max_parameter_name)
                  for index in new_max_index:
                     new_max_parameter[index] = 0.0
                  tree_node._maximums[reference_variable.name] = new_max_parameter                                                      


      # indicate that we're ready to run.
      self._initialized = True

      self._init_end_time = time.time()

      if self._verbose is True:
         print "PH is successfully initialized"
         if self._output_times is True:
            print "Initialization time=" + str(self._init_end_time - self._init_start_time) + " seconds"

      # let plugins know if they care.
      if len(self._ph_plugin) == 1:
         self._ph_plugin.service().post_ph_initialization(self)

   """ Perform the non-weighted scenario solves and form the initial w and xbars.
   """   
   def iteration_0_solve(self):

      if self._verbose == True:
         print "------------------------------------------------"
         print "Starting PH iteration 0 solves"

      self._current_iteration = 0

      solve_start_time = time.time()                     

      # STEP 1: queue up the solves for all scenario sub-problems.
      #         grab all the action handles for the subsequent barrier sync.

      action_handles = []
      action_handle_instance_map = {} 

      for scenario in self._scenario_tree._scenarios:
         
         instance = self._instances[scenario._name]
         
         if self._verbose == True:
            print "Queuing solve for scenario=" + scenario._name
            
         # TBD - need to have the solver be able to solve a particular instance, with a specific objective

         # there's nothing to warm-start from in iteration 0.
         new_action_handle = self._solver_manager.queue(instance, opt=self._solver, warmstart=False, tee=self._output_solver_log)

         action_handle_instance_map[scenario._name] = new_action_handle

         action_handles.append(new_action_handle)

      # STEP 2: barrier sync for all scenario sub-problem solves.
      print "Waiting for scenario sub-problem solves"
      self._solver_manager.wait_all(action_handles)

      solve_end_time = time.time()
      self._cumulative_solve_time += (solve_end_time - solve_start_time)

      # STEP 3: Load the results!
      for scenario_name, action_handle in action_handle_instance_map.items():

         instance = self._instances[scenario_name]
         results = self._solver_manager.get_results(action_handle)

         if len(results.solution) == 0:
            raise RuntimeError, "Solve failed for scenario="+scenario._name+"; no solutions generated"

         if self._verbose is True:         
            print "Solve completed successfully"

#         if self._output_times is True:
#            print "Solve time=%8.2f" % (solve_end_time - solve_start_time)

#         if self._output_solver_results == True:
         print "Results:"
         results.write(num=1)            

         instance.load(results)

         if self._verbose == True:                  
            print "Successfully loaded solution"

      # TBD - save the solutions for history tracking

      if self._verbose == True:
         print "Successfully completed PH iteration 0 solves"
         print "         Scenario              Objective                  Value"
         for scenario in self._scenario_tree._scenarios:
            instance = self._instances[scenario._name]
            for objective_name in instance.active_components(Objective):
               objective = instance.active_components(Objective)[objective_name]
               # TBD: I don't know how to deal with objective arrays, so I'll assume they aren't there
               print "%20s       %15s     %14.4f" % (scenario._name, objective.name, objective._data[None].expr())
         print "------------------------------------------------"
         print ""

   #
   # recompute the averages, minimum, and maximum statistics for all variables to be blended by PH, i.e.,
   # not appearing in the final stage. technically speaking, the min/max aren't required by PH, but they
   # are used often enough to warrant their computation and it's basically free if you're computing the
   # average.
   #
   def update_variable_statistics(self):

      start_time = time.time()
      
      for stage in self._scenario_tree._stages:
         
         if stage != self._scenario_tree._stages[-1]: # no blending over the final stage
            
            for tree_node in stage._tree_nodes:
               
               for (variable, index_template, variable_indices) in stage._variables:
                  
                  variable_name = variable.name
                     
                  avg_parameter_name = "PHAVG_"+variable_name
                  
                  for index in variable_indices:
                     min = float("inf")
                     avg = 0.0
                     max = float("-inf")
                     node_probability = 0.0
                     
                     is_used = True # until proven otherwise                     
                     for scenario in tree_node._scenarios:
                        
                        instance = self._instances[scenario._name]
                        
                        if getattr(instance,variable_name)[index].status == VarStatus.unused:
                           is_used = False
                        else:
                           node_probability += scenario._probability
                           var_value = getattr(instance, variable.name)[index].value
                           if var_value < min:
                              min = var_value
                           avg += (scenario._probability * var_value)
                           if var_value > max:
                              max = var_value

                     if is_used is True:
                        tree_node._minimums[variable.name][index] = min
                        tree_node._averages[variable.name][index] = avg / node_probability
                        tree_node._maximums[variable.name][index] = max                        

                        # distribute the newly computed average to the xbar variable in
                        # each instance/scenario associated with this node. only do this
                        # if the variable is used!
                        for scenario in tree_node._scenarios:
                           instance = self._instances[scenario._name]
                           avg_parameter = getattr(instance, avg_parameter_name)
                           avg_parameter[index] = avg / node_probability

      end_time = time.time()
      self._cumulative_xbar_time += (end_time - start_time)

   def update_weights(self):

      # because the weight updates rely on the xbars, and the xbars are node-based,
      # I'm looping over the tree nodes and pushing weights into the corresponding scenarios.
      start_time = time.time()      

      for stage in self._scenario_tree._stages:
         
         if stage != self._scenario_tree._stages[-1]: # no blending over the final stage, so no weights to worry about.
            
            for tree_node in stage._tree_nodes:

               for (variable, index_template, variable_indices) in stage._variables:

                  variable_name = variable.name
                     
                  weight_parameter_name = "PHWEIGHT_"+variable_name

                  for index in variable_indices:

                     tree_node_average = value(tree_node._averages[variable.name][index])

                     for scenario in tree_node._scenarios:

                        instance = self._instances[scenario._name]
                        
                        if getattr(instance,variable.name)[index].status != VarStatus.unused:

                           current_variable_weight = value(getattr(instance, weight_parameter_name)[index])
                           # if I'm maximizing, invert value prior to adding (hack to implement negatives)
                           if self._is_minimizing is False:
                              current_variable_weight = (-current_variable_weight)
                           current_variable_value = getattr(instance,variable.name)[index].value
                           new_variable_weight = current_variable_weight + self._rho * (current_variable_value - tree_node_average)
                           # I have the correct updated value, so now invert if maximizing.
                           if self._is_minimizing is False:
                              new_variable_weight = (-new_variable_weight)
                           getattr(instance, weight_parameter_name)[index] = new_variable_weight

      end_time = time.time()
      self._cumulative_weight_time += (end_time - start_time)

   def update_scenario_weights(self, instance):

      # because the weight updates rely on the xbars, and the xbars are node-based,
      # I'm looping over the tree nodes and pushing weights into the corresponding scenarios.
      start_time = time.time()      

      for stage in self._scenario_tree._stages:
         
         if stage != self._scenario_tree._stages[-1]: # no blending over the final stage, so no weights to worry about.
            
            for tree_node in stage._tree_nodes:

               for (variable, index_template, variable_indices) in stage._variables:

                  variable_name = variable.name
                     
                  weight_parameter_name = "PHWEIGHT_"+variable_name

                  for index in variable_indices:

                     tree_node_average = value(tree_node._averages[variable.name][index])

                     if getattr(instance,variable.name)[index].status != VarStatus.unused:

                        current_variable_weight = value(getattr(instance, weight_parameter_name)[index])
                        # if I'm maximizing, invert value prior to adding (hack to implement negatives)
                        if self._is_minimizing is False:
                           current_variable_weight = (-current_variable_weight)
                        current_variable_value = getattr(instance,variable.name)[index].value
                        new_variable_weight = current_variable_weight + self._rho * (current_variable_value - tree_node_average)
                        # I have the correct updated value, so now invert if maximizing.
                        if self._is_minimizing is False:
                           new_variable_weight = (-new_variable_weight)
                        getattr(instance, weight_parameter_name)[index] = new_variable_weight

      end_time = time.time()
      self._cumulative_weight_time += (end_time - start_time)      

   def form_iteration_k_objectives(self):

      if self._verbose == True:
         print "Forming PH-weighted objective"

      # for each blended variable (i.e., those not appearing in the final stage),
      # add the linear and quadratic penalty terms to the objective.
      for instance_name, instance in self._instances.items():
         
         objective_name = instance.active_components(Objective).keys()[0]         
         objective = instance.active_components(Objective)[objective_name]         
         objective_expression = objective._data[None].expr # TBD: we don't deal with indexed expressions (not even sure how to interpret them)
         # the quadratic expression is really treated as just a list - eventually should be treated as a full expression.
         quad_expression = 0.0
         
         for stage in self._scenario_tree._stages:

            # skip the last stage, as no blending occurs
            if stage != self._scenario_tree._stages[-1]:
               # find the instance objective.
               # TBD - for simiplicity, I'm assuming a single objective - we should select "active" objectives later.
               #       also, can create a quadratic objective and leave the original alone.

               for (reference_variable, index_template, variable_indices) in stage._variables:

                  variable_name = reference_variable.name

                  w_parameter_name = "PHWEIGHT_"+variable_name
                  w_parameter = instance.active_components(Param)[w_parameter_name]
                  
                  average_parameter_name = "PHAVG_"+variable_name
                  average_parameter = instance.active_components(Param)[average_parameter_name]

                  rho_parameter_name = "PHRHO_"+variable_name
                  rho_parameter = instance.active_components(Param)[rho_parameter_name]

                  for index in variable_indices:

                     instance_variable = instance.active_components(Var)[variable_name][index]
                     
                     if (instance_variable.status is not VarStatus.unused) and (instance_variable.fixed is False):
                        
                        # TBD - if maximizing, here is where you would want "-=" - however, if you do this, the collect process chokes.
                        objective_expression += (w_parameter[index] * instance_variable)
                        quad_expression += (rho_parameter[index] * (instance_variable - average_parameter[index]) ** 2)

         # strictly speaking, this probably isn't necessary - parameter coefficients won't get
         # pre-processed out of the expression tree. however, if the under-the-hood should change,
         # we'll be covered.
         instance.active_components(Objective)[objective_name]._data[None].expr = objective_expression
         instance.active_components(Objective)[objective_name]._quad_subexpr = quad_expression

   def iteration_k_plus_solves(self):

     if self._verbose == True:
        print "Starting PH iteration k+ solves"

     # things progress at different rates - keep track of what's going on.
     scenario_ks = {}
     for scenario in self._scenario_tree._scenarios:
        scenario_ks[scenario._name]=0

     # keep track of action handles mapping to scenarios.
     action_handle_instance_map = {}        

     # STEP 1: queue up the solves for all scenario sub-problems.

     for scenario in self._scenario_tree._scenarios:     

        instance = self._instances[scenario._name]

        if self._verbose == True:
           print "Queuing solve for scenario=" + scenario._name

        # IMPT: You have to re-presolve, as the simple presolver collects the linear terms together. If you
        # don't do this, you won't see any chance in the output files as you vary the problem parameters!
        # ditto for instance fixing!
        instance.preprocess()

        # once past iteration 0, there is always a feasible solution from which to warm-start.
        new_action_handle = self._solver_manager.queue(instance, opt=self._solver, warmstart=True, tee=self._output_solver_log)

        action_handle_instance_map[new_action_handle] = scenario._name

     # STEP 2: wait for the first action handle to return, process it, and keep chugging.

     while(True):

        this_action_handle = self._solver_manager.wait_any()
        scenario_name = action_handle_instance_map[this_action_handle]

        scenario_ks[scenario_name] += 1

        print "SOLVE FOR SCENARIO=",scenario_name," COMPLETED - NEW SOLVE COUNT=", scenario_ks[scenario_name]        

        instance = self._instances[scenario_name]
        results = self._solver_manager.get_results(this_action_handle)
        
        if len(results.solution) == 0:
           raise RuntimeError, "Solve failed for scenario="+scenario_name+"; no solutions generated"

        if self._verbose is True:         
           print "Solve completed successfully"

        if self._output_solver_results == True:
           print "Results:"
           results.write(num=1)            

        instance.load(results)

        if self._verbose == True:                  
           print "Successfully loaded solution"

        # we're assuming there is a single solution.
        # the "value" attribute is a pre-defined feature of any solution - it is relative to whatever
        # objective was selected during optimization, which of course should be the PH objective.
        ph_objective_value = float(results.solution(0).value)

        if self._verbose == True:
           for objective_name in instance.active_components(Objective):
              objective = instance.active_components(Objective)[objective_name]
              print "%20s       %18.4f     %14.4f" % (scenario_name, ph_objective_value, 0.0)

        # update variable statistics prior to any output.
        self.update_variable_statistics()
        self.update_scenario_weights(instance)

        print "Variable averages and weights prior to scenario solves:"
        self.pprint(True,True,False)        

        # see if we've converged.
        all_good = True
        for scenario in self._scenario_tree._scenarios:     
           instance = self._instances[scenario._name]
           if scenario_ks[scenario._name] < self._max_iterations:
              all_good = False
              break
        if all_good is True:
           return

        if scenario_ks[scenario_name] < self._max_iterations:

           # IMPT: You have to re-presolve, as the simple presolver collects the linear terms together. If you
           # don't do this, you won't see any chance in the output files as you vary the problem parameters!
           # ditto for instance fixing!
           instance.preprocess()

           # once past iteration 0, there is always a feasible solution from which to warm-start.
           new_action_handle = self._solver_manager.queue(instance, opt=self._solver, warmstart=True, tee=self._output_solver_log)

           action_handle_instance_map[new_action_handle] = scenario_name

           print "Queued up solve k=",str(scenario_ks[scenario_name]+1)," for scenario=",scenario_name

        print "Variable values following scenario solve:"
        self.pprint(False,False,True)           

   def solve(self):

      self._solve_start_time = time.time()
      self._cumulative_solve_time = 0.0
      self._cumulative_xbar_time = 0.0
      self._cumulative_weight_time = 0.0

      print "Starting PH"

      if self._initialized == False:
         raise RuntimeError, "PH is not initialized - cannot invoke solve() method"

      print "Initiating PH iteration=" + `self._current_iteration`         

      self.iteration_0_solve()

      # update variable statistics prior to any output.
      self.update_variable_statistics()

      if self._verbose == True:
         print "Variable values following scenario solves:"
         self.pprint(False,False,True)

      # let plugins know if they care.
      if len(self._ph_plugin) == 1:
         self._ph_plugin.service().post_iteration_0_solves(self)      

      self._converger.update(self._current_iteration, self._scenario_tree, self._instances)
      print "Convergence metric=%12.4f" % self._converger.lastMetric()

      self.update_weights()

      if self._max_iterations > 0:
         self.form_iteration_k_objectives()

      # let plugins know if they care.
      if len(self._ph_plugin) == 1:
         self._ph_plugin.service().post_iteration_0(self)

      # iteration 0 is done, plugins are good to go. enter the async solve loop.
      self.iteration_k_plus_solves()
      
      print "PH complete"

      print "Final variable values:"
      self.pprint(False,False,True)         

      print "Final costs:"
      self._scenario_tree.pprintCosts(self._instances)

      self._solve_end_time = time.time()

      if (self._verbose is True) and (self._output_times is True):
         print "Overall solve time=" + str(self._solve_end_time - self._solve_start_time) + " seconds"

      # let plugins know if they care.
      if len(self._ph_plugin) == 1:
         self._ph_plugin.service().post_ph_execution(self)                                 

   #
   # prints a summary of all collected time statistics
   #
   def print_time_stats(self):

      print "PH run-time statistics (user):"

      print "Initialization time=  %8.2f seconds" % (self._init_end_time - self._init_start_time)
      print "Overall solve time=   %8.2f seconds" % (self._solve_end_time - self._solve_start_time)
      print "Scenario solve time=  %8.2f seconds" % self._cumulative_solve_time
      print "Average update time=  %8.2f seconds" % self._cumulative_xbar_time
      print "Weight update time=   %8.2f seconds" % self._cumulative_weight_time

   #
   # a utility to determine whether to output weight / average / etc. information for
   # a variable/node combination. when the printing is moved into a callback/plugin,
   # this routine will go there. for now, we don't dive down into the node resolution -
   # just the variable/stage.
   #
   def should_print(self, stage, variable, variable_indices):

      if self._output_continuous_variable_stats is False:

         variable_type = variable.domain         

         if (isinstance(variable_type, IntegerSet) is False) and (isinstance(variable_type, BooleanSet) is False):

            return False

      return True
      
   #
   # pretty-prints the state of the current variable averages, weights, and values.
   # inputs are booleans indicating which components should be output.
   #
   def pprint(self, output_averages, output_weights, output_values):

      # TBD - write a utility routine to figure out the longest identifier width for indicies and other names,
      #       to make the output a bit more readable.

      if self._initialized is False:
         raise RuntimeError, "PH is not initialized - cannot invoke pprint() method"         
      
      # print tree nodes and associated variable/xbar/ph information in stage-order
      for stage in self._scenario_tree._stages:

         # we don't blend in the last stage, so we don't current care about printing the associated information.
         if stage != self._scenario_tree._stages[-1]:

            print "\tStage=" + stage._name

            num_outputs_this_stage = 0 # tracks the number of outputs on a per-index basis.

            for (variable, index_template, variable_indices) in stage._variables:

               variable_name = variable.name

               if self.should_print(stage, variable, variable_indices) is True:

                  num_outputs_this_variable = 0 # track, so we don't output the variable names unless there is an entry to report.

                  for index in variable_indices:               

                     weight_parameter_name = "PHWEIGHT_"+variable_name

                     num_outputs_this_index = 0 # track, so we don't output the variable index more than once.

                     for tree_node in stage._tree_nodes:                  

                        # determine if the variable/index pair is used across the set of scenarios (technically,
                        # it should be good enough to check one scenario). will be deleted once we have
                        # implemented a "cull" method to get rid of unused variables and variable indices.

                        is_used = True # should be consistent across scenarios, so one "unused" flags as invalid.

                        for scenario in tree_node._scenarios:
                           instance = self._instances[scenario._name]
                           if getattr(instance,variable_name)[index].status == VarStatus.unused:
                              is_used = False
 
                        # IMPT: this is far from obvious, but variables that are fixed will - because
                        #       presolve will identify them as constants and eliminate them from all
                        #       expressions - be flagged as "unused" and therefore not output. 
   
                        if is_used is True:

                              minimum_value = value(tree_node._minimums[variable_name][index])
                              maximum_value = value(tree_node._maximums[variable_name][index])

                              num_outputs_this_stage = num_outputs_this_stage + 1                           
                              num_outputs_this_variable = num_outputs_this_variable + 1
                              num_outputs_this_index = num_outputs_this_index + 1

                              if num_outputs_this_variable == 1:
                                 print "\t\tVariable=",variable_name

                              if num_outputs_this_index == 1:
                                 print "\t\t\tIndex:", indexToString(index)                              

                              print "\t\t\t\tTree Node=",tree_node._name,"\t\t (Scenarios: ",                              
                              for scenario in tree_node._scenarios:
                                 print scenario._name," ",
                                 if scenario == tree_node._scenarios[-1]:
                                    print ")"
                           
                              if output_values is True:
                                 average_value = value(tree_node._averages[variable_name][index])
                                 print "\t\t\t\tValues: ",                        
                                 for scenario in tree_node._scenarios:
                                    instance = self._instances[scenario._name]
                                    this_value = getattr(instance,variable_name)[index].value
                                    print "%12.4f" % this_value,
                                    if scenario == tree_node._scenarios[-1]:
                                       print "    Max-Min=%12.4f" % (maximum_value-minimum_value),
                                       print "    Avg=%12.4f" % (average_value),
                                       print ""
                              if output_weights:
                                 print "\t\t\t\tWeights: ",
                                 for scenario in tree_node._scenarios:
                                    instance = self._instances[scenario._name]
                                    print "%12.4f" % value(getattr(instance,weight_parameter_name)[index])
                                    if scenario == tree_node._scenarios[-1]:
                                       print ""
                              if output_averages:
                                 print "\t\t\t\tAverage: %12.4f" % (value(tree_node._averages[variable_name][index]))

            if num_outputs_this_stage == 0:
               print "\t\tNo non-converged variables in stage"

            # cost variables aren't blended, so go through the gory computation of min/max/avg.
            # TBD: possibly move these into the tree node anyway, as they are useful in general.
            # TBD: these should also be probability-weighted - fix with above-mentioned TBD fix.
            # we currently always print these.
            cost_variable_name = stage._cost_variable[0].name
            cost_variable_index = stage._cost_variable[1]
            if cost_variable_index is None:
               print "\t\tCost Variable=" + cost_variable_name
            else:
               print "\t\tCost Variable=" + cost_variable_name + indexToString(cost_variable_index)            
            for tree_node in stage._tree_nodes:
               print "\t\t\tTree Node=" + tree_node._name + "\t\t (Scenarios: ",
               for scenario in tree_node._scenarios:
                  print scenario._name," ",
                  if scenario == tree_node._scenarios[-1]:
                     print ")"
               maximum_value = 0.0
               minimum_value = 0.0
               sum_values = 0.0
               num_values = 0
               first_time = True
               print "\t\t\tValues: ",                        
               for scenario in tree_node._scenarios:
                   instance = self._instances[scenario._name]
                   this_value = getattr(instance,cost_variable_name)[cost_variable_index].value
                   print "%12.4f" % this_value,
                   num_values += 1
                   sum_values += this_value
                   if first_time is True:
                      first_time = False
                      maximum_value = this_value
                      minimum_value = this_value
                   else:
                      if this_value > maximum_value:
                         maximum_value = this_value
                      if this_value < minimum_value:
                         minimum_value = this_value
                   if scenario == tree_node._scenarios[-1]:
                      print "    Max-Min=%12.4f" % (maximum_value-minimum_value),
                      print "    Avg=%12.4f" % (sum_values/num_values),
                      print ""
            
