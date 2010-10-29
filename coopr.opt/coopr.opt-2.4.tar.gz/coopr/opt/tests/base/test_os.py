#
# Unit Tests for coopr.opt.base.OS
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
import xml
import pyutilib.th as unittest
import pyutilib.services

pyutilib.services.TempfileManager.tempdir = currdir

class Test(unittest.TestCase):

    def setUp(self):
        pyutilib.services.TempfileManager.tempdir = currdir
        #
        # Create OSrL object
        #
        self.osrl = coopr.opt.reader.OS.OSrL()
        #
        # Initialize header info
        #
        self.osrl.header.serviceURI=""
        self.osrl.header.serviceName=""
        self.osrl.header.instanceName=""
        self.osrl.header.time=0.0
        self.osrl.header.message=""
        self.osrl.header.jobID=0

    def tearDown(self):
        pyutilib.services.TempfileManager.clear_tempfiles()

    def test_write_solution(self):
        #
        # Initialize solutions
        #
        self.osrl.numVariables=4
        self.osrl.numObjectives=2
        self.osrl.numConstraints=4
        self.soln = self.osrl.add_solution()
        self.soln.status_description=""
        self.soln.variable[0]=1.2
        self.soln.variable[1]=1.2
        self.soln.variable[3]=1.2
        self.soln.objective[-1]=1.2
        self.soln.objective[-2]=1.2
        self.soln.dual[0]=1.2
        self.soln.dual[1]=1.2
        self.soln.dual[3]=1.2
        self.osrl.write(currdir+"write_solution.OSrL.xml")
        if not os.path.exists(currdir+"write_solution.OSrL.xml"):
           self.fail("test_write_solution - failed to write OSrL.xml")
        self.failUnlessFileEqualsBaseline(currdir+"write_solution.OSrL.xml",currdir+"test1.OSrL.xml")

    def test_None_values(self):
        self.osrl.read(currdir+"test1.OSrL.xml")
        self.osrl.header.serviceName=None
        self.osrl.header.serviceURI=None
        self.osrl.header.instanceName=None
        self.osrl.header.time=None
        self.osrl.header.message=None
        self.osrl.header.jobID=None
        OUTPUT = open(currdir+"None_values.OSrL.xml","w")
        self.osrl.write(OUTPUT)
        OUTPUT.close()
        if not os.path.exists(currdir+"None_values.OSrL.xml"):
           self.fail("test_write_solution - failed to write OSrL.xml")
        self.failUnlessFileEqualsBaseline(currdir+"None_values.OSrL.xml",currdir+"test7.OSrL.xml")

    def test_read_solution(self):
        self.osrl.read(currdir+"test1.OSrL.xml")
        self.failUnlessEqual(len(self.osrl),1)
        
    def test_bad_status(self):
        self.osrl.header.generalStatus=None
        try:
          self.osrl.validate()
          self.fail("test_bad_status - Error validating 'None' status.")
        except ValueError:
          pass

    def test_test2_error(self):
        try:
          self.osrl.read(currdir+"test2.OSrL.xml")
          self.fail("test_test2_error - Failed to find error in test2.OSrL.xml")
        except ValueError:
          pass

    def test_test3_error(self):
        try:
          self.osrl.read(currdir+"test3.OSrL.xml")
          self.fail("test_test3_error - Failed to find error in test3.OSrL.xml")
        except KeyError:
          pass

    def test_test4_error(self):
        try:
          self.osrl.read(currdir+"test4.OSrL.xml")
          self.fail("test_test4_error - Failed to find error in test4.OSrL.xml")
        except KeyError:
          pass

    def test_test5_error(self):
        try:
          self.osrl.read(currdir+"test5.OSrL.xml")
          self.fail("test_test5_error - Failed to find error in test5.OSrL.xml")
        except KeyError:
          pass

    def test_test6_error(self):
        try:
          self.osrl.read(currdir+"test6.OSrL.xml")
          self.fail("test_test6_error - Failed to find error in test6.OSrL.xml")
        except xml.parsers.expat.ExpatError:
          pass
        try:
          self.osrl.read(currdir+"test6.OSrL")
          self.fail("test_test6_error - Failed raise an error for a missing file")
        except IOError:
          pass

    def test_factory(self):
        reader = coopr.opt.ReaderFactory("osrl")
        soln = reader(currdir+"test1.OSrL.xml")
        soln.write(filename=currdir+"test_os.txt")
        #
        # Compare with baseline
        #
        self.failUnlessFileEqualsBaseline(currdir+"test_os.txt", currdir+"test1.txt")
        

if __name__ == "__main__":
   unittest.main()
