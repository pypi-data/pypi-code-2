# coding: utf-8
import sys
import unittest
sys.path.append('../')
sys.path.append('./')
from pgmagick import Image, Geometry, Color, DrawableText


class TestImage(unittest.TestCase):

    def test_text_utf8(self):
        im = Image(Geometry(300, 200), Color('transparent'))
        #im.font("/usr/share/fonts/truetype/ipafont/ipag.ttf")
        im.font("/usr/share/fonts/truetype/ttf-japanese-gothic.ttf")
        im.fontPointsize(40)
        im.draw(DrawableText(20, 100, "HAはHa"))
        im.write('t.png')

unittest.main()
