##
## test_util.py
## Login : <uli@pu.smp.net>
## Started on  Mon Nov 29 14:04:37 2010 Uli Fouquet
## $Id$
## 
## Copyright (C) 2010 Uli Fouquet
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
"""
Tests for helpers.
"""
import doctest
import unittest
import odls.client.util
from odls.client.util import split_path

class UtilTestCase(unittest.TestCase):

    def test_split_path(self):
        result0 = split_path('sample')
        self.assertTrue(result0[1].endswith('/sample'))

def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(
        UtilTestCase)
    suite.addTests(
        doctest.DocTestSuite(odls.client.util,
                             optionflags=doctest.ELLIPSIS,
                             ),
        )
    return suite

test_suite = suite

if __name__ == '__main__':
    unittest.main(defaultTests='test_suite')
