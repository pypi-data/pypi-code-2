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
import coopr
import pyutilib.services
import pyutilib.component.core


class TestWriter(coopr.opt.AbstractProblemWriter):

    pyutilib.component.core.alias('wtest')

    def __init__(self, name=None):
        coopr.opt.AbstractProblemWriter.__init__(self,name)
    

class TestReader(coopr.opt.AbstractResultsReader):

    pyutilib.component.core.alias('rtest')

    def __init__(self, name=None):
        coopr.opt.AbstractResultsReader.__init__(self,name)
    

class TestSolver(coopr.opt.OptSolver):

    pyutilib.component.core.alias('stest')

    def __init__(self, **kwds):
        kwds['type'] = 'stest_type'
        kwds['doc'] = 'TestSolver Documentation'
        coopr.opt.OptSolver.__init__(self,**kwds)

    def enabled(self):
        return False


class Test(unittest.TestCase):

    def run(self, result=None):
        unittest.TestCase.run(self,result)

    def setUp(self):
        coopr.opt.SolverFactory.activate('stest')
        coopr.opt.WriterFactory.activate('wtest')
        coopr.opt.ReaderFactory.activate('rtest')
        pyutilib.services.TempfileManager.tempdir = currdir

    def tearDown(self):
        pyutilib.services.TempfileManager.clear_tempfiles()
        coopr.opt.SolverFactory.deactivate('stest')
        coopr.opt.WriterFactory.deactivate('wtest')
        coopr.opt.ReaderFactory.deactivate('rtest')

    def test_solver_factory(self):
        """
        Testing the coopr.opt solver factory
        """
        ans = sorted(coopr.opt.SolverFactory.services())
        #self.failUnlessEqual(len(ans),8)
        self.failUnless(set(['stest']) <= set(ans))

    def test_solver_instance(self):
        """
        Testing that we get a specific solver instance
        """
        ans = coopr.opt.SolverFactory("none")
        self.failUnlessEqual(ans, None)
        ans = coopr.opt.SolverFactory("stest")
        self.failUnlessEqual(type(ans), TestSolver)
        ans = coopr.opt.SolverFactory("stest", name="mymock")
        self.failUnlessEqual(type(ans), TestSolver)
        self.failUnlessEqual(ans.name,  "mymock")

    def test_solver_registration(self):
        """
        Testing methods in the solverwriter factory registration process
        """
        coopr.opt.SolverFactory.deactivate("stest")
        self.failUnless(not 'stest' in coopr.opt.SolverFactory.services())
        coopr.opt.SolverFactory.activate("stest")
        self.failUnless('stest' in coopr.opt.SolverFactory.services())

    def test_writer_factory(self):
        """
        Testing the coopr.opt writer factory
        """
        factory = coopr.opt.WriterFactory.services()
        self.failUnless(set(['wtest']) <= set(factory))

    def test_writer_instance(self):
        """
        Testing that we get a specific writer instance

        Note: this simply provides code coverage right now, but
        later it should be adapted to generate a specific writer.
        """
        ans = coopr.opt.WriterFactory("none")
        self.failUnlessEqual(ans, None)
        ans = coopr.opt.WriterFactory("wtest")
        self.failIfEqual(ans, None)
        #ans = coopr.opt.WriterFactory("wtest", "mywriter")
        #self.failIfEqual(ans, None)
        #self.failIfEqual(ans.name, "mywriter")

    def test_writer_registration(self):
        """
        Testing methods in the writer factory registration process
        """
        coopr.opt.WriterFactory.deactivate("wtest")
        self.failUnless(not 'wtest' in coopr.opt.WriterFactory.services())
        coopr.opt.WriterFactory.activate("wtest")
        self.failUnless('wtest' in coopr.opt.WriterFactory.services())


    def test_reader_factory(self):
        """
        Testing the coopr.opt reader factory
        """
        ans = coopr.opt.ReaderFactory.services()
        self.failUnless(set(ans) >= set(["rtest", "sol","yaml"]))

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
        coopr.opt.ReaderFactory.deactivate("rtest")
        self.failUnless(not 'rtest' in coopr.opt.ReaderFactory.services())
        coopr.opt.ReaderFactory.activate("rtest")
        self.failUnless('rtest' in coopr.opt.ReaderFactory.services())

if __name__ == "__main__":
   unittest.main()

