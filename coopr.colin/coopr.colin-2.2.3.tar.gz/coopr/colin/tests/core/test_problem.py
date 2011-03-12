#
# Unit Tests for coopr.colin.problem
#
#

import os
import sys
from os.path import abspath, dirname
cooprdir = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.insert(0, cooprdir)
cooprdir += os.sep
currdir = dirname(abspath(__file__))+os.sep

from nose.tools import nottest
import coopr.colin
import xml
from coopr.opt import ResultsFormat, ProblemFormat
import pyutilib.services
import pyutilib.th as unittest


class TestProblem1(coopr.colin.MixedIntOptProblem):

    def __init__(self):
        coopr.colin.MixedIntOptProblem.__init__(self)
        self.real_lower=[0.0, -1.0, 1.0, None]
        self.real_upper=[None, 0.0, 2.0, -1.0]
        self.nreal=4

    def function_value(self, point):
        self.validate(point)
        return point.reals[0] - point.reals[1] + (point.reals[2]-1.5)**2 + (point.reals[3]+2)**4




class TestColinProblem(unittest.TestCase):

    def setUp(self):
        self.do_setup(False)
        pyutilib.services.TempfileManager.tempdir = currdir

    def do_setup(self,flag):
        pyutilib.services.TempfileManager.tempdir = currdir
        self.ps = coopr.colin.solver.PatternSearch()
        self.problem=TestProblem1()

    def tearDown(self):
        pyutilib.services.TempfileManager.clear_tempfiles()

    def test_error1(self):
        point = coopr.colin.MixedIntVars()
        point.reals = [1.0]
        try:
            self.problem.validate(point)
            self.fail("Expected ValueError")
        except ValueError:
            pass
        point.reals = [1.0] * 4
        point.integers = [1.0] * 4
        

if __name__ == "__main__":
    unittest.main()

