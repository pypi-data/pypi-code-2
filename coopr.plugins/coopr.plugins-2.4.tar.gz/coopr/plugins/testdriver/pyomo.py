#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________
#

import os
import os.path
import pyutilib.autotest
from pyutilib.component.core import *
import pyutilib.services
import coopr.pyomo


class PyomoTestDriver(Plugin):

    implements(pyutilib.autotest.ITestDriver)
    alias('pyomo')

    def setUpClass(self, cls, options):
        pass

    def tearDownClass(self, cls, options):
        pass

    def setUp(self, testcase, options):
        # TODO: rework
        global tmpdir
        tmpdir = os.getcwd()
        os.chdir(options.currdir)
        pyutilib.services.TempfileManager.sequential_files(0)
        pyutilib.services.TempfileManager.tempdir = options.currdir
        #
        testcase.opt = coopr.opt.SolverFactory(options.solver, options=options.solver_options)
        if testcase.opt is None:
            testcase.skipTest('Solver %s is not available' % options.solver)
        else:
            testcase.opt.suffixes = ['.*']

    def tearDown(self, testcase, options):
        # TODO: rework
        global tmpdir
        pyutilib.services.TempfileManager.clear_tempfiles()
        os.chdir(tmpdir)
        pyutilib.services.TempfileManager.unique_files()

    def run_test(self, testcase, name, options):
        # TODO: rework
        if options.verbose or options.debug:
            print "Test %s - Running coopr.opt solver with options %s" % (name, str(options))
        if options.use_pico_convert and testcase.pico_convert_available:
            if options.results_format:
                results = testcase.opt.solve(options.currdir+options.files, rformat=coopr.opt.ResultsFormat(options.results_format), logfile=options.currdir+name+".log")
            else:
                results = testcase.opt.solve(options.currdir+options.files, logfile=options.currdir+name+".log")
            baseline = pyutilib.misc.load_yaml( pyutilib.misc.extract_yaml( options.baseline ) )
            if options.tolerance is None:
                tol = 1e-7
            else:
                tol = options.tolerance
            pyutilib.misc.compare_yaml_repn( baseline, results, tolerance=tol, exact=False)
            #results.write(filename=options.currdir+name+".txt", ignore_time=True)
            #testcase.failUnlessFileEqualsBaseline(options.currdir+name+".txt", options.baseline)
        else:
            try:
                if options.results_format:
                    results = testcase.opt.solve(options.currdir+options.files, rformat=coopr.opt.ResultsFormat(options.results_format), logfile=options.currdir+name+".log")
                else:
                    results = testcase.opt.solve(options.currdir+options.files, logfile=options.currdir+name+".log")
            except coopr.opt.ConverterError:
                pass
        if os.path.exists(options.currdir+name+".log"):
            os.remove(options.currdir+name+".log")

