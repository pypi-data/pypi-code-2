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
import sys
import re

import pyutilib.autotest
from pyutilib.component.core import *
import pyutilib.services
from pyutilib.misc import Options

import coopr.opt

class PyomoTestDriver(Plugin):

    implements(pyutilib.autotest.ITestDriver)
    alias('coopr.pyomo')

    def setUpClass(self, cls, options):
        try:
            cls.pico_convert =  pyutilib.services.registered_executable("pico_convert")
            cls.pico_convert_available= (not cls.pico_convert is None)
        except pyutilib.common.ApplicationError:
            cls.pico_convert_available=False

    def tearDownClass(self, cls, options):
        pass

    def setUp(self, testcase, options):
        global tmpdir
        tmpdir = os.getcwd()
        os.chdir(options.currdir)
        pyutilib.services.TempfileManager.sequential_files(0)
        pyutilib.services.TempfileManager.tempdir = options.currdir
        #
        if ':' in options.solver:
            solver, sub_solver = options.solver.split(':')
            if options.solver_options is None:
                _options = Options()
            else:
                _options = options.solver_options
            _options.solver = sub_solver
            testcase.opt = coopr.opt.SolverFactory(solver, options=_options)
        else:
            testcase.opt = coopr.opt.SolverFactory(options.solver, options=options.solver_options)
        if testcase.opt is None or not testcase.opt.available(False):
            testcase.skipTest('Solver %s is not available' % options.solver)
        else:
            testcase.opt.suffixes = ['.*']

    def tearDown(self, testcase, options):
        global tmpdir
        pyutilib.services.TempfileManager.clear_tempfiles()
        os.chdir(tmpdir)
        pyutilib.services.TempfileManager.unique_files()

    def pyomo(self, cmd, **kwds):
        import coopr.pyomo.scripting.pyomo as main
        sys.stdout.flush()
        sys.stderr.flush()
        print "Running: pyomo "+cmd
        args = re.split('[ ]+',cmd)
        output = main.run(list(args))
        return output

    def run_test(self, testcase, name, options):
        if options.verbose or options.debug:
            print "Test %s - Running pyomo with options %s" % (name, str(options))
        #
        print options
        if options.files is None:
            files = options.problem+'.py'
            if os.path.exists(options.problem+'.dat'):
                files += ' '+options.problem+'.dat'
        else:
            files = options.files
        #
        root = options.solver+'_'+options.problem
        self.pyomo('-w -c --solver=%s --output=%s --save-results=%s %s' % (options.solver, root+'.log', root+'.out', files))
        #
        if options.baseline is None:
            baseline = options.problem+'.yml'
        else:
            baseline = options.baseline
        baseline = pyutilib.misc.load_yaml( pyutilib.misc.extract_yaml( baseline ) )
        results = pyutilib.misc.load_yaml( pyutilib.misc.extract_yaml( root+'.out' ) )
        #
        if options.tolerance is None:
            tol = 1e-7
        else:
            tol = options.tolerance
        #
        pyutilib.misc.compare_yaml_repn( baseline, results, tolerance=tol, exact=False)
        os.remove(root+'.out')
        os.remove(root+'.log')

