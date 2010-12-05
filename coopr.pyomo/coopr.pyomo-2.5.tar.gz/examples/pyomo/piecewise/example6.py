# an example of an indexed piecewise function, i.e., a set of piecewise functions, each identified by a unique index.
# minimum is at (0,0).

from coopr.pyomo import *

def compute_breakpoints(i, m):
  print "COMPUTING BREAKPOINTS FOR I=",i
  return [0, 2.5, 5]

def compute_slopes(i, m):
  print "COMPUTING SLOPES FOR I=",i
  return [-1, 1, 2, 3]

model = Model()

model.Index = Set(initialize=[1, 2])

model.X = Var()

model.Z = Piecewise(breakpoint_rule=compute_breakpoints,
                    slope_rule=compute_slopes,
                    breakpoint_sets=model.Index,
                    slope_sets=model.Index,
                    value=model.X)

model.obj = Objective(rule = lambda model: model.Z, sense=minimize)
