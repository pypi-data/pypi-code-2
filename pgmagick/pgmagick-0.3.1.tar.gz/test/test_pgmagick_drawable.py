# coding: utf-8
import sys
import unittest
sys.path.append('../')
sys.path.append('./')
from pgmagick import Image, Geometry, Color
from pgmagick import DrawableAffine, DrawableCompositeImage, DrawableText


class TestDrawableAffine(unittest.TestCase):

    def test_affine_nonarg(self):
        drawer = DrawableAffine()
        self.assertEqual(type(drawer), DrawableAffine)

    def test_affine_arg(self):
        drawer = DrawableAffine(0.1, 0.1, 0.1, 0.1, 0.1, 0.1)
        self.assertEqual(type(drawer), DrawableAffine)


class TestDrawableCompositeImage(unittest.TestCase):

    def test_arg_d_d_str(self):
        DrawableCompositeImage(10, 10, "./t.png")

    def test_arg_d_d_img(self):
        img = Image(Geometry(50, 50), Color('red'))
        base_img = Image(Geometry(300, 300), Color('transparent'))
        base_img.draw(DrawableCompositeImage(10, 10, img))
        base_img.write('t.png')


class TestDrawableText(unittest.TestCase):

    def test_text_japanese(self):
        DrawableText(20, 300, "は")

unittest.main()
