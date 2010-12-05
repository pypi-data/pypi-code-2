#
# Knapsack Problem
#

from coopr.pyomo import *

v = [8, 11, 6, 4]
w = [5, 7, 4, 3]
limit = 14

model = ConcreteModel()

model.items = RangeSet(0,3)

model.x = Var(model.items, within=Binary)

model.value = Objective(expr=sum(v[i]*model.x[i] for i in model.items), sense=maximize)

model.weight = Constraint(expr=sum(w[i]*model.x[i] for i in model.items) <= limit)
