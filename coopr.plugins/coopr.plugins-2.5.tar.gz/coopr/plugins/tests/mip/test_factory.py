#
# Unit Tests for util/misc
#
#

import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+"/../..")
cooprdir = dirname(abspath(__file__))+"/../.."
currdir = dirname(abspath(__file__))+os.sep

import unittest
from nose.tools import nottest
import coopr.opt
import coopr.plugins.mip
import coopr
import pyutilib.services
import pyutilib.component.core


class TestWriter(coopr.opt.AbstractProblemWriter):

    pyutilib.component.core.alias('wtest3')

    def __init__(self, name=None):
        coopr.opt.AbstractProblemWriter.__init__(self,name)
    

class TestReader(coopr.opt.AbstractResultsReader):

    pyutilib.component.core.alias('rtest3')

    def __init__(self, name=None):
        coopr.opt.AbstractResultsReader.__init__(self,name)
    

class TestSolver(coopr.opt.OptSolver):

    pyutilib.component.core.alias('stest3')

    def __init__(self, **kwds):
        kwds['type'] = 'stest_type'
        kwds['doc'] = 'TestSolver Documentation'
        coopr.opt.OptSolver.__init__(self,**kwds)

    def enabled(self):
        return False


class OptFactoryDebug(unittest.TestCase):

    def setUp(self):
        pyutilib.services.TempfileManager.tempdir = currdir

    def tearDown(self):
        pyutilib.services.TempfileManager.clear_tempfiles()

    def test_solver_factory(self):
        """
        Testing the coopr.opt solver factory with MIP solvers
        """
        ans = sorted(coopr.opt.SolverFactory.services())
        tmp = ['_mock_asl', '_mock_cbc', '_mock_cplex', '_mock_glpk', '_mock_pico', 'cbc', 'cplex', 'glpk', 'pico', 'stest3', 'asl']
        tmp.sort()
        self.failUnless(set(tmp) <= set(ans), msg="Set %s is not a subset of set %s" %(tmp,ans))

    def test_solver_instance(self):
        """
        Testing that we get a specific solver instance
        """
        ans = coopr.opt.SolverFactory("none")
        self.failUnlessEqual(ans, None)
        ans = coopr.opt.SolverFactory("_mock_pico")
        self.failUnlessEqual(type(ans), coopr.plugins.mip.MockPICO)
        ans = coopr.opt.SolverFactory("_mock_pico", name="mymock")
        self.failUnlessEqual(type(ans), coopr.plugins.mip.MockPICO)
        self.failUnlessEqual(ans.name,  "mymock")

    def test_solver_registration(self):
        """
        Testing methods in the solverwriter factory registration process
        """
        coopr.opt.SolverFactory.deactivate('stest3')
        self.failUnless(not 'stest3' in coopr.opt.SolverFactory.services())
        coopr.opt.SolverFactory.activate('stest3')
        self.failUnless('stest3' in coopr.opt.SolverFactory.services())
        self.failUnless('_mock_pico' in coopr.opt.SolverFactory.services())

    def test_writer_factory(self):
        """
        Testing the coopr.opt writer factory with MIP writers
        """
        factory = coopr.opt.WriterFactory.services()
        self.failUnless(set(['wtest3']) <= set(factory))

    def test_writer_instance(self):
        """
        Testing that we get a specific writer instance

        Note: this simply provides code coverage right now, but
        later it should be adapted to generate a specific writer.
        """
        ans = coopr.opt.WriterFactory("none")
        self.failUnlessEqual(ans, None)
        ans = coopr.opt.WriterFactory("wtest3")
        self.failIfEqual(ans, None)
        #ans = coopr.opt.WriterFactory("wtest", "mywriter")
        #self.failIfEqual(ans, None)
        #self.failIfEqual(ans.name, "mywriter")

    def test_writer_registration(self):
        """
        Testing methods in the writer factory registration process
        """
        coopr.opt.WriterFactory.deactivate('wtest3')
        self.failUnless(not 'wtest3' in coopr.opt.WriterFactory.services())
        coopr.opt.WriterFactory.activate('wtest3')
        self.failUnless('wtest3' in coopr.opt.WriterFactory.services())


    def test_reader_factory(self):
        """
        Testing the coopr.opt reader factory
        """
        ans = coopr.opt.ReaderFactory.services()
        #self.failUnlessEqual(len(ans),4)
        self.failUnless(set(ans) >= set(["rtest3", "sol","yaml"]))

    def test_reader_instance(self):
        """
        Testing that we get a specific reader instance
        """
        ans = coopr.opt.ReaderFactory("none")
        self.failUnlessEqual(ans, None)
        ans = coopr.opt.ReaderFactory("sol")
        self.failUnlessEqual(type(ans), coopr.opt.reader.sol.ResultsReader_sol)
        #ans = coopr.opt.ReaderFactory("osrl", "myreader")
        #self.failUnlessEqual(type(ans), coopr.opt.reader.OS.ResultsReader_osrl)
        #self.failUnlessEqual(ans.name, "myreader")

    def test_reader_registration(self):
        """
        Testing methods in the reader factory registration process
        """
        coopr.opt.ReaderFactory.deactivate('rtest3')
        self.failUnless(not 'rtest3' in coopr.opt.ReaderFactory.services())
        coopr.opt.ReaderFactory.activate('rtest3')
        self.failUnless('rtest3' in coopr.opt.ReaderFactory.services())

if __name__ == "__main__":
   unittest.main()

