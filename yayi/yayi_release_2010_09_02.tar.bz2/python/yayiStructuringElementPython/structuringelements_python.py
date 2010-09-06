#  -*- coding=UTF-8 -*-
#  -:- LICENCE -:- 
# Copyright Raffi Enficiaud 2007-2010
# 
# Distributed under the Boost Software License, Version 1.0.
# (See accompanying file ../../LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
# 
#  -:- LICENCE -:- 
#

#  -*- coding=UTF-8 -*-


# structuring element tests

import os, sys, unittest, exceptions

if(globals().has_key('__file__')):
  sys.path.insert(0, os.path.join(os.path.split(__file__)[0], os.path.pardir, "yayiCommonPython"))
from common_test import *
import YayiStructuringElementPython as yaSE
import YayiImageCorePython          as yaCORE

class SECreateCase(unittest.TestCase):
  def setUp(self):
    self.image2D = yaCORE.ImageFactory(YAC.type(YAC.c_scalar, YAC.s_ui8), 2)
    self.image3D = yaCORE.ImageFactory(YAC.type(YAC.c_scalar, YAC.s_ui16), 3)
    
    self.image2D.Size = (10, 10)
    self.image2D.AllocateImage()

    self.image3D.Size = (10, 15, 20)
    self.image3D.AllocateImage()
    
    

  def tearDown(self):
    del self.image2D
    del self.image3D
    
    
  def testCreateSE(self):
  
    se = yaSE.SEFactory(yaSE.e_set_neighborlist, 2, (0,1, 0,0, 0,-1), yaSE.e_sest_neighborlist_generic_single)
    self.assert_(not (se is None))
    self.assert_(se == se)
    self.assert_(se % se)
    
    self.assert_(se != yaSE.SEHex2D())
    self.assert_(se != yaSE.SESquare2D())
    self.assert_(se != yaSE.SESquare2D())
    self.assert_(se % yaSE.SESegmentY2D())

    se2 = yaSE.SEFactory(yaSE.e_set_neighborlist, 2, (0,-1, 0,0, 0,1), yaSE.e_sest_neighborlist_generic_single)
    self.assert_(se != se2)
    self.assert_(se % se2)
    
    del se
  
  def testCloneOk(self):
    self.assert_(yaSE.SEHex2D().SEType == yaSE.e_set_neighborlist)
    self.assert_(yaSE.SEHex2D().SETSubtype == yaSE.e_sest_neighborlist_hexa)
  
  def testNeighborhood(self):
    se = yaSE.SEFactory(yaSE.e_set_neighborlist, 2, (0,1, 0,0, 0,-1), yaSE.e_sest_neighborlist_generic_single)
    self.assert_(not se is None)

    neighbor = yaSE.NeighborhoodFactory(self.image2D, se)
    self.assert_(not (neighbor is None))
    
    neighbor.Center((5, 5))
    i = 0
    for n in neighbor.pixels:
      i += 1
    
    self.assert_(i == 3)

    neighbor.Center((5, 0))
    i = 0
    for n in neighbor.pixels:
      i += 1
    
    self.assert_(i == 2)



def suite():
  suite = unittest.TestSuite()
  
  suite.addTest(SECreateCase('testCreateSE'))
  suite.addTest(SECreateCase('testNeighborhood'))
  suite.addTest(SECreateCase('testCloneOk'))
  return suite


if __name__ == '__main__':
  ret = unittest.TextTestRunner(verbosity=3).run(suite())
  if(not ret.wasSuccessful()):
    sys.exit(-1)


