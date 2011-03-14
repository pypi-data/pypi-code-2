#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2010 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

# this module contains various utilities for creating PH weighted penalty
# objectives, e.g., through quadratic or linearized penalty terms.

from math import fabs, log, exp
from coopr.pyomo import *
from phutils import indexToString

# IMPT: In general, the breakpoint computation codes can return a 2-list even if the lb equals
#       the ub. This case happens quite often in real models (although typically lb=xvag=ub).
#       See the code for constructing the pieces on how this case is handled in the linearization.

#
# routine to compute linearization breakpoints uniformly between the bounds and the mean.
#

def compute_uniform_breakpoints(lb, node_min, xavg, node_max, ub, num_breakpoints_per_side, tolerance):

   breakpoints = []

   # add the lower bound - the first breakpoint.
   breakpoints.append(lb)

   # determine the breakpoints to the left of the mean.
   left_step = (xavg - lb) / num_breakpoints_per_side
   current_x = lb
   for i in range(1,num_breakpoints_per_side+1):
      this_lb = current_x
      this_ub = current_x+left_step
      if (fabs(this_lb-lb) > tolerance) and (fabs(this_lb-xavg) > tolerance):
         breakpoints.append(this_lb)
      current_x += left_step

   # add the mean - it's always a breakpoint. unless!
   # the lb or ub and the avg are the same.
   if (fabs(lb-xavg) > tolerance) and (fabs(ub-xavg) > tolerance):
      breakpoints.append(xavg)

   # determine the breakpoints to the right of the mean.
   right_step = (ub - xavg) / num_breakpoints_per_side
   current_x = xavg
   for i in range(1,num_breakpoints_per_side+1):
      this_lb = current_x
      this_ub = current_x+right_step
      if (fabs(this_ub-xavg) > tolerance) and (fabs(this_ub-ub) > tolerance):
         breakpoints.append(this_ub)
      current_x += right_step

   # add the upper bound - the last breakpoint.
   # the upper bound should always be different than the lower bound (I say with some
   # hesitation - it really depends on what plugins are doing to modify the bounds dynamically).
   breakpoints.append(ub)

   return breakpoints

#
# routine to compute linearization breakpoints uniformly between the current node min/max bounds.
#

def compute_uniform_between_nodestat_breakpoints(lb, node_min, xavg, node_max, ub, num_breakpoints, tolerance):

   breakpoints = []

   # add the lower bound - the first breakpoint.
   breakpoints.append(lb)

   # add the node-min - the second breakpoint. but only if it is different than the lower bound and the mean.
   if (fabs(node_min-lb) > tolerance) and (fabs(node_min-xavg) > tolerance):
      breakpoints.append(node_min)

   step = (node_max - node_min) / num_breakpoints
   current_x = node_min
   for i in range(1,num_breakpoints+1):
      this_lb = current_x
      this_ub = current_x+step
      if (fabs(this_lb-node_min) > tolerance) and (fabs(this_lb-node_max) > tolerance) and (fabs(this_lb-xavg) > tolerance):
         breakpoints.append(this_lb)
      current_x += step

   # add the node-max - the second-to-last breakpoint. but only if it is different than the upper bound and the mean.
   if (fabs(node_max-ub) > tolerance) and (fabs(node_max-xavg) > tolerance):
      breakpoints.append(node_max)

   # add the upper bound - the last breakpoint.
   breakpoints.append(ub)

   # add the mean - it's always a breakpoint. unless! -
   # it happens to be equal to (within tolerance) the lower or upper bounds.
   # sort to insert it in the correct place.
   if (fabs(xavg - lb) > tolerance) and (fabs(xavg - ub) > tolerance):
      breakpoints.append(xavg)
   breakpoints.sort()

   return breakpoints

#
# routine to compute linearization breakpoints using "Woodruff" relaxation of the compute_uniform_between_nodestat_breakpoints.
#

def compute_uniform_between_woodruff_breakpoints(lb, node_min, xavg, node_max, ub, num_breakpoints, tolerance):

   breakpoints = []

   # add the lower bound - the first breakpoint.
   breakpoints.append(lb)

   # be either three "differences" from the mean, or else "halfway to the bound", whichever is closer to the mean.
   left = max(xavg - 3.0 * (xavg - node_min), xavg - 0.5 * (xavg - lb))
   right = min(xavg + 3.0 * (node_max - xavg), xavg + 0.5 * (ub - xavg))

   # add the left bound - the second breakpoint. but only if it is different than the lower bound and the mean.
   if (fabs(left-lb) > tolerance) and (fabs(left-xavg) > tolerance):
      breakpoints.append(left)

   step = (right - left) / num_breakpoints
   current_x = left
   for i in range(1,num_breakpoints+1):
      this_lb = current_x
      this_ub = current_x+step
      if (fabs(this_lb-left) > tolerance) and (fabs(this_lb-right) > tolerance) and (fabs(this_lb-xavg) > tolerance):
         breakpoints.append(this_lb)
      current_x += step

   # add the right bound - the second-to-last breakpoint. but only if it is different than the upper bound and the mean.
   if (fabs(right-ub) > tolerance) and (fabs(right-xavg) > tolerance):
      breakpoints.append(right)

   # add the upper bound - the last breakpoint.
   breakpoints.append(ub)

   # add the mean - it's always a breakpoint.
   # sort to insert it in the correct place.
   breakpoints.append(xavg)
   breakpoints.sort()

   return breakpoints

#
# routine to compute linearization breakpoints based on an exponential distribution from the mean in each direction.
#

def compute_exponential_from_mean_breakpoints(lb, node_min, xavg, node_max, ub, num_breakpoints_per_side, tolerance):

   breakpoints = []

   # add the lower bound - the first breakpoint.
   breakpoints.append(lb)

   # determine the breakpoints to the left of the mean.
   left_delta = xavg - lb
   base = exp(log(left_delta) / num_breakpoints_per_side)
   current_offset = base
   for i in range(1,num_breakpoints_per_side+1):
      current_x = xavg - current_offset
      if (fabs(current_x-lb) > tolerance) and (fabs(current_x-xavg) > tolerance):
         breakpoints.append(current_x)
      current_offset *= base

   # add the mean - it's always a breakpoint.
   breakpoints.append(xavg)

   # determine the breakpoints to the right of the mean.
   right_delta = ub - xavg
   base = exp(log(right_delta) / num_breakpoints_per_side)
   current_offset = base
   for i in range(1,num_breakpoints_per_side+1):
      current_x = xavg + current_offset
      if (fabs(current_x-xavg) > tolerance) and (fabs(current_x-ub) > tolerance):
         breakpoints.append(current_x)
      current_offset *= base

   # add the upper bound - the last breakpoint.
   breakpoints.append(ub)

   return breakpoints

#
# a utility to create piece-wise linear constraint expressions for a given variable, for
# use in constructing the augmented (penalized) PH objective. lb and ub are the bounds
# on this piece, variable is the actual instance variable, and average is the instance
# parameter specifying the average of this variable across instances sharing passing
# through a common tree node. lb and ub are floats.
# IMPT: There are cases where lb=ub, in which case the slope is 0 and the intercept
#       is simply the penalty at the lower(or upper) bound.
#

def create_piecewise_constraint_tuple(lb, ub, instance_variable, variable_average, quad_variable, tolerance):

   penalty_at_lb = (lb - value(variable_average)) * (lb - value(variable_average))
   penalty_at_ub = (ub - value(variable_average)) * (ub - value(variable_average))
   slope = None
   if fabs(ub-lb) > tolerance:
      slope = (penalty_at_ub - penalty_at_lb) / (ub - lb)
   else:
      slope = 0.0
   intercept = penalty_at_lb - slope * lb
   expression = (0.0, quad_variable - slope * instance_variable - intercept, None)

   return expression

#
# form the baseline objective. really just a wrapper around a clone
# operation at this point.
#

def form_standard_objective(instance_name, instance, original_objective_expression, scenario_tree):

   objective_name = instance.active_components(Objective).keys()[0]
   objective = instance.active_components(Objective)[objective_name]
   # clone the objective, because we're going to augment (repeatedly) the original objective.
   objective_expression = original_objective_expression.clone()
   instance.active_components(Objective)[objective_name]._data[None].expr = objective_expression
   instance.active_components(Objective)[objective_name]._quad_subexpr = None

#
# form the penalized PH objective, guided by various options.
# returns the list of components added to the instance, e.g.,
# in the case of constraints required to implement linearization.
#

def form_ph_objective(instance_name, instance, original_objective_expression, scenario_tree, \
                      linearize_nonbinary_penalty_terms, drop_proximal_terms, \
                      retain_quadratic_binary_terms, breakpoint_strategy, \
                      tolerance):

   new_instance_attributes = []

   objective_name = instance.active_components(Objective).keys()[0]
   objective = instance.active_components(Objective)[objective_name]
   # clone the objective, because we're going to augment (repeatedly) the original objective.
   objective_expression = original_objective_expression.clone()
   # the quadratic expression is really treated as just a list - eventually should be treated as a full expression.
   quad_expression = 0.0

   # for each blended variable (i.e., those not appearing in the final stage),
   # add the linear and quadratic penalty terms to the objective.

   for stage in scenario_tree._stages[:-1]: # skip the last stage, as no blending occurs

      variable_tree_node = None
      for node in stage._tree_nodes:
         for scenario in node._scenarios:
            if scenario._name == instance_name:
               variable_tree_node = node
               break

      for (reference_variable, index_template) in stage._variables:

         variable_name = reference_variable.name
         variable_type = reference_variable.domain

         w_parameter_name = "PHWEIGHT_"+variable_name
         w_parameter = instance.active_components(Param)[w_parameter_name]

         average_parameter_name = "PHAVG_"+variable_name
         average_parameter = instance.active_components(Param)[average_parameter_name]

         rho_parameter_name = "PHRHO_"+variable_name
         rho_parameter = instance.active_components(Param)[rho_parameter_name]

         blend_parameter_name = "PHBLEND_"+variable_name
         blend_parameter = instance.active_components(Param)[blend_parameter_name]

         node_min_parameter = variable_tree_node._minimums[variable_name]
         node_max_parameter = variable_tree_node._maximums[variable_name]

         quad_penalty_term_variable = None
         if linearize_nonbinary_penalty_terms > 0:
            quad_penalty_term_variable_name = "PHQUADPENALTY_"+variable_name
            quad_penalty_term_variable = instance.active_components(Var)[quad_penalty_term_variable_name]

         instance_variable = instance.active_components(Var)[variable_name]

         variable_indices = variable_tree_node._variable_indices[variable_name]

         for index in variable_indices:

            if (instance_variable[index].status is not VarStatus.unused) and (instance_variable[index].fixed is False):

               # add the linear (w-weighted) term is a consistent fashion, independent of variable type.
               # if maximizing, here is where you would want "-=" - however, if you do this, the collect process chokes for reasons currently unknown.
               objective_expression += (value(w_parameter[index]) * instance_variable[index])

               # there are some cases in which a user may want to avoid the proximal term completely.
               # it's of course only a good idea when there are at least bounds (both lb and ub) on
               # the variables to be blended.
               if drop_proximal_terms is False:

                  # deal with binaries
                  if isinstance(variable_type, BooleanSet) is True:

                     if retain_quadratic_binary_terms is False:
                        # this rather ugly form of the linearized quadratic expression term is required
                        # due to a pyomo bug - the form (rho/2) * (x+y+z) chokes in presolve when distributing
                        # over the sum.
                        new_term = (value(blend_parameter[index]) * value(rho_parameter[index]) / 2.0 * instance_variable[index]) - \
                                   (value(blend_parameter[index]) * value(rho_parameter[index]) * value(average_parameter[index]) * instance_variable[index]) + \
                                   (value(blend_parameter[index]) * value(rho_parameter[index]) / 2.0 * value(average_parameter[index]) * value(average_parameter[index]))
                        if objective.sense is minimize:
                           objective_expression += new_term
                        else:
                           objective_expression -= new_term
                     else:
                        quad_expression += (blend_parameter[index] * rho_parameter[index] * (instance_variable[index] - average_parameter[index]) ** 2)

                  # deal with everything else
                  else:

                     if linearize_nonbinary_penalty_terms > 0:

                        # the variables are easy - just a single entry.
                        if objective.sense is minimize:
                           objective_expression += (rho_parameter[index] / 2.0 * quad_penalty_term_variable[index])
                        else:
                           objective_expression -= (rho_parameter[index] / 2.0 * quad_penalty_term_variable[index])

                        # the constraints are somewhat nastier.

                        # TBD - DEFINE CONSTRAINTS ON-THE-FLY?? (INDIVIDUALLY NAMED FOR NOW - CREATE INDEX SETS!) - OR A LEAST AN INDEX SET PER "PIECE"
                        xavg = average_parameter[index]
                        x = instance_variable[index]

                        if x.lb is None or x.ub is None:
                            var = variable_name + indexToString(index)
                            msg = "Missing bound for variable '%s'\n"         \
                                  'Both lower and upper bounds required when' \
                                  ' piece-wise approximating quadratic '      \
                                  'penalty terms'
                            raise ValueError, msg % var
                        lb = x.lb()
                        ub = x.ub()

                        node_min = value(node_min_parameter[index])
                        node_max = value(node_max_parameter[index])

                        # compute the breakpoint sequence according to the specified strategy.
                        try:
                            strategy = (
                              compute_uniform_breakpoints,
                              compute_uniform_between_nodestat_breakpoints,
                              compute_uniform_between_woodruff_breakpoints,
                              compute_exponential_from_mean_breakpoints,
                            )[ breakpoint_strategy ]
                            args = ( lb, node_min, value(xavg), node_max, ub, \
                                linearize_nonbinary_penalty_terms, tolerance )
                            breakpoints = strategy( *args )
                        except ValueError, e:
                            msg = 'A breakpoint distribution strategy (%s) '  \
                                  'is currently not supported within PH!'
                            raise ValueError, msg % breakpoint_strategy

                        for i in range(0,len(breakpoints)-1):

                           this_lb = breakpoints[i]
                           this_ub = breakpoints[i+1]

                           piece_tuple = create_piecewise_constraint_tuple(this_lb, this_ub, x, xavg, \
                                                                                quad_penalty_term_variable[index], \
                                                                                tolerance)

                           def makePieceRule(tuple):
                              def pieceRule(model):
                                 return tuple
                              return pieceRule

                           piece_constraint_name = "QUAD_PENALTY_PIECE_"+str(i)+"_"+variable_name+str(index)
                           piece_constraint = Constraint(name=piece_constraint_name, rule=makePieceRule(piece_tuple))
                           setattr(instance, piece_constraint_name, piece_constraint)

                           if hasattr(instance, piece_constraint_name) is False:
                              # this is the first time the constraint is being added - add it to the list of PH-specific constraints for this instance.
                              new_instance_attributes.append(piece_constraint_name)                           

                     else:

                        quad_expression += (blend_parameter[index] * rho_parameter[index] * (instance_variable[index] - average_parameter[index]) ** 2)

   # assign the new expression to the objective.
   instance.active_components(Objective)[objective_name]._data[None].expr = objective_expression

   # if we are linearizing everything, then nothing will appear in the quadratic expression -
   # don't add the empty "0.0" expression to the objective. otherwise, the output file won't
   # be properly generated.
   if quad_expression != 0.0:
     instance.active_components(Objective)[objective_name]._quad_subexpr = quad_expression
   else:
     instance.active_components(Objective)[objective_name]._quad_subexpr = None

   return new_instance_attributes
