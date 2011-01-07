# -*- coding: UTF-8 -*-
# vim: fileencoding=UTF-8 filetype=python ff=unix et ts=4 sw=4 sts=4 tw=120
#
# Copyright (c) 2010, Christer Sjöholm -- hcs AT furuvik DOT net
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import os

from hcs_utils.path import list_dir, scan_for_new_files, tempdir, walkfiles
from hcs_utils.unittest import eq_

def test_list_dir():
    with tempdir() as tmpd:
        eq_(list_dir(tmpd), ([], []))
        open(os.path.join(tmpd, 'f1'), 'w').close()
        open(os.path.join(tmpd, 'f2'), 'w').close()
        os.mkdir(os.path.join(tmpd, 'd1'))
        eq_(list_dir(tmpd), (['d1'], ['f1', 'f2']))

def test_scan_for_new_files():
    with tempdir() as tmpd:
        os.mkdir(os.path.join(tmpd, 'd1'))
        open(os.path.join(tmpd, 'f1'), 'w').close()
        open(os.path.join(tmpd, 'f2'), 'w').close()
        scanner = scan_for_new_files(tmpd, interval=0.1)
        eq_(next(scanner), os.path.join(tmpd, 'f1'))
        eq_(next(scanner), os.path.join(tmpd, 'f2'))
        scanner.close()

def test_scan_for_new_files_include():
    with tempdir() as tmpd:
        open(os.path.join(tmpd, 'f1'), 'w').close()
        open(os.path.join(tmpd, 'f2'), 'w').close()
        open(os.path.join(tmpd, 'f2.test'), 'w').close()
        scanner = scan_for_new_files(tmpd, interval=0.1, include='.*\.test$')
        eq_(next(scanner), os.path.join(tmpd, 'f2.test'))
        open(os.path.join(tmpd, 'f3.test'), 'w').close()
        eq_(next(scanner), os.path.join(tmpd, 'f3.test'))
        scanner.close()

def test_scan_for_new_files_exclude():
    with tempdir() as tmpd:
        open(os.path.join(tmpd, 'f1'), 'w').close()
        open(os.path.join(tmpd, 'f2'), 'w').close()
        open(os.path.join(tmpd, 'f2.test'), 'w').close()
        scanner = scan_for_new_files(tmpd, interval=0.1, ignore='.*\.test$')
        eq_(next(scanner), os.path.join(tmpd, 'f1'))
        eq_(next(scanner), os.path.join(tmpd, 'f2'))
        open(os.path.join(tmpd, 'f3.test'), 'w').close()
        open(os.path.join(tmpd, 'f3'), 'w').close()
        eq_(next(scanner), os.path.join(tmpd, 'f3'))
        scanner.close()

def test_walkfiles():
    with tempdir() as tmpd:
        open(os.path.join(tmpd, 'f1'), 'w').close()
        open(os.path.join(tmpd, 'f2'), 'w').close()
        open(os.path.join(tmpd, 'f2.test'), 'w').close()
        os.makedirs(os.path.join(tmpd, 'd1', 'dd1'))
        os.makedirs(os.path.join(tmpd, 'd2', 'dd2'))
        open(os.path.join(tmpd, 'd2', 'dd2', 'ddf23'), 'w').close()
        open(os.path.join(tmpd, 'd2', 'dd2', 'ddf2'), 'w').close()
        os.makedirs(os.path.join(tmpd, 'd3', 'dd3'))
        open(os.path.join(tmpd, 'd3', 'dd3', 'ddf3'), 'w').close()

        expected_result = ['f1', 'f2', 'f2.test', 'd2/dd2/ddf2', 'd2/dd2/ddf23', 'd3/dd3/ddf3']
        eq_(list(walkfiles(tmpd)), [os.path.join(tmpd, fn) for fn in expected_result])

        expected_result = ['f2.test']
        eq_(list(walkfiles(tmpd, pattern='*.test')), [os.path.join(tmpd, fn) for fn in expected_result])
