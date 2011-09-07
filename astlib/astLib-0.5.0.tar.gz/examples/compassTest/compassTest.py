#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Test of contour plot

import pyfits
from astLib import *
import pylab 

TEST_IMAGE="../../../../testingData/testImage1.fits"
    
img=pyfits.open(TEST_IMAGE)
wcs=astWCS.WCS(TEST_IMAGE)
d=img[0].data

f=astPlots.ImagePlot(d, wcs, axes=[0,0,1,1])
f.addCompass("SW", 20.0)

f.draw()
f.save("output_compassTest.png")
