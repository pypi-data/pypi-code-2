# Copyright (c) 2003-2010 gocept gmbh & co. kg, http://www.gocept.com
# Christian Zagrodnick, cz@gocept.com
# See also LICENSE.txt
# $Id: test_helpers.py 31512 2010-12-14 10:13:34Z mac $

from StringIO import StringIO
from tcm2sql.helpers import parseString
import unittest


class TestHelpers(unittest.TestCase):

    def test_string_parser(self):
        self.assertEquals(parseString('"foobar"'), 'foobar')
        self.assertEquals(parseString('foobar'), 'foobar')
        self.assertEquals(parseString('"1"'), '1')
        self.assertEquals(parseString('1'), '1')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestHelpers))
    return suite
