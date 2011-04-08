# identical to example1 - just more breakpoints.
#
# because the left-most breakpoint equals -2.5,
# the fixed "reference" point is (-2.5,0). the
# optimal variable value for this problem is
# obviously x=0. however, because the fixed
# point equals (-2.5,0) and the slope from x=-2.5
# x=0 is -1, the optimal objective function
# value equals -2.5.

from coopr.pyomo import *

model = AbstractModel()

model.X = Var(bounds=(-5,5))

breakpoints = [-2.5, 0, 2.5]
slopes =      [-10, -1, 1, 10]

model.Z = Piecewise(breakpoints=breakpoints,
                    slopes=slopes,
                    value=model.X)

model.obj = Objective(rule = lambda model: model.Z, sense=minimize)
