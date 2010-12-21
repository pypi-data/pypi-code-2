##
## test_odlsclient.py
## Login : <uli@pu.smp.net>
## Started on  Thu Dec  3 09:57:58 2009 Uli Fouquet
## $Id$
## 
## Copyright (C) 2009 Uli Fouquet
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
## 
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##
import doctest
import os
import re
import unittest
import zc.buildout.testing
from zope.testing import renormalizing

checker = renormalizing.RENormalizing([
    zc.buildout.testing.normalize_path,
    (re.compile(
        "Couldn't find index page for '[a-zA-Z0-9.]+' "
        "\(maybe misspelled\?\)"
        "\n"),
     ''),
    (re.compile("""['"][^\n"']+z3c.recipe.i18n[^\n"']*['"],"""),
     "'/z3c.recipe.i18n',"),
    (re.compile('#![^\n]+\n'), ''),
    (re.compile('-\S+-py\d[.]\d(-\S+)?.egg'),
     '-pyN.N.egg',
    ),
    ])


globs = dict()

def setUp(test):
    pass

def tearDown(test):
    pass

def test_suite():
    testfiles = [
        'README.txt',
        'tests/test_configuration.txt',
        ]
    suite = unittest.TestSuite()
    for testfile in testfiles:
        suite.addTest(
            doctest.DocFileSuite(
                testfile,
                setUp = setUp,
                tearDown = tearDown,
                optionflags = doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE,
                checker = checker,
                globs = globs,
                ))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTests='test_suite')
