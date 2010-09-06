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
import YayiImageCorePython as YAI
import YayiIOPython as YAIO
import YayiMeasurementsPython as YAMEAS

class MeasurementsTestCase(unittest.TestCase):
  def setUp(self):
    self.image = YAI.ImageFactory(YAC.type(YAC.c_scalar, YAC.s_ui8), 2)

  def tearDown(self):
    if(not self.image is None): del self.image

  def test1(self):
    self.assert_(self.image.DynamicType() == YAC.type(YAC.c_scalar, YAC.s_ui8), 'bad image type :' + str(self.image.DynamicType()))

    im = YAIO.readPNG(os.path.join(test_data_path, "release-grosse bouche.png"))
    hist = YAMEAS.meas_histogram(im)
    self.assert_(len(hist) == 21304, 'bad number of colours in the histogram : ' + str(len(hist)) + ' != 21304')
    j = 0
    for i in hist:
      j += i[1]
    
    self.assert_(j == im.Size[0] * im.Size[1], 'bad total count for the histogram')
    

def suite():
  suite = unittest.TestSuite()
  suite.addTest(MeasurementsTestCase('test1'))

  return suite
  
  
if __name__ == '__main__':
  ret = unittest.TextTestRunner(verbosity=3).run(suite())
  if(not ret.wasSuccessful()):
    sys.exit(-1)
