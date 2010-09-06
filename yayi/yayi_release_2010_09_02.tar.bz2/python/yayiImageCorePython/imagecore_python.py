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

#print dir(YAI)

class ImageTestCase(unittest.TestCase):
  def setUp(self):
    self.image = YAI.ImageFactory(YAC.type(YAC.c_scalar, YAC.s_ui8), 2)

  def tearDown(self):
    if(not self.image is None): del self.image

  def testType(self):
    self.assert_(self.image.DynamicType() == YAC.type(YAC.c_scalar, YAC.s_ui8), 'bad image type :' + str(self.image.DynamicType()))
    self.assert_(str(self.image).find(str(YAC.type(YAC.c_scalar, YAC.s_ui8))), 'image seems to have a bad description :' + str(self.image))


  def testDefaultSize(self):
    self.image.SetSize((10,10))
    self.assert_(self.image.GetSize() == (10, 10), 'error on set size (1)' + str(self.image.GetSize()) + " != " + str((10, 10)))

    self.image.SetSize((20,10))
    self.assert_(self.image.GetSize() == (20, 10), 'error on set size (2)')

    self.image.Size = (20,11)
    self.assert_(self.image.GetSize() == (20, 11), 'error on set size (3)')

    self.image.Size = (23,11)
    self.assert_(self.image.Size == (23, 11), 'error on set size (4)')

    self.assertRaises(exceptions.RuntimeError, self.image.SetSize, (-4,150))
    self.assertRaises(exceptions.RuntimeError, self.image.SetSize, (0,0))

    self.image.AllocateImage()
    self.assert_(self.image.Size == (23, 11), 'error on set size (5) : ' + str(self.image.Size) + ' != ' + str((23, 11)))


  def testResizeWhileSet(self):
    self.image.Size = (23,11)
    self.assert_(self.image.Size == (23, 11), 'error on set size')
    self.image.AllocateImage()
    self.assertRaises(exceptions.RuntimeError, self.image.SetSize, (100,150))
    self.image.FreeImage()
    self.image.SetSize((100,150))
    #self.assert_(self.image.SetSize((100,150)), 'sizing while freed does not work')
    self.assert_(self.image.Size == (100,150), 'error on set size')
    

class ImagePixelTestCase(unittest.TestCase):
  def setUp(self):
    self.image = YAI.ImageFactory(YAC.type(YAC.c_scalar, YAC.s_ui8), 2)

  def tearDown(self):
    del self.image
    
  def testPixel(self):
    self.image.SetSize((10,10))
    self.assert_(self.image.GetSize() == (10, 10), 'error on set size' + str(self.image.GetSize()) + " != " + str((10, 10)))
    self.assertRaises(exceptions.RuntimeError, self.image.pixel, (0,10)) # should raise an error since the image is not allocated
    self.image.AllocateImage()

    p = self.image.pixel((0, 9))
    p.value = 0
    self.assert_(p.value == 0, "the value of the pixel is not 0")
    
    del self.image
    #self.image = None
    b = True
    try:
      p.value = 10
    except Exception, e:
      b = False

    self.assert_(b, "it seems that the pixel's lifetime is not correctly bound to the image's lifetime")

    #print p.value
    del p
    try:
      print self.image
    except Exception, e:
      b = False    

    self.assert_(not b,"it seems that the pixel's lifetime is not correctly bound to the image's lifetime")
    self.image = None
    



class ImageIteratorTestCase(unittest.TestCase):
  def setUp(self):
    self.image = YAI.ImageFactory(YAC.type(YAC.c_scalar, YAC.s_ui8), 2)

  def tearDown(self):
    del self.image
    
  def testIterator(self):
    self.image.SetSize((10,10))
    self.assert_(self.image.GetSize() == (10, 10), 'error on set size' + str(self.image.GetSize()) + " != " + str((10, 10)))
    
    #self.assertRaises(exceptions.RuntimeError, self.image.pixels) # should raise an error since the image is not allocated
    self.image.AllocateImage()
    print 'Image allocated'

    c = 0
    it = self.image.pixels
    print 'Iterator got'    
    while True:
      self.failUnless(c < (self.image.Size[0] * self.image.Size[1] + 10), 'the iterator does not seem to stop')
      
      try:
        #print 2
        print '.', c, 'pos', it.position
        it.value = c
        print '.', c, 'pos set', it.position
        v = it.next()
        self.assert_(v == c, 'error on the pixel\' value : ' + str(v) + ' != ' + str(c))
      except StopIteration, e: break
      except Exception, e:
        print 'Caught exception', e
        break

      c += 1
      
    self.assert_(c == self.image.Size[0] * self.image.Size[1], 'error on the number of pixel iterated : ' + str(c) + ' != ' + str(self.image.Size[0] * self.image.Size[1]))
    
    
    

def suite():
  suite = unittest.TestSuite()
  suite.addTest(ImageTestCase('testType'))
  suite.addTest(ImageTestCase('testDefaultSize'))
  suite.addTest(ImageTestCase('testResizeWhileSet'))
  
  suite.addTest(ImagePixelTestCase('testPixel'))
  
  suite.addTest(ImageIteratorTestCase('testIterator'))
  return suite




def create_image():
  toto = YAI.ImageFactory(tt, 2)
  print toto
  print toto.DynamicType()
  print toto.IsAllocated()
  print toto.Size
  return toto

def set_size_test(image):
  image.SetSize((10,10))
  #toto.SetSize(("val",True))
  image.AllocateImage()
  print image.Size
  image.Size = (20,20)
  print image.Size
  
  
if __name__ == '__main__':
  ret = unittest.TextTestRunner(verbosity=3).run(suite())
  if(not ret.wasSuccessful()):
    sys.exit(-1)
