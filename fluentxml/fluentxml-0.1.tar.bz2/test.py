#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  Copyright (c) 2007, 2008, 2009, 2010, 2011 Anaël Verrier
#  Copyright (c) 2007, 2008 Vincent Rasneur
#
#  Code based on test.py from PycaWM 0.2
#  Copyright (c) 2007, 2008 Vincent Rasneur, Anaël Verrier
#  Distributed under the terms of the GNU General Public License,
#  version 3 only. See http://pycawm.last-exile.org/
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, version 3 only.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals, print_function

import sys

from os import listdir
from os.path import join as path_join
from doctest import testfile, ELLIPSIS


class File(object):
    def __init__(self, content=''):
        self.content = content

    def __call__(self, *_args, **_kwds):
        return self

    def read(self):
        return self.content

    def close(self):
        pass

    def write(self, content):
        self.content += content


def get_test_files():
    test_dir = 'tests'
    if sys.version_info < (3,):
        test_dir += '2'
    test_ext = '.test'
    for test_file in listdir(test_dir):
        if test_file.endswith(test_ext):
            yield path_join(test_dir, test_file)


def run_tests():
    failed = 0
    total = 0
    for test_file in get_test_files():
        print('** Running the tests in %s' % test_file)
        f, t = testfile(test_file, module_relative=False, verbose=False,
                        encoding='utf-8', optionflags=ELLIPSIS,
                        globs={'File': File})
        failed += f
        total += t
    return failed, total


if __name__ == '__main__':
    failed, total = run_tests()
    print('*** All tests are finished now!')
    print('%d tests have been running.' % total)
    if failed:
        print('%d tests have failed! Go fix the bugs!' % failed)
    else:
        print('They all have succeeded, commit immediately!')
