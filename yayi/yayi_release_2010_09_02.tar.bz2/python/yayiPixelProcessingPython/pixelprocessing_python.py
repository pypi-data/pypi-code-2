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
import YayiPixelProcessingPython as YAPIX

class PixelProcessTestCase(unittest.TestCase):
  def setUp(self):
    self.image = YAI.ImageFactory(YAC.type(YAC.c_scalar, YAC.s_ui16), 2)
    self.image3D = YAI.ImageFactory(YAC.type(YAC.c_scalar, YAC.s_ui16), 3)
    

  def tearDown(self):
    if(not self.image is None): del self.image

  def test1(self):
    self.assert_(self.image.DynamicType() == YAC.type(YAC.c_scalar, YAC.s_ui16), 'bad image type :' + str(self.image.DynamicType()))
    self.assert_(self.image3D.DynamicType() == YAC.type(YAC.c_scalar, YAC.s_ui16), 'bad image type :' + str(self.image.DynamicType()))

    s = (130, 140, 11)
    self.image.Size = s[:2]
    self.image.AllocateImage()
    self.assert_(self.image.Size == s[:2], 'error on set size : ' + str(self.image.Size) + ' != ' + str(s[:2]))

    self.image3D.Size = s
    self.image3D.AllocateImage()
    self.assert_(self.image3D.Size == s, 'error on set size : ' + str(self.image.Size) + ' != ' + str(s))

    print 'Preparing 3D image'
    i = 0
    it = self.image3D.pixels
    
    while it.has_next():
      try:
        it.value =  i % 17
        v = it.next()
        self.assert_(v == i % 17, 'error on the pixel\' value : ' + str(v) + ' != ' + str(i % 17))
      except StopIteration, e:
          print "Stopped iteration", e
          print it.position
          break
      except Exception, e:
          print 'Caught exception at position', it.position, e
          raise

      i += 1

    self.assert_(i == reduce(lambda x,y:x*y, s, 1), 'bad number of points : ' + str(i) + ' != ' + str(reduce(lambda x,y:x*y, s, 1)))
    print 'Testing windowed copies...'
    
    for i in range(s[2]):
      print '\tSlice', i
      
      #YAPIX.CopyWindow(self.image3D, YAC.HyperRectangle([0]*2 + [i], list(s[:2]) + [i]), YAC.HyperRectangle((0,0), self.image.Size), self.image)
      origin_size = ([0]*2 + [i], list(s[:2]) + [1])
      print 'copy from', origin_size , 'to', ((0,0), self.image.Size)
      YAPIX.CopyWindow(self.image3D, origin_size, ((0,0), self.image.Size), self.image)
      
      k = s[0]*s[1] * i
      print 'k', k
      it = self.image.pixels
      while it.has_next():
        
        try:
          self.assert_(it.value == k % 17, 'error on the pixel\' value : ' + str(it.value) + ' != ' + str(k % 17) + ' coordinate ' + str(it.GetPosition()))
          it.next()
        except StopIteration, e: 
          print "Stopped iteration", e
          break
        except Exception, e:
          print 'Caught exception at position', it.position, e
          raise

        k += 1
      pass

    pass

def suite():
  suite = unittest.TestSuite()
  suite.addTest(PixelProcessTestCase('test1'))

  return suite
  
  
if __name__ == '__main__':
  ret = unittest.TextTestRunner(verbosity=3).run(suite())
  if(not ret.wasSuccessful()):
    sys.exit(-1)
