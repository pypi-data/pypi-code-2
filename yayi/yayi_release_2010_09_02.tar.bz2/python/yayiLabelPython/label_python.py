#  -*- coding=UTF-8 -*-
#  -:- LICENCE -:- 
# Copyright Raffi Enficiaud 2007-2010
# 
# Distributed under the Boost Software License, Version 1.0.
# (See accompanying file ../../LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
# 
#  -:- LICENCE -:- 
#

#!/usr/bin/env python2.3
#  -*- coding=UTF-8 -*-

import os, sys, unittest, exceptions

if(globals().has_key('__file__')):
  sys.path.insert(0, os.path.join(os.path.split(__file__)[0], os.path.pardir, "yayiCommonPython"))

from common_test import *
import YayiImageCorePython  as YAI
import YayiLabelPython      as YAL

class LabelTestCase(unittest.TestCase):
  def setUp(self):
    self.image = YAI.ImageFactory(YAC.type(YAC.c_scalar, YAC.s_ui8), 2)

  def tearDown(self):
    if(not self.image is None): del self.image

  def testLabel(self):
    #self.image.Size = (23,11)
    #self.assert_(self.image.Size == (23, 11), 'error on set size')
    #self.image.AllocateImage()
    #self.assertRaises(exceptions.RuntimeError, self.image.SetSize, (100,150))
    #self.image.FreeImage()
    #self.image.SetSize((100,150))
    #self.assert_(self.image.SetSize((100,150)), 'sizing while freed does not work')
    #self.assert_(self.image.Size == (100,150), 'error on set size')
    pass

def suite():
  suite = unittest.TestSuite()
  suite.addTest(LabelTestCase('testLabel'))
  return suite

if __name__ == '__main__':
  ret = unittest.TextTestRunner(verbosity=3).run(suite())
  if(not ret.wasSuccessful()):
    sys.exit(-1)
