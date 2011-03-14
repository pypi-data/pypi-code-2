# a very simple non-convex "sawtooth" piecewise example. 

from coopr.pyomo import *

model = AbstractModel()

model.X = Var(bounds=(-5,5))

breakpoints = [ 0, 1, 1.5]
slopes =      [-1, 1, -1, 1]

model.Z = Piecewise(breakpoints=breakpoints,
                    slopes=slopes,
                    value=model.X)

model.obj = Objective(rule = lambda model: model.Z, sense=minimize)
