#
# Unit Tests for coopr.opt.base.solution
#
#

import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+"/../..")
cooprdir = dirname(abspath(__file__))+os.sep+".."+os.sep+".."+os.sep
currdir = dirname(abspath(__file__))+os.sep

from nose.tools import nottest
import coopr.opt
import coopr
import pyutilib.th as unittest
import pyutilib.misc
import pyutilib.services
import xml
import pickle

try:
    import yaml
    yaml_available=True
except ImportError:
    yaml_available=False


class Test(unittest.TestCase):

    def setUp(self):
        pyutilib.services.TempfileManager.tempdir = currdir
        self.results = coopr.opt.SolverResults()
        self.soln = self.results.solution.add()
        self.soln.variable[1]=0.0
        self.soln.variable[2]=0.0
        self.soln.variable[4]=0.0
        pyutilib.services.TempfileManager.clear_tempfiles()

    def tearDown(self):
        del self.results

    def test_write_solution1(self):
        """ Write a SolverResults Object with solutions """
        self.results.write(filename=currdir+"write_solution1.txt")
        if not os.path.exists(currdir+"write_solution1.txt"):
           self.fail("test_write_solution - failed to write write_solution1.txt")
        self.failUnlessFileEqualsBaseline(currdir+"write_solution1.txt", currdir+"test1_soln.txt")

    def test_write_solution2(self):
        """ Write a SolverResults Object without solutions """
        self.results.write(num=None,filename=currdir+"write_solution2.txt")
        if not os.path.exists(currdir+"write_solution2.txt"):
           self.fail("test_write_solution - failed to write write_solution2.txt")
        self.failUnlessFileEqualsBaseline(currdir+"write_solution2.txt", currdir+"test2_soln.txt")

    @unittest.skipIf(not yaml_available, "Cannot import 'yaml'")
    def test_read_solution1(self):
        """ Read a SolverResults Object"""
        self.results = coopr.opt.SolverResults()
        self.results.read(filename=currdir+"test4_sol.txt")
        self.results.write(filename=currdir+"read_solution1.out")
        if not os.path.exists(currdir+"read_solution1.out"):
           self.fail("test_read_solution1 - failed to write read_solution1.out")
        self.failUnlessFileEqualsBaseline(currdir+"read_solution1.out", currdir+"test4_sol.txt")

    @unittest.skipIf(not yaml_available, "Cannot import 'yaml'")
    def test_pickle_solution1(self):
        """ Read a SolverResults Object"""
        self.results = coopr.opt.SolverResults()
        self.results.read(filename=currdir+"test4_sol.txt")
        str = pickle.dumps(self.results)
        res = pickle.loads(str)
        self.results.write(filename=currdir+"read_solution1.out")
        if not os.path.exists(currdir+"read_solution1.out"):
           self.fail("test_read_solution1 - failed to write read_solution1.out")
        self.failUnlessFileEqualsBaseline(currdir+"read_solution1.out", currdir+"test4_sol.txt")

    #
    # deleting is not supported right now
    #
    def Xtest_delete_solution(self):
        """ Delete a solution from a SolverResults object """
        self.results.solution.delete(0)
        self.results.write(filename=currdir+"delete_solution.txt")
        if not os.path.exists(currdir+"delete_solution.txt"):
           self.fail("test_write_solution - failed to write delete_solution.txt")
        self.failUnlessFileEqualsBaseline(currdir+"delete_solution.txt", currdir+"test4_soln.txt")

    def test_get_solution(self):
        """ Get a solution from a SolverResults object """
        tmp = self.results.solution[0]
        self.failUnlessEqual(tmp,self.soln)

    def test_get_solution_attr_error(self):
        """ Create an error with a solution suffix """
        try:
           tmp = self.soln.bad
           self.fail("Expected attribute error failure for 'bad'")
        except AttributeError:
           pass

    #
    # This is currently allowed, although soln.variable = True is equivalent to
    #   soln.variable.value = True
    #
    def Xtest_set_solution_attr_error(self):
        """ Create an error with a solution suffix """
        try:
           self.soln.variable = True
           self.fail("Expected attribute error failure for 'variable'")
        except AttributeError:
           pass

    def test_soln_pprint1(self):
        """ Write a solution with only zero values, using the results 'write()' method """
        self.soln.variable[1]=0.0
        self.soln.variable[2]=0.0
        self.soln.variable[4]=0.0
        self.results.write(filename=currdir+"soln_pprint.txt")
        if not os.path.exists(currdir+"soln_pprint.txt"):
           self.fail("test_write_solution - failed to write soln_pprint.txt")
        self.failUnlessFileEqualsBaseline(currdir+"soln_pprint.txt", currdir+"test3_soln.txt")

    def test_soln_pprint2(self):
        """ Write a solution with only zero values, using the Solution.pprint() method """
        self.soln.variable[1]=0.0
        self.soln.variable[2]=0.0
        self.soln.variable[4]=0.0
        pyutilib.misc.setup_redirect(currdir+"soln_pprint2.out")
        print self.soln
        print self.soln.variable
        pyutilib.misc.reset_redirect()
        self.failUnlessFileEqualsBaseline(currdir+"soln_pprint2.out", currdir+"soln_pprint2.txt")

    def test_soln_suffix_iter(self):
        """ Test a suffix iterator """
        self.soln.variable[1]=0.0
        self.soln.variable[2]=0.1
        self.soln.variable[4]=0.3
        i=0
        for key in self.soln.variable:
          i=i+1
          self.failUnlessEqual(self.soln.variable[key].value, self.soln.variable[key].id/10.0)
        self.failUnlessEqual(i,len(self.soln.variable))

    def test_soln_suffix_getiter(self):
        self.soln.variable["x0"]=0.0
        self.soln.variable[2]=0.1
        self.soln.variable["x3"]=0.3
        self.failUnlessEqual(self.soln.variable["x3"].value,0.3)
        #print "HERE",self.soln.variable._names
        self.failUnlessEqual(self.soln.variable[2].value,0.1)

    def test_soln_suffix_setattr(self):
        self.soln.variable["x(0)"] = 0.0
        self.soln.variable["x3"]=0.3
        self.soln.variable["x3"].slack=0.4
        self.soln.variable["y[1,ab]"]=0.5
        #self.soln.variable.z[0,'a']=2.0
        #print "HERE",self.soln.variable._names
        #print "HERE",self.soln.variable.__dict__.keys()
        #print "HERE",self.soln.variable.keys()
        #print "HERE",self.soln.variable.__getitem__('y[1,ab]')
        #print "HERE",repr(self.soln.variable.x)
        #print "HERE",repr(self.soln.variable.x[0])
        #print "HERE",repr(self.soln.variable.y)
        #print "HERE",repr(self.soln.variable.y[1,'ab'])
        #print "HERE",repr(self.soln.variable.z)
        #print "HERE",repr(self.soln.variable.z[0,'a'])
        #print "HERE",repr(self.soln.variable.foo('x(0)'))
        #self.soln.pprint()
        #print "HERE", self.soln.variable._index.keys()
        self.failUnlessEqual(self.soln.variable.x.keys(),[0])
        self.failUnlessEqual(self.soln.variable.x[0].value,0.0)
        self.failUnlessEqual(self.soln.variable.x3.value,0.3)
        self.failUnlessEqual(self.soln.variable.x3.slack,0.4)
        self.failUnlessEqual(self.soln.variable.y.keys(),[(1,'ab')])
        self.failUnlessEqual(self.soln.variable.y[1,'ab'].value,0.5)


if __name__ == "__main__":
    import pyutilib.misc
    #sys.settrace(pyutilib.misc.traceit)
    unittest.main()
