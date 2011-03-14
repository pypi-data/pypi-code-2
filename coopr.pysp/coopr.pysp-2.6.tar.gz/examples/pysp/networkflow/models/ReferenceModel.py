#
# A simple budget-constrained single-commodity network flow problem, taken from Ruszcynski.
#

from coopr.pyomo import *

#
# Model
#

model = AbstractModel()

#
# Parameters
#

model.Nodes = Set(ordered=True)

model.Arcs = Set(within=model.Nodes*model.Nodes)

# derived set
def aplus_arc_set_rule(v, model):
   return  [(i, j) for (i, j) in model.Arcs if j == v]
model.Aplus = Set(model.Nodes, within=model.Arcs, rule=aplus_arc_set_rule)

# derived set
def aminus_arc_set_rule(v, model):
   return  [(i, j) for (i, j) in model.Arcs if i == v]
model.Aminus = Set(model.Nodes, within=model.Arcs, rule=aminus_arc_set_rule)

model.Demand = Param(model.Nodes, model.Nodes, default=0.0)

model.CapCost = Param(model.Arcs)

model.b0Cost = Param(model.Arcs)

model.FCost = Param(model.Nodes, model.Nodes)

def compute_scenario_m_rule(model):
   max_value = 0.0
   for index in model.Demand:
      max_value = max(max_value, value(model.Demand[index]))
   return max_value
model.M = Param(within=NonNegativeReals, default=0.0, rule=compute_scenario_m_rule)

#
# Variables
#

# total arc capacity.
model.x = Var(model.Arcs, within=NonNegativeReals)

# from between the nodes through the arc
model.y = Var(model.Nodes, model.Nodes, model.Arcs, within=NonNegativeReals)

# first stage budget allocation variable
model.b0 = Var(model.Arcs, within=Binary)

# second stage budget allocation variable
model.b = Var(model.Arcs, within=Binary)

# the cost variables for the stages, in isolation.
model.FirstStageCost = Var()
model.SecondStageCost = Var()

#
# Constraints
#

def flow_balance_constraint_rule(v, k, l, model):
   if v == k:
      return (sum([model.y[k, l, i, j] for (i, j) in model.Aplus[v]]) - sum([model.y[k, l, i, j] for (i, j) in model.Aminus[v]]) + model.Demand[k, l]) == 0.0
   elif v == l:
      return (sum([model.y[k, l, i, j] for (i, j) in model.Aplus[v]]) - sum([model.y[k, l, i, j] for (i, j) in model.Aminus[v]]) - model.Demand[k, l]) == 0.0
   else:
      return (sum([model.y[k, l, i, j] for (i, j) in model.Aplus[v]]) - sum([model.y[k, l, i, j] for (i, j) in model.Aminus[v]])) == 0.0      
model.FlowBalanceConstraint = Constraint(model.Nodes, model.Nodes, model.Nodes, rule=flow_balance_constraint_rule)

def capacity_constraint_rule(i, j, model):
   return (None, sum([model.y[k, l, i, j] for k in model.Nodes for l in model.Nodes]) - model.x[i, j], 0.0)
model.CapacityConstraint = Constraint(model.Arcs, rule=capacity_constraint_rule)

def x_symmetry_constraint_rule(i, j, model):
   return (model.x[i, j] - model.x[j, i]) == 0.0
model.xSymmetryConstraint = Constraint(model.Arcs, rule=x_symmetry_constraint_rule)

def b0_symmetry_constraint_rule(i, j, model):
   return (model.b0[i, j] - model.b0[j, i]) == 0.0
model.b0SymmetryConstraint = Constraint(model.Arcs, rule=b0_symmetry_constraint_rule)
    
def b_symmetry_constraint_rule(i, j, model):
   return (model.b[i, j] - model.b[j, i]) == 0.0
model.bSymmetryConstraint = Constraint(model.Arcs, rule=b_symmetry_constraint_rule)
    
def bought_arc0_constraint_rule(k, l, i, j, model):
   return (0.0, model.M * model.b0[i, j] - model.y[k, l, i, j], None)
model.BoughtArc0Constraint = Constraint(model.Nodes, model.Nodes, model.Arcs, rule=bought_arc0_constraint_rule)

def bought_arc_constraint_rule(k, l, i, j, model):
   return (0.0, model.M * model.b[i, j] - model.y[k, l, i, j], None)
model.BoughtArcConstraint = Constraint(model.Nodes, model.Nodes, model.Arcs, rule=bought_arc_constraint_rule)

#
# Stage-specific cost computations
#

def compute_first_stage_cost_rule(model):
   return (model.FirstStageCost - summation(model.CapCost, model.x) - summation(model.b0Cost, model.b0)) == 0.0
model.ComputeFirstStageCost = Constraint(rule=compute_first_stage_cost_rule)

def compute_second_stage_cost_rule(model):
   return (model.SecondStageCost - summation(model.FCost, model.b)) == 0.0
model.ComputeSecondStageCost = Constraint(rule=compute_second_stage_cost_rule)

#
# Objective
#

def total_cost_rule(model):
    return model.FirstStageCost + model.SecondStageCost

model.Total_Cost_Objective = Objective(rule=total_cost_rule, sense=minimize)
