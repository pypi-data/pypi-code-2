import unittest
import sys
import os
sys.path.insert(0, os.path.abspath("pyrg"))
import pyrg


class ColorFunctionTest(unittest.TestCase):

    def test_coloring_method(self):
        line = "get_gg (__main__.TestTest)"
        self.assertEqual("[36mget_gg (__main__.TestTest)[0m",
                         pyrg.coloring_method(line))

    def test_ngroute(self):
        pass
        input_strings = """..
----------------------------------------------------------------------
Ran 2 tests in 0.000s

OK
"""
        result_strings = """[32m.[0m[32m.[0m
----------------------------------------------------------------------
Ran 2 tests in 0.000s

[32mOK[0m"""
        ret = pyrg.parse_unittest_result(input_strings.splitlines(1))
        self.assertEqual(ret, result_strings)


class TestColor(unittest.TestCase):

    def setUp(self):
        self.test_color_define = ['black', 'gray', 'red', 'pink', 'darkred',
                             'green', 'yellowgreen', 'darkgreen', 'brown',
                             'yellow', 'gold', 'blue', 'lightblue', 'darkblue',
                             'magenta', 'lightmagenta', 'darkmagenta',
                             'cyan', 'lightcyan', 'darkcyan', 'silver',
                             'white', 'darksilver']
        #self.test_color_define_offset += 1
        None

    def test_colormap_key_black(self):
        colorname = self.id().split('_')[-1]
        self.assertEqual(True, colorname in pyrg.COLOR_MAP)

    def test_colormap_key_gray(self):
        colorname = self.id().split('_')[-1]
        self.assertEqual(True, colorname in pyrg.COLOR_MAP)

    def test_colormap_key_red(self):
        colorname = self.id().split('_')[-1]
        self.assertEqual(True, colorname in pyrg.COLOR_MAP)

    def test_colormap_key_pink(self):
        colorname = self.id().split('_')[-1]
        self.assertEqual(True, colorname in pyrg.COLOR_MAP)

    def test_colormap_key_darkred(self):
        colorname = self.id().split('_')[-1]
        self.assertEqual(True, colorname in pyrg.COLOR_MAP)

    def test_colormap_key_green(self):
        colorname = self.id().split('_')[-1]
        self.assertEqual(True, colorname in pyrg.COLOR_MAP)

    def test_colormap_key_yellowgreen(self):
        colorname = self.id().split('_')[-1]
        self.assertEqual(True, colorname in pyrg.COLOR_MAP)

    def test_colormap_key_darkgreen(self):
        colorname = self.id().split('_')[-1]
        self.assertEqual(True, colorname in pyrg.COLOR_MAP)

    def test_colormap_key_brown(self):
        colorname = self.id().split('_')[-1]
        self.assertEqual(True, colorname in pyrg.COLOR_MAP)

    def test_colormap_key_yellow(self):
        colorname = self.id().split('_')[-1]
        self.assertEqual(True, colorname in pyrg.COLOR_MAP)

    def test_colormap_key_gold(self):
        colorname = self.id().split('_')[-1]
        self.assertEqual(True, colorname in pyrg.COLOR_MAP)

    def test_colormap_key_blue(self):
        colorname = self.id().split('_')[-1]
        self.assertEqual(True, colorname in pyrg.COLOR_MAP)

    def test_colormap_key_lightblue(self):
        colorname = self.id().split('_')[-1]
        self.assertEqual(True, colorname in pyrg.COLOR_MAP)

    def test_colormap_key_darkblue(self):
        colorname = self.id().split('_')[-1]
        self.assertEqual(True, colorname in pyrg.COLOR_MAP)

    def test_colormap_key_magenta(self):
        colorname = self.id().split('_')[-1]
        self.assertEqual(True, colorname in pyrg.COLOR_MAP)

    def test_colormap_key_lightmagenta(self):
        colorname = self.id().split('_')[-1]
        self.assertEqual(True, colorname in pyrg.COLOR_MAP)

    def test_colormap_key_darkmagenta(self):
        colorname = self.id().split('_')[-1]
        self.assertEqual(True, colorname in pyrg.COLOR_MAP)

    def test_colormap_key_cyan(self):
        colorname = self.id().split('_')[-1]
        self.assertEqual(True, colorname in pyrg.COLOR_MAP)

    def test_colormap_key_lightcyan(self):
        colorname = self.id().split('_')[-1]
        self.assertEqual(True, colorname in pyrg.COLOR_MAP)

    def test_colormap_key_darkcyan(self):
        colorname = self.id().split('_')[-1]
        self.assertEqual(True, colorname in pyrg.COLOR_MAP)

    def test_colormap_key_silver(self):
        colorname = self.id().split('_')[-1]
        self.assertEqual(True, colorname in pyrg.COLOR_MAP)

    def test_colormap_key_white(self):
        colorname = self.id().split('_')[-1]
        self.assertEqual(True, colorname in pyrg.COLOR_MAP)

    def test_colormap_key_darksilver(self):
        colorname = self.id().split('_')[-1]
        self.assertEqual(True, colorname in pyrg.COLOR_MAP)


class TestDummy(unittest.TestCase):

    def test_dummy_fail(self):
        self.assertEqual(1, 2)

    def test_dummy_error(self):
        self.assertEqual(1, a)


if __name__ == '__main__':
    unittest.main()
