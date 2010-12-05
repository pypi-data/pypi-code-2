#
# Imports
#
import sys
from coopr.pyomo import *

#
# Setup
#

model = Model()

model.NUTR = Set()

model.FOOD = Set()

model.cost = Param(model.FOOD, within=NonNegativeReals)

model.f_min = Param(model.FOOD, within=NonNegativeReals)

def f_max_valid (value, j, model):
    return value > model.f_min[j]
model.f_max = Param(model.FOOD, validate=f_max_valid)

model.n_min = Param(model.NUTR, within=NonNegativeReals)

def paramn_max (value, i, model):
    return value > model.n_min[i]
model.n_max = Param(model.NUTR, validate=paramn_max)

model.amt = Param(model.NUTR, model.FOOD, within=NonNegativeReals)

def Buy_bounds(i,model):
    return (model.f_min[i],model.f_max[i])
model.Buy = Var(model.FOOD, bounds=Buy_bounds, domain=Integers)

def Objective_rule(model):
    return summation(model.cost, model.Buy)
model.totalcost = Objective(rule=Objective_rule)

def Diet_rule(i, model):
    expr = 0
    for j in model.FOOD:
      expr = expr + model.amt[i,j] * model.Buy[j]
    return (model.n_min[i], expr, model.n_max[i])
model.Diet = Constraint(model.NUTR, rule=Diet_rule)

