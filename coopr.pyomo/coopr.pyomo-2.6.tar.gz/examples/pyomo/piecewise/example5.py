# an example of a piecewise function constructed from breakpoint slopes and rules. 
# minimum is at (0,0), where the objective function value is 0.

from coopr.pyomo import *

def compute_breakpoints(m):
  return [0, 2.5, 5]

def compute_slopes(m):
  return [-1, 1, 2, 3]

model = AbstractModel()

model.X = Var()

model.Z = Piecewise(breakpoint_rule=compute_breakpoints,
                    slope_rule=compute_slopes,
                    value=model.X)

model.obj = Objective(rule = lambda model: model.Z, sense=minimize)
