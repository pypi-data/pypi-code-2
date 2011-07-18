# a simple example illustrating piecewise linear
# constraints on the value of a variable X.
#
# the minimal objective function value is obtained
# with x=0. because there is a single breakpoint,
# the fixed point (where y=0) is assumed to be
# (0,0) - by adding the keyword "offset=y", this
# can be changed to (0,y). Thus, the optimal
# objective function value at x=0 is 0!

from coopr.pyomo import *

model = AbstractModel()

model.X = Var(bounds=(-5,5))

breakpoints = [0]
slopes =      [-1, 1]

model.Z = Piecewise(breakpoints=breakpoints,
                    slopes=slopes,
                    offset=0,
                    value=model.X)

model.obj = Objective(rule = lambda model: model.Z, sense=minimize)
