#!/usr/bin/env python
"""test_pyprof2html - testing script for pyprof2html
"""
import os
import shutil
import sys
from subprocess import Popen, PIPE, call
import tempfile
import unittest
sys.path.insert(0, './pyprof2html')     # test to development path
import pyprof2html as p2h
from pyprof2html.core import check_cprofile, check_hotshot, convert_unit, \
                             create_stylefile, detect_filecodec, mapping_table


class FileTypeCheckTestCase(unittest.TestCase):

    def test_hotshot(self):
        self.assertEqual(True,
                check_hotshot("jifejihotshot-versionfijeifje)"))

    def test_nothotshot(self):
        self.assertEqual(False, check_hotshot("jotionfijeifje"))

    def test_cprofile(self):
        self.assertEqual(True, check_cprofile("jfiesprof.Profilerjife"))


class ConvertUnitTestCase(unittest.TestCase):

    def test_millisec1(self):
        ret = convert_unit(0.01)
        self.assertEqual(ret, "10.0 [ms]")

    def test_millisec100(self):
        ret = convert_unit(0.005)
        self.assertEqual(ret, "5.0 [ms]")

    def test_microsec1(self):
        ret = convert_unit(0.0009)
        self.assertEqual(ret, "900.0 [us]")

    def test_microsec100(self):
        ret = convert_unit(0.000009)
        self.assertEqual(ret, "9.0 [us]")

    def test_notconvert(self):
        ret = convert_unit(1.008009)
        self.assertEqual(ret, "1.008 [ s]")

    def test_nanosec1(self):
        ret = convert_unit(0.000000008)
        self.assertEqual(ret, "8.0 [ns]")


hotshotline_testdata_path = './test/hotshot.prof'
hotshot_testdata_path = './test/hot.prof'
cprof_testdata_path = './test/cprof.prof'
prof_testdata_path = './test/less.profile'
less_cprof_testdata_path = './test/less.cprof'
twenty_hotprof_testdata_path = './test/20funcs.hotprof'
less_hotprof_testdata_path = './test/less.hotprof'


class ExecuteHtmlTestCase(unittest.TestCase):

    def setUp(self):
        self.dirname = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.dirname)

    def test_cprofhtml(self):
        prof = p2h.Converter(cprof_testdata_path)
        prof.printout('html', self.dirname)
        self.assertEqual(True, os.path.exists(self.dirname + '/index.html'))

    def test_profilehtml(self):
        prof = p2h.Converter(prof_testdata_path)
        prof.output_dir = self.dirname
        prof.printout('html', self.dirname)
        self.assertEqual(True, os.path.exists(self.dirname + '/index.html'))

    def test_hotshothtml(self):
        prof = p2h.Converter(hotshot_testdata_path)
        prof.printout('html', self.dirname)
        self.assertEqual(True, os.path.exists(self.dirname + '/index.html'))

    def test_hotshotlinehtml(self):
        prof = p2h.Converter(hotshotline_testdata_path)
        prof.output_dir = self.dirname
        prof.printout('html')
        self.assertEqual(True, True)

    def test_cprof_function_is_twenty_or_less(self):
        prof = p2h.Converter(less_cprof_testdata_path)
        prof.printout('html', self.dirname)
        path = self.dirname + '/index.html'
        self.assertEqual(True, os.path.exists(path))
        path = self.dirname + '/index-all.html'
        self.assertEqual(False, os.path.exists(path))

    def test_hotshot_function_is_twenty(self):
        prof = p2h.Converter(twenty_hotprof_testdata_path)
        prof.printout('html', self.dirname)
        path = self.dirname + '/index.html'
        self.assertEqual(True, os.path.exists(path))
        path = self.dirname + '/index-all.html'
        self.assertEqual(False, os.path.exists(path))

    def test_hotshot_function_is_less_or_twenty(self):
        prof = p2h.Converter(less_hotprof_testdata_path)
        prof.printout('html', self.dirname)
        path = self.dirname + '/index.html'
        self.assertEqual(True, os.path.exists(path))
        path = self.dirname + '/index-all.html'
        self.assertEqual(False, os.path.exists(path))


class ExecuteRawTestCase(unittest.TestCase):

    def setUp(self):
        self.defaultstdout = sys.stdout
        sys.stdout = open('/dev/null', 'w')

    def tearDown(self):
        sys.stdout = self.defaultstdout

    def test_cprofraw(self):
        prof = p2h.Converter(cprof_testdata_path)
        prof.printout('raw')
        self.assertEqual(True, True)

    def test_hotshotraw(self):
        prof = p2h.Converter(hotshot_testdata_path)
        prof.printout('raw')
        self.assertEqual(True, True)


class ColorMappingTestCase(unittest.TestCase):

    def test_mapping_v1(self):
        ret = mapping_table(1, 1000)
        self.assertEqual(ret, '#ffffff')

    def test_mapping_v2(self):
        ret = mapping_table(29, 1000)
        self.assertEqual(ret, '#66ff99')

    def test_mapping_v3(self):
        ret = mapping_table(79, 1000)
        self.assertEqual(ret, '#ffcc33')

    def test_mapping_v4(self):
        ret = mapping_table(119, 1000)
        self.assertEqual(ret, '#ff6666')

    def test_mapping_v5(self):
        ret = mapping_table(199, 1000)
        self.assertEqual(ret, '#ff3333')

    def test_mapping_min(self):
        ret = mapping_table(0, 100)
        self.assertEqual(ret, '#ffffff')

    def test_mapping_max(self):
        ret = mapping_table(100, 100)
        self.assertEqual(ret, '#ff3333')

    def test_mapping_v1_float(self):
        ret = mapping_table(1., 1000.)
        self.assertEqual(ret, '#ffffff')

    def test_mapping_v2_float(self):
        ret = mapping_table(10., 1000.)
        self.assertEqual(ret, '#66ff99')

    def test_mapping_v3_float(self):
        ret = mapping_table(79., 1000.)
        self.assertEqual(ret, '#ffcc33')

    def test_mapping_v4_float(self):
        ret = mapping_table(119., 1000.)
        self.assertEqual(ret, '#ff6666')

    def test_mapping_v5_float(self):
        ret = mapping_table(199., 1000.)
        self.assertEqual(ret, '#ff3333')

    def test_mapping_min_float(self):
        ret = mapping_table(0.0, 1000.0)
        self.assertEqual(ret, '#ffffff')

    def test_mapping_max_float(self):
        ret = mapping_table(100., 100.)
        self.assertEqual(ret, '#ff3333')


class FindFileCodecTestCase(unittest.TestCase):

    def test_emacs_style1_eucjp(self):
        ret = detect_filecodec(["# -*- coding=euc-jp -*-"])
        self.assertEqual(ret, 'euc-jp')

    def test_emacs_style1(self):
        ret = detect_filecodec(["# -*- coding=utf-8 -*-"])
        self.assertEqual(ret, 'utf-8')

    def test_vim_style1(self):
        ret = detect_filecodec(["# vim: fileencoding=utf-8"])
        self.assertEqual(ret, 'utf-8')

    def test_vim_style1_shiftjis(self):
        ret = detect_filecodec(["# vim: fileencoding=shift_jis"])
        self.assertEqual(ret, 'shift_jis')


class CreateStylefileTestCase(unittest.TestCase):

    def setUp(self):
        self.dirname = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.dirname)

    def test_create_ok(self):
        create_stylefile(self.dirname)
        path = self.dirname + '/style.css'
        self.assertEqual(True, os.path.exists(path))
        path = self.dirname + '/jquery.js'
        self.assertEqual(True, os.path.exists(path))
        path = self.dirname + '/jquery.tablesorter.min.js'
        self.assertEqual(True, os.path.exists(path))
        path = self.dirname + '/arrow.png'
        self.assertEqual(True, os.path.exists(path))


class CommandExeTestCase(unittest.TestCase):

    def test_pyprof2html_nonarg(self):
        self.assertEqual(1, call('pyprof2html', shell=True,
                                  stdout=PIPE, stderr=PIPE))

    def test_pyprof2html_invalidarg(self):
        self.assertNotEqual(0, call('pyprof2html -p', shell=True,
                                  stdout=PIPE, stderr=PIPE))

    def test_pyprof2html_proffilearg(self):
        self.assertEqual(0, call('pyprof2html ' + cprof_testdata_path,
                                  shell=True))
        shutil.rmtree('./html')

    def test_pyprof2html_outputdir(self):
        call('pyprof2html -o dummy %s' % less_cprof_testdata_path,
             shell=True, stdout=PIPE, stderr=PIPE)
        self.assertEqual(os.path.exists('./dummy'), True)
        shutil.rmtree('./dummy')


unittest.main()
