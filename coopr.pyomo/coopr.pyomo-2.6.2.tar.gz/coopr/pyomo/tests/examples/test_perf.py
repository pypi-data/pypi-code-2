#
# Test the Pyomo command-line interface
#

import os
import sys
from os.path import abspath, dirname
currdir = dirname(abspath(__file__))+os.sep
datadir = os.path.normpath(currdir+'../../../../examples/pyomo/p-median/')+os.sep

from coopr.pyomo import *
import pyutilib.th as unittest
import coopr.pyomo.scripting.convert as convert
import re
import glob

class Test(unittest.TestCase):

    def setUp(self):
        self.cwd = os.getcwd()
        os.chdir(currdir)

    def tearDown(self):
        os.chdir(self.cwd)

    def test1(self):
        convert.pyomo2nl(['--save-model',currdir+'test1.nl','pmedian.py','pmedian.dat'])
        if not os.path.exists(currdir+'test1.nl'):
            raise ValueError, "Missing file test1.nl generated in test1"
        os.remove(currdir+'test1.nl')

    def test2(self):
        convert.pyomo2lp(['--save-model',currdir+'test2.lp','pmedian.py','pmedian.dat'])
        if not os.path.exists(currdir+'test2.lp'):
            raise ValueError, "Missing file test2.lp generated in test2"
        os.remove(currdir+'test2.lp')

Test = unittest.category('performance')(Test)

@unittest.nottest
def nl_test(self, suite, name):
    fname = currdir+name+'.nl'
    root = name.split('_')[1]
    #print >>sys.stderr, fname
    convert.pyomo2nl(['--save-model',fname]+self._options[suite,name]+[datadir+root+'.dat'])
    if not os.path.exists(fname):
        raise ValueError, "Missing file %s generated in test2" % fname
    os.remove(fname)

@unittest.nottest
def lp_test(self, suite, name):
    fname = currdir+name+'.lp'
    root = name.split('_')[1]
    #print >>sys.stderr, fname
    convert.pyomo2lp(['--save-model',fname]+self._options[suite,name]+[datadir+root+'.dat'])
    if not os.path.exists(fname):
        raise ValueError, "Missing file %s generated in test2" % fname
    os.remove(fname)


for i in range(8):
    name = 'test'+str(i+1)
    #
    Test.add_fn_test(Test, fn=nl_test, name='nl_pmedian.'+name, options=[datadir+'pmedian.py'])
    Test.add_fn_test(Test, fn=nl_test, name='nl-O_pmedian.'+name, options=['--disable-gc', datadir+'pmedian.py'] )
    #
    Test.add_fn_test(Test, fn=lp_test, name='lp_pmedian.'+name, options=[datadir+'pmedian.py'])
    Test.add_fn_test(Test, fn=lp_test, name='lp-O_pmedian.'+name, options=['--disable-gc', datadir+'pmedian.py'] )
    #
    #Test.add_fn_test(Test, fn=nl_test, name='nl_pmedian_v2.'+name, options=[datadir+'pmedianv2.py'])
    #Test.add_fn_test(Test, fn=nl_test, name='nl-O_pmedian_v2.'+name, options=['--disable-gc', datadir+'pmedianv2.py'] )
    #
    #Test.add_fn_test(Test, fn=lp_test, name='lp_pmedian_v2.'+name, options=[datadir+'pmedianv2.py'])
    #Test.add_fn_test(Test, fn=lp_test, name='lp-O_pmedian_v2.'+name, options=['--disable-gc', datadir+'pmedianv2.py'] )


if __name__ == "__main__":
   unittest.main()
