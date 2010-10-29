#
# A multi-stage capacity expansion problem, taken from Ahmed et al.
#

from coopr.pyomo import *

#
# Model
#

model = Model()

#
# Parameters
#

# the number of stages.
model.NumStages = Param(within=PositiveIntegers)

# derived set.
def stages_set_rule(model):
   return set(range(1, model.NumStages()+1))
model.Stages = Set(rule=stages_set_rule)

# the number of resources.
model.NumResources = Param(within=PositiveIntegers)

# derived set.
def resources_set_rule(model):
   return set(range(1, model.NumResources()+1))
model.Resources = Set(rule=resources_set_rule)

# the marginal cost for each unit of procured resource.
model.MarginalCost = Param(model.Stages, model.Resources, within=PositiveReals)

# the fixed-charge cost for procurement of a given resource.
model.FixedCost = Param(model.Stages, model.Resources, within=PositiveReals)

# the amount of demand for each stage.
model.Demand = Param(model.Stages, within=NonNegativeReals)

# the upper bound on the amount of resource acquired in any given stage.
def procurement_upper_bound_rule(t, r, model):
   return model.Demand[t]()
model.ProcurementUpperBound = Param(model.Stages, model.Resources, within=NonNegativeReals, rule=procurement_upper_bound_rule)

#
# Variables
#

# a binary indicating whether a given resource is acquired
# in a given stage.
model.ProcureResource = Var(model.Stages, model.Resources, within=Binary)

# the amount of each resource acquired in each stage.
# NOTE: the bounds are a hack - it needs to be a global computed across all scenarios.
model.AmountProcured = Var(model.Stages, model.Resources, within=NonNegativeReals, bounds=(0.0, 1000.0))

# the cost variables for the stages.
model.StageCost = Var(model.Stages)

#
# Constraints
#

# enforce bound on resource acquisition.
def enforce_resource_bounds_rule(t, r, model):
   return (0.0, model.ProcurementUpperBound[t, r] * model.ProcureResource[t, r] - model.AmountProcured[t, r], None)
model.EnforceResourceAcquisitionBounds = Constraint(model.Stages, model.Resources, rule=enforce_resource_bounds_rule)

# ensure that demand is satisifed in each stage.
def satisfy_demand_rule(t, model):
   return (0.0, \
	   sum([model.AmountProcured[z, r] for z in model.Stages if z <= t for r in model.Resources]) - model.Demand[t], \
           None)
model.SatisfyDemand = Constraint(model.Stages, rule=satisfy_demand_rule)

#
# Stage-specific cost computations
#

def compute_stage_cost_rule(t, model):
   cost = sum([model.FixedCost[t, r] * model.ProcureResource[t, r] for r in model.Resources]) + \
          sum([model.MarginalCost[t, r] * model.AmountProcured[t, r] for r in model.Resources])

   return (model.StageCost[t] - cost) == 0.0

model.ComputeStageCost = Constraint(model.Stages, rule=compute_stage_cost_rule)

#
# Objective
#

def total_cost_rule(model):
    return sum([model.StageCost[t] for t in model.Stages])

model.Total_Cost_Objective = Objective(rule=total_cost_rule, sense=minimize)
