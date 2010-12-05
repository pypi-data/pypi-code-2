#
# Abstract Knapsack Problem
#

from coopr.pyomo import *


model = AbstractModel()

model.N = Param(within=PositiveIntegers)

model.items = RangeSet(0,model.N-1)

model.v = Param(model.items, within=PositiveReals)

model.w = Param(model.items, within=PositiveReals)

model.limit = Param(within=PositiveReals)

model.x = Var(model.items, within=Binary)

def value_rule(model):
    return sum(model.v[i]*model.x[i] for i in model.items)
model.value = Objective(sense=maximize)

def weight_rule(model):
    return sum(model.w[i]*model.x[i] for i in model.items) <= model.limit
model.weight = Constraint()
