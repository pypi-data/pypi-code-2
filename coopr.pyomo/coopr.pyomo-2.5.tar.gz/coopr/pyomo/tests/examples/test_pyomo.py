#
# Test the Pyomo command-line interface
#

import unittest
import os
import sys
from os.path import abspath, dirname
currdir = dirname(abspath(__file__))+os.sep
scriptdir = dirname(dirname(dirname(dirname(dirname(abspath(__file__))))))+os.sep

from coopr.pyomo import *
import pyutilib.services
import pyutilib.subprocess
import pyutilib.th as unittest
import coopr.pyomo.scripting.pyomo as main
import StringIO 
from pyutilib.misc import setup_redirect, reset_redirect
import re

if os.path.exists(sys.exec_prefix+os.sep+'bin'+os.sep+'coverage'):
    executable=sys.exec_prefix+os.sep+'bin'+os.sep+'coverage -x '
else:
    executable=sys.executable


class Test(unittest.TestCase):

    def pyomo(self, cmd, **kwds):
        args=re.split('[ ]+',cmd)
        if 'file' in kwds:
            OUTPUT=kwds['file']
        else:
            OUTPUT=StringIO.StringIO()
        setup_redirect(OUTPUT)
        os.chdir(currdir)
        output = main.run(list(args))
        reset_redirect()
        if not 'file' in kwds:
            return OUTPUT.getvalue()
        return output
        
    def test1(self):
        """Simple execution of 'pyomo'"""
        self.pyomo('pmedian.py pmedian.dat', file=currdir+'test1.out')
        self.failUnlessFileEqualsBaseline(currdir+"test1.out", currdir+"test1.txt")

    def test1a(self):
        """Simple execution of 'pyomo' with implicit rules"""
        self.pyomo('pmedian3.py pmedian.dat', file=currdir+'test1a.out')
        self.failUnlessFileEqualsBaseline(currdir+"test1a.out", currdir+"test1.txt")

    def test2(self):
        """Run pyomo with bad --model-name option value"""
        output=self.pyomo('--model-name=dummy pmedian.py pmedian.dat')
        self.failUnlessEqual(output.strip(),"Exiting pyomo: Neither 'dummy' nor 'pyomo_create_model' are available in module pmedian.py")

    def test3(self):
        """Run pyomo with model that does not define model object"""
        output=self.pyomo('pmedian1.py pmedian.dat')
        self.failUnlessEqual(output.strip(),"Exiting pyomo: Neither 'model' nor 'pyomo_create_model' are available in module pmedian1.py")

    def test4(self):
        """Run pyomo with good --model-name option value"""
        self.pyomo('--model-name=MODEL pmedian1.py pmedian.dat', file=currdir+'test4.out')
        self.failUnlessFileEqualsBaseline(currdir+"test4.out", currdir+"test1.txt")

    def test5(self):
        """Run pyomo with create_model function"""
        self.pyomo('pmedian2.py pmedian.dat', file=currdir+'test5.out')
        self.failUnlessFileEqualsBaseline(currdir+"test5.out", currdir+"test5.txt")

    def test6(self):
        """Run pyomo with help-components option"""
        self.pyomo('--help-components', file=currdir+'test6.out')
        self.failUnlessFileEqualsBaseline(currdir+"test6.out", currdir+"test6.txt")

    def Xtest7(self):
        """Run pyomo with help option"""
        self.pyomo('--help', file=currdir+'test7.out')
        self.failUnlessFileEqualsBaseline(currdir+"test7.out", currdir+"test7.txt")

    def test8(self):
        """Run pyomo with --instance-only option"""
        output = self.pyomo('--instance-only pmedian.py pmedian.dat', file=currdir+'test8.out')
        self.failUnlessEqual(type(output.instance), Model)
        os.remove(currdir+'test8.out')

    def test9(self):
        """Run pyomo with --disable-gc option"""
        output = self.pyomo('--disable-gc pmedian.py pmedian.dat', file=currdir+'test9.out')
        self.failUnlessEqual(type(output.instance), Model)
        os.remove(currdir+'test9.out')

    def test10(self):
        """Run pyomo with --verbose option"""
        def filter(line):
            #print "HERE",line
            return line.startswith("Writing")
        self.pyomo('-v pmedian.py pmedian.dat', file=currdir+'test10.out')
        self.failUnlessFileEqualsBaseline(currdir+"test10.out", currdir+"test10.txt", filter)

    def test11(self):
        """Run pyomo with --debug=generate option"""
        self.pyomo('--debug=generate pmedian.py pmedian.dat', file=currdir+'test11.out')
        self.failUnlessFileEqualsBaseline(currdir+"test11.out", currdir+"test11.txt")

    def test12(self):
        """Run pyomo with --logfile option"""
        self.pyomo('--debug=errors --logfile=%s pmedian.py pmedian.dat' % (currdir+'test12.log'), file=currdir+'test12.out')
        self.failUnlessFileEqualsBaseline(currdir+"test12.log", currdir+"test12.txt")
        os.remove(currdir+'test12.out')

Test = unittest.skipIf(pyutilib.services.registered_executable("glpsol") is None, "The 'glpsol' executable is not available")(Test)

if __name__ == "__main__":
   unittest.main()
