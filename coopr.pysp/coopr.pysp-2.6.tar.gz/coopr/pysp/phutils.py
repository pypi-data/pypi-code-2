#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

import string
import traceback
import os

from coopr.pyomo import *

from coopr.pyomo.expr.linear_repn import linearize_model_expressions

# for PYRO
import Pyro.core
import Pyro.naming


#
# a utility for shutting down Pyro-related components, which at the
# moment is restricted to the name server and any dispatchers. the
# mip servers will come down once their dispatcher is shut down.
# NOTE: this is a utility that should eventually become part of
#       pyutilib.pyro, but because is prototype, I'm keeping it
#       here for now.
#

def shutDownPyroComponents():

   Pyro.core.initServer()
   ns = Pyro.naming.NameServerLocator().getNS()
   ns_entries = ns.flatlist()
   for (name,uri) in ns_entries:
      if name == ":Pyro.NameServer":
         proxy = Pyro.core.getProxyForURI(uri)
         proxy._shutdown()
      elif name == ":PyUtilibServer.dispatcher":
         proxy = Pyro.core.getProxyForURI(uri)
         proxy.shutdown()

#
# a simple utility function to pretty-print an index tuple into a [x,y] form string.
#

def indexToString(index):

   # if the input type is a string or an int, then this isn't a tuple!
   if isinstance(index, (str, int)):
      return "["+str(index)+"]"

   result = "["
   for i in range(0,len(index)):
      result += str(index[i])
      if i != len(index) - 1:
         result += ","
   result += "]"
   return result

#
# a simple utility to determine if a variable name contains an index specification.
# in other words, is the reference to a complete variable (e.g., "foo") - which may
# or may not be indexed - or a specific index or set of indices (e.g., "foo[1]" or
# or "foo[1,*]".
#

def isVariableNameIndexed(variable_name):

   left_bracket_count = variable_name.count('[')
   right_bracket_count = variable_name.count(']')

   if (left_bracket_count == 1) and (right_bracket_count == 1):
      return True
   elif (left_bracket_count == 1) or (right_bracket_count == 1):
      raise ValueError, "Illegally formed variable name="+variable_name+"; if indexed, variable names must contain matching left and right brackets"
   else:
      return False

#
# takes a string indexed of the form "('foo', 'bar')" and returns a proper tuple ('foo','bar')
#

def tupleizeIndexString(index_string):

   index_string=index_string.lstrip('(')
   index_string=index_string.rstrip(')')
   pieces = index_string.split(',')
   return_index = ()
   for piece in pieces:
      piece = string.strip(piece)
      piece = piece.lstrip('\'')
      piece = piece.rstrip('\'')
      transformed_component = None
      try:
         transformed_component = int(piece)
      except ValueError:
         transformed_component = piece
      return_index = return_index + (transformed_component,)

   # IMPT: if the tuple is a singleton, return the element itself.
   if len(return_index) == 1:
      return return_index[0]
   else:
      return return_index

#
# related to above, extract the index from the variable name.
# will throw an exception if the variable name isn't indexed.
# the returned variable name is a string, while the returned
# index is a tuple. integer values are converted to integers
# if the conversion works!
#

def extractVariableNameAndIndex(variable_name):

   if isVariableNameIndexed(variable_name) is False:
      raise ValueError, "Non-indexed variable name passed to function extractVariableNameAndIndex()"

   pieces = variable_name.split('[')
   name = string.strip(pieces[0])
   full_index = pieces[1].rstrip(']')

   # even nested tuples in pyomo are "flattened" into
   # one-dimensional tuples. to accomplish flattening
   # replace all parens in the string with commas and
   # proceed with the split.
   full_index=string.translate(full_index, string.maketrans("",""), "()")
   indices = full_index.split(',')

   return_index = ()

   for index in indices:

      # unlikely, but strip white-space from the string.
      index=string.strip(index)

      # if the tuple contains nested tuples, then the nested
      # tuples have single quotes - "'" characters - around
      # strings. remove these, as otherwise you have an
      # illegal index.
      index=string.translate(index, string.maketrans("",""), "\'")

      # if the index is an integer, make it one!
      transformed_index = None
      try:
         transformed_index = int(index)
      except ValueError:
         transformed_index = index
      return_index = return_index + (transformed_index,)

   # IMPT: if the tuple is a singleton, return the element itself.
   if len(return_index) == 1:
      return name, return_index[0]
   else:
      return name, return_index

#
# determine if the input index is an instance of the template,
# which may or may not contain wildcards.
#

def indexMatchesTemplate(index, index_template):

   # if the input index is not a tuple, make it one.
   # ditto with the index template. one-dimensional
   # indices in pyomo are not tuples, but anything
   # else is.

   if type(index) != tuple:
      index = (index,)
   if type(index_template) != tuple:
      index_template = (index_template,)

   if len(index) != len(index_template):
      return False

   for i in range(0,len(index_template)):
      if index_template[i] == '*':
         # anything matches
         pass
      else:
         if index_template[i] != index[i]:
            return False

   return True

#
# given a variable (the real object, not the name) and an index,
# "shotgun" the index and see which variable indices match the
# input index. the cardinality could be > 1 if slices are
# specified, e.g., [*,1].
#

def extractVariableIndices(variable, index_template):

   result = []

   for index in variable._index:

      if indexMatchesTemplate(index, index_template) is True:
         result.append(index)

   return result

#
# construct a scenario instance!
#
def construct_scenario_instance(scenario_tree_instance,
                                scenario_data_directory_name,
                                scenario_name,
                                reference_model,
                                verbose,
                                preprocess = True,
                                linearize = True):

   if verbose is True:
      if scenario_tree_instance._scenario_based_data == 1:
         print "Scenario-based instance initialization enabled"
      else:
         print "Node-based instance initialization enabled"

   scenario = scenario_tree_instance.get_scenario(scenario_name)
   scenario_instance = None

   if verbose is True:
      print "Creating instance for scenario=" + scenario._name

   try:
      if scenario_tree_instance._scenario_based_data == 1:
         scenario_data_filename = scenario_data_directory_name + os.sep + scenario._name + ".dat"
         if verbose is True:
            print "Data for scenario=" + scenario._name + " loads from file=" + scenario_data_filename
         scenario_instance = reference_model.create(scenario_data_filename)
      else:
         scenario_instance = reference_model.clone()

         data_files = []
         current_node = scenario._leaf_node
         while current_node is not None:
            node_data_filename = scenario_data_directory_name + os.sep + current_node._name + ".dat"
            if os.path.exists(node_data_filename) is False:
               raise RuntimeError, "Node data file="+node_data_filename+" does not exist or cannot be accessed"
            data_files.append(node_data_filename)
            current_node = current_node._parent         

         # to make sure we read from root node to leaf node
         data_files.reverse() 

         scenario_data = ModelData()
         for data_file in data_files:
            if verbose is True:
               print "Node data for scenario=" + scenario._name + " partially loading from file=" + data_file
            scenario_data.add(data_file)

         scenario_data.read(model=scenario_instance)
         scenario_instance.load(scenario_data)
         if preprocess is True:
            scenario_instance.preprocess()         
   except:
      print "Encountered exception in model instance creation - traceback:"
      traceback.print_exc()
      raise RuntimeError, "Failed to create model instance for scenario=" + scenario._name

   if linearize is True:
      # IMPT: The model *must* be preprocessed in order for linearization to work. This is because
      #       linearization relies on the canonical expression representation extraction routine,
      #       which in turn relies on variables being identified/categorized (e.g., into "Used").
      if preprocess is False:
         scenario_instance.preprocess()
      linearize_model_expressions(scenario_instance)

   return scenario_instance


# creates all PH parameters for a problem instance, given a scenario tree
# (to identify the relevant variables), a default rho (simply for initialization),
# and a boolean indicating if quadratic penalty terms are to be linearized.
# returns a list of any created variables, specifically when linearizing -
# this is useful to clean-up reporting.

def create_ph_parameters(instance, scenario_tree, default_rho, linearizing_penalty_terms):

   new_penalty_variable_names = []

   # first, gather all unique variables referenced in any stage
   # other than the last, independent of specific indices. this
   # "gather" step is currently required because we're being lazy
   # in terms of index management in the scenario tree - which
   # should really be done in terms of sets of indices.
   # NOTE: technically, the "instance variables" aren't really references
   # to the variable in the instance - instead, the reference model. this
   # isn't an issue now, but it could easily become one (esp. in avoiding deep copies).
   instance_variables = {}

   for stage in scenario_tree._stages[:-1]:

      for (reference_variable, index_template) in stage._variables:

         if reference_variable.name not in instance_variables.keys():

            instance_variables[reference_variable.name] = reference_variable

   # for each blended variable, create a corresponding ph weight and average parameter in the instance.
   # this is a bit wasteful, in terms of indices that might appear in the last stage, but that is minor
   # in the grand scheme of things.

   for (variable_name, reference_variable) in instance_variables.items():

      # PH WEIGHT

      new_w_index = reference_variable._index
      new_w_parameter_name = "PHWEIGHT_"+reference_variable.name
      # this bit of ugliness is due to Pyomo not correctly handling the Param construction
      # case when the supplied index set consists strictly of None, i.e., the source variable
      # is a singleton. this case be cleaned up when the source issue in Pyomo is fixed.
      new_w_parameter = None
      if (len(new_w_index) is 1) and (None in new_w_index):
         new_w_parameter = Param(name=new_w_parameter_name, default=0.0, nochecking=True)
      else:
         new_w_parameter = Param(new_w_index, name=new_w_parameter_name, default=0.0, nochecking=True)
      setattr(instance,new_w_parameter_name,new_w_parameter)

      # if you don't explicitly assign values to each index, the entry isn't created - instead, when you reference
      # the parameter that hasn't been explicitly assigned, you just get the default value as a constant. I'm not
      # sure if this has to do with the model output, or the function of the model, but I'm doing this to avoid the
      # issue in any case for now. NOTE: I'm not sure this is still the case in Pyomo.
      for index in new_w_index:
         new_w_parameter[index] = 0.0

      # PH AVG

      new_avg_index = reference_variable._index
      new_avg_parameter_name = "PHAVG_"+reference_variable.name
      new_avg_parameter = None
      if (len(new_avg_index) is 1) and (None in new_avg_index):
         new_avg_parameter = Param(name=new_avg_parameter_name, default=0.0, nochecking=True)
      else:
         new_avg_parameter = Param(new_avg_index, name=new_avg_parameter_name, default=0.0, nochecking=True)
      setattr(instance,new_avg_parameter_name,new_avg_parameter)

      for index in new_avg_index:
         new_avg_parameter[index] = 0.0

      # PH RHO

      new_rho_index = reference_variable._index
      new_rho_parameter_name = "PHRHO_"+reference_variable.name
      new_rho_parameter = None
      if (len(new_avg_index) is 1) and (None in new_avg_index):
         new_rho_parameter = Param(name=new_rho_parameter_name, default=0.0, nochecking=True)
      else:
         new_rho_parameter = Param(new_rho_index, name=new_rho_parameter_name, default=0.0, nochecking=True)
      setattr(instance,new_rho_parameter_name,new_rho_parameter)

      for index in new_rho_index:
         new_rho_parameter[index] = default_rho

      # PH LINEARIZED PENALTY TERM

      if linearizing_penalty_terms > 0:

         new_penalty_term_variable_index = reference_variable._index
         new_penalty_term_variable_name = "PHQUADPENALTY_"+reference_variable.name
         # this is a quadratic penalty term - the lower bound is 0!
         new_penalty_term_variable = None
         if (len(new_avg_index) is 1) and (None in new_avg_index):
            new_penalty_term_variable = Var(name=new_penalty_term_variable_name, bounds=(0.0,None))
         else:
            new_penalty_term_variable = Var(new_penalty_term_variable_index, name=new_penalty_term_variable_name, bounds=(0.0,None))
         setattr(instance, new_penalty_term_variable_name, new_penalty_term_variable)
         new_penalty_variable_names.append(new_penalty_term_variable_name)

      # BINARY INDICATOR PARAMETER FOR WHETHER SPECIFIC VARIABLES ARE BLENDED. FOR ADVANCED USERS ONLY.

      # also controls whether weight updates proceed at any iteration.

      new_blend_index = reference_variable._index
      new_blend_parameter_name = "PHBLEND_"+reference_variable.name
      new_blend_parameter = None
      if (len(new_avg_index) is 1) and (None in new_avg_index):
         new_blend_parameter = Param(name=new_blend_parameter_name, within=Binary, default=False, nochecking=True)
      else:
         new_blend_parameter = Param(new_blend_index, name=new_blend_parameter_name, within=Binary, default=False, nochecking=True)
      setattr(instance,new_blend_parameter_name,new_blend_parameter)

      for index in new_blend_index:
         new_blend_parameter[index] = 1

   return new_penalty_variable_names
