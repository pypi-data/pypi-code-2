# an example of an indexed piecewise function, i.e., a set of piecewise functions, each identified by a unique index.

from coopr.pyomo import *

def compute_breakpoints(i, m):
  return [0]

def compute_slopes(i, m):
  return [-1, 1]

model = AbstractModel()

model.Index = Set(initialize=[1, 2])

model.X = Var(model.Index)

model.Z = Piecewise(model.Index,
                    breakpoint_rule=compute_breakpoints,
                    slope_rule=compute_slopes,
                    offset=2,
                    value=model.X)

def objective_rule(model):
   return sum([model.Z[i] for i in model.Index])

model.obj = Objective(rule = objective_rule, sense=minimize)
