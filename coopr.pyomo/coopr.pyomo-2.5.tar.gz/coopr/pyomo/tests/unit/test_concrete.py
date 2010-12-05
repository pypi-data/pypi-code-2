#
# Test behavior of concrete classes.
#

import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+os.sep+".."+os.sep+"..")
currdir = dirname(abspath(__file__))+os.sep

from coopr.pyomo import *
from coopr.opt import *
import pyutilib.th as unittest
import pyutilib.services

class Test(unittest.TestCase):

    def test_blending(self):
        """ The blending example from the PuLP documentation """
        model = Model()
        model.concrete_mode()

        model.x1 = Var(bounds=(0,None), doc="ChickenPercent")
        model.x2 = Var(bounds=(0,None), doc="BeefPercent")

        model.obj = Objective(expr=0.013*model.x1 + 0.008*model.x2, doc="Total Cost of Ingredients per can")

        model.c0 = Constraint(expr=model.x1+model.x2 == 100.0, doc="Percentage Sum")
        model.c1 = Constraint(expr=0.100*model.x1 + 0.200*model.x2 >= 8.0, doc="Protein Requirement")
        model.c2 = Constraint(expr=0.080*model.x1 + 0.100*model.x2 >= 6.0, doc="Fat Requirement")
        model.c3 = Constraint(expr=0.001*model.x1 + 0.005*model.x2 <= 2.0, doc="Fiber Requirement")
        model.c4 = Constraint(expr=0.002*model.x1 + 0.005*model.x2 <= 0.4, doc="Salt Requirement")

        instance = model.create()
        opt = SolverFactory('glpk')
        solutions = opt.solve(instance, keepFiles=True)
        instance.load(solutions)
        solutions.write(filename=currdir+"blend.out")
        self.failUnlessFileEqualsBaseline(currdir+"blend.out",currdir+"blend.txt")

Test = unittest.skipIf(not pyutilib.services.registered_executable("glpsol"), "The 'glpsol' executable is not available")(Test)

if __name__ == "__main__":
   unittest.main()

