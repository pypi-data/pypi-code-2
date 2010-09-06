#  -*- coding=UTF-8 -*-
#  -:- LICENCE -:- 
# Copyright Raffi Enficiaud 2007-2010
# 
# Distributed under the Boost Software License, Version 1.0.
# (See accompanying file ../LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
# 
#  -:- LICENCE -:- 
#

#!/usr/bin/env python2.3

import os, sys
print os.path.abspath(os.curdir)

sys.path.insert(0, os.path.abspath(os.curdir))


import YayiCommonPython as COM
import YayiIOPython as IO
import YayiImageCorePython as CORE
im = IO.readJPG(os.path.join(os.path.split(__file__)[0], os.path.pardir, "coreTests", "yayiTestData", "release-grosse bouche.jpg"))

im1 = CORE.ImageFactory(COM.type(COM.c_scalar, COM.s_ui8), im.GetDimension())
im1.SetSize(im.GetSize())
im1.AllocateImage()

print "Images definitions"
print "im", im
print "im1", im1

import YayiPixelProcessingPython as PIX
PIX.CopyOneChannel(im, 0, im1)
IO.writePNG("toto.png", im1)

print "First channel of the image has been saved"

import YayiLowLevelMorphologyPython as MORPH
import YayiStructuringElementPython as SE

toto = SE.SESquare2D()
neigh = SE.NeighborhoodFactory(im1, toto)

#out = CORE.ImageFactory(im.DynamicType(), 2)
#out.SetSize(im.GetSize())
out = CORE.GetSameImage(im1)
print 'Erosion...'
MORPH.Erosion(im1, toto, out)
print 'Erosion ok...'
IO.writePNG("toto_erode.png", out)

print "The erosion of the first channel of the image has been saved"