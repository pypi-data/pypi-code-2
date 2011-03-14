# same as example 1, but with maximization. should yield an unboundedness error.

from coopr.pyomo import *

model = AbstractModel()

model.X = Var(bounds=(-5,5))

breakpoints = [0]
slopes =      [-1, 1]

model.Z = Piecewise(breakpoints=breakpoints,
                    slopes=slopes,
                    offset=0,
                    value=model.X)

model.obj = Objective(rule = lambda model: model.Z, sense=maximize)
