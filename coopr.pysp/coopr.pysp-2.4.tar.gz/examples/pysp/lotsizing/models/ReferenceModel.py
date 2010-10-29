#
# A lot-sizing problem, taken from Haugen, Lokketangen, and Woodruff (2001).
# European Journal of Operational Reserach, Volume 132, pp. 116-122.
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

# the initial inventory, at time stage 0.
model.InitialInventory = Param(within=NonNegativeReals)

# the production setup cost in each time period.
model.SetupCost = Param(model.Stages, within=NonNegativeReals)

# the holding cost for inventory in each time period.
model.HoldingCost = Param(model.Stages, within=NonNegativeReals)

# the shortage cost for inventory in each time period.
model.ShortageCost = Param(model.Stages, within=NonNegativeReals)

# the demand for inventory in each time period.
model.Demand = Param(model.Stages, within=NonNegativeReals)

# the big M coefficient used to compute the production binary.
# production is trivially bounded by the sum of demand across
# stages minus the initial inventory.
def compute_m_rule(model):
   result = sum([model.Demand[t] for t in model.Stages]) - model.InitialInventory
   return result()
model.M = Param(within=NonNegativeReals, rule=compute_m_rule)

#
# Variables
#

# does production occur in time period t?
model.Produce = Var(model.Stages, within=Binary)

# TBD - upper bounds can be computed for each amount produced, inventory,
#       backlog variable - introduce bounds rule.

# the amount of product to be produced in time period t.
model.AmountProduced = Var(model.Stages, within=NonNegativeReals)

# the excess inventory at the end of time period t.
model.Inventory = Var(model.Stages, within=NonNegativeReals)

# the inventory backlog at the end of time period t.
model.Backlog = Var(model.Stages, within=NonNegativeReals)

# the cost variables for the stages.
model.StageCost = Var(model.Stages)

#
# Constraints
#

# can't produce unless production is enabled!
def limit_production_rule(t, model):
   return (None, model.AmountProduced[t] - model.M * model.Produce[t], 0.0)
model.LimitProduction = Constraint(model.Stages, rule=limit_production_rule)

# enforce inventory balance for each time period.
def inventory_balance_rule(t, model):
   expr = None
   if (t == 1):
      # there is no initial backlog.
      expr = model.AmountProduced[t] + model.InitialInventory + model.Backlog[t] - \
             model.Inventory[t] - model.Demand[t]      
   else:
      expr = model.AmountProduced[t] + model.Inventory[t-1] + model.Backlog[t] - \
             model.Inventory[t] - model.Backlog[t-1] - model.Demand[t]
   return (expr == 0.0)
model.InventoryBalance = Constraint(model.Stages, rule=inventory_balance_rule)

#
# Stage-specific cost computations
#

def compute_stage_cost_rule(t, model):
   cost = sum([model.SetupCost[t] * model.Produce[t] + \
               model.HoldingCost[t] * model.Inventory[t] + \
               model.ShortageCost[t] * model.Backlog[t]])

   return (model.StageCost[t] - cost) == 0.0

model.ComputeStageCost = Constraint(model.Stages, rule=compute_stage_cost_rule)

#
# Objective
#

def total_cost_rule(model):
    return sum([model.StageCost[t] for t in model.Stages])

model.Total_Cost_Objective = Objective(rule=total_cost_rule, sense=minimize)
