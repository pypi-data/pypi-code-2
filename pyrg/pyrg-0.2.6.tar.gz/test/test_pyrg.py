import unittest
import ConfigParser
import sys
import os
from tempfile import NamedTemporaryFile
sys.path.insert(0, os.path.abspath("pyrg"))
import pyrg


class ColorFunctionTest(unittest.TestCase):

    def test_coloring_method(self):
        line = "get_gg (__main__.TestTest)"
        self.assertEqual("[36mget_gg (__main__.TestTest)[0m",
                         pyrg.coloring_method(line))

    def test_okroute(self):
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

    def test_okroute_verbose(self):
        input_strings = """test_dummy1 (__main__.TestDummy) ... ok

----------------------------------------------------------------------
Ran 1 tests in 0.000s

OK
"""
        result_strings = """test_dummy1 (__main__.TestDummy) ... [32mok[0m

----------------------------------------------------------------------
Ran 1 tests in 0.000s

[32mOK[0m"""
        ret = pyrg.parse_unittest_result_verbose(input_strings.splitlines(1))
        self.assertEqual(ret, result_strings)

    def test_failroute(self):
        input_strings = """.F
======================================================================
FAIL: test_dummy_fail (__main__.TestDummy)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "test/test_pyrg_ng.py", line 140, in test_dummy_fail
    self.assertEqual(1, 2)
AssertionError: 1 != 2

----------------------------------------------------------------------
Ran 2 tests in 0.000s

FAILED (failures=1)
"""
        result_strings = """[32m.[0m[31mF[0m
======================================================================
[31mFAIL[0m: [36mtest_dummy_fail (__main__.TestDummy)[0m
----------------------------------------------------------------------
Traceback (most recent call last):
  File "test/test_pyrg_ng.py", line 140, in test_dummy_fail
    self.assertEqual(1, 2)
AssertionError: 1 != 2

----------------------------------------------------------------------
Ran 2 tests in 0.000s

[31mFAILED[0m ([31mfailures[0m=[31m1[0m)"""
        ret = pyrg.parse_unittest_result(input_strings.splitlines(1))
        self.assertEqual(ret, result_strings)

    def test_errorroute(self):
        input_strings = """.E
======================================================================
ERROR: test_dummy_error (__main__.TestDummy)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "test/test_pyrg_ng.py", line 143, in test_dummy_error
    self.assertEqual(1, a)
NameError: global name 'a' is not defined

----------------------------------------------------------------------
Ran 2 tests in 0.000s

FAILED (errors=1)
"""
        result_strings = """[32m.[0m[1;33mE[0m
======================================================================
[1;33mERROR[0m: [36mtest_dummy_error (__main__.TestDummy)[0m
----------------------------------------------------------------------
Traceback (most recent call last):
  File "test/test_pyrg_ng.py", line 143, in test_dummy_error
    self.assertEqual(1, a)
NameError: global name 'a' is not defined

----------------------------------------------------------------------
Ran 2 tests in 0.000s

[31mFAILED[0m ([1;33merrors[0m=[1;33m1[0m)"""
        ret = pyrg.parse_unittest_result(input_strings.splitlines(1))
        self.assertEqual(ret, result_strings)

    def test_errorfailroute(self):
        input_strings = """.EF
======================================================================
ERROR: test_dummy_error (__main__.TestDummy)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "test/test_pyrg_ng.py", line 143, in test_dummy_error
    self.assertEqual(1, a)
NameError: global name 'a' is not defined

======================================================================
FAIL: test_dummy_fail (__main__.TestDummy)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "test/test_pyrg_ng.py", line 140, in test_dummy_fail
    self.assertEqual(1, 2)
AssertionError: 1 != 2

----------------------------------------------------------------------
Ran 3 tests in 0.000s

FAILED (failures=1, errors=1)
"""
        result_strings = """[32m.[0m[1;33mE[0m[31mF[0m
======================================================================
[1;33mERROR[0m: [36mtest_dummy_error (__main__.TestDummy)[0m
----------------------------------------------------------------------
Traceback (most recent call last):
  File "test/test_pyrg_ng.py", line 143, in test_dummy_error
    self.assertEqual(1, a)
NameError: global name 'a' is not defined

======================================================================
[31mFAIL[0m: [36mtest_dummy_fail (__main__.TestDummy)[0m
----------------------------------------------------------------------
Traceback (most recent call last):
  File "test/test_pyrg_ng.py", line 140, in test_dummy_fail
    self.assertEqual(1, 2)
AssertionError: 1 != 2

----------------------------------------------------------------------
Ran 3 tests in 0.000s

[31mFAILED[0m ([31mfailures[0m=[31m1[0m, """\
"""[1;33merrors[0m=[1;33m1[0m)"""
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
        None

    def test_colormap_key_nonkey(self):
        colorname = self.id().split('_')[-1]
        self.assertEqual(False, colorname in pyrg.COLOR_MAP)

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


class TestConfig(unittest.TestCase):

    def test_notexist_file(self):
        color_set = pyrg.set_configuration("/home/hogehoge/.pyrgrc")
        self.assertEqual(pyrg.PRINT_COLOR_SET_DEFAULT, color_set)

    def test_check_id(self):
        default_color_id = id(pyrg.PRINT_COLOR_SET_DEFAULT)
        setting_color_id = id(pyrg.PRINT_COLOR_SET)
        get_color_id = id(pyrg.set_configuration(""))
        self.assertNotEqual(default_color_id, setting_color_id)
        self.assertNotEqual(default_color_id, get_color_id)
        self.assertNotEqual(setting_color_id, get_color_id)

    def test_config(self):
        config_example = """
[color]
ok = yellowgreen
error = red
fail = blue
function = pink
"""
        temp = NamedTemporaryFile()
        temp.file.write(config_example)
        temp.file.flush()
        color_set = pyrg.set_configuration(temp.name)
        self.assertEqual('yellowgreen', color_set['ok'])
        self.assertEqual('red', color_set['error'])
        self.assertEqual('blue', color_set['fail'])
        self.assertEqual('pink', color_set['function'])
        temp.close()

    def test_config_inval_colorkey(self):
        config_example = """
[color]
ok = white
fail = red
error = jihogeredd
function = pink
"""
        temp = NamedTemporaryFile()
        temp.file.write(config_example)
        temp.file.flush()
        color_set = pyrg.set_configuration(temp.name)
        self.assertEqual('white', color_set['ok'])
        self.assertEqual('yellow', color_set['error'])
        self.assertEqual('red', color_set['fail'])
        self.assertEqual('pink', color_set['function'])
        temp.close()

    def test_config_empty(self):
        config_example = """
[color]
ok =
error =
fail =
function =
"""
        temp = NamedTemporaryFile()
        temp.file.write(config_example)
        temp.file.flush()
        color_set = pyrg.set_configuration(temp.name)
        self.assertEqual(pyrg.PRINT_COLOR_SET_DEFAULT, color_set)
        temp.close()

    def test_config_colorkey_notexist_all(self):
        config_example = """
[color]
ok =
error =
hoge =
fail =
function =
"""
        temp = NamedTemporaryFile()
        temp.file.write(config_example)
        temp.file.flush()
        color_set = pyrg.set_configuration(temp.name)
        self.assertEqual(pyrg.PRINT_COLOR_SET_DEFAULT, color_set)
        temp.close()

    def test_config_keyword_notexist_2(self):
        config_example = """
[color]
ok =
fail =
function =
"""
        temp = NamedTemporaryFile()
        temp.file.write(config_example)
        temp.file.flush()
        color_set = pyrg.set_configuration(temp.name)
        self.assertEqual(pyrg.PRINT_COLOR_SET_DEFAULT, color_set)
        temp.close()

    def test_config_keyword_notexist_4(self):
        config_example = """
[color]
function =
"""
        temp = NamedTemporaryFile()
        temp.file.write(config_example)
        temp.file.flush()
        color_set = pyrg.set_configuration(temp.name)
        self.assertEqual(pyrg.PRINT_COLOR_SET_DEFAULT, color_set)
        temp.close()

    def test_config_keyword_notexist_all(self):
        config_example = """
[color]
"""
        temp = NamedTemporaryFile()
        temp.file.write(config_example)
        temp.file.flush()
        color_set = pyrg.set_configuration(temp.name)
        self.assertEqual(pyrg.PRINT_COLOR_SET_DEFAULT, color_set)
        temp.close()

    def test_config_empty(self):
        config_example = ""
        temp = NamedTemporaryFile()
        temp.file.write(config_example)
        temp.file.flush()
        self.assertRaises(ConfigParser.NoSectionError,
                          pyrg.set_configuration, temp.name)
        temp.close()


if __name__ == '__main__':
    unittest.main()
