#!/usr/bin/env python

import libxml2dom.svg

# NOTE: Need to incorporate unit conversion.

xscale, yscale = 3.75, 3.75

d = libxml2dom.svg.parse("tests/test_svg.xml")
svg = d.documentElement
path = svg.xpath(".//svg:path")[0]
m = svg.createSVGMatrixComponents(1, 0, 0, 1, 0, 0)
m.mTranslate(-20 * xscale, -30 * yscale)
m.mRotate(60)
m.mTranslate(20 * xscale, 30 * yscale)
path.setMatrixTrait("transform", m)
d.toFile(open("tmp_test.svg", "wb"))

# vim: tabstop=4 expandtab shiftwidth=4
