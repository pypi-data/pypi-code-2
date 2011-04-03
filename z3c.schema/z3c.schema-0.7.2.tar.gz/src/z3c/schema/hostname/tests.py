##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
from zope.schema.interfaces import RequiredMissing
from zope.schema.tests.test_field import FieldTestBase
import doctest
import unittest

from z3c.schema.hostname import HostName
from z3c.schema.hostname import InvalidHostName


class HostNameTest(FieldTestBase):

    _Field_Factory = HostName
    _convert = str

    def testValidate(self):
        field = self._Field_Factory(title=u'HostName field', description=u'',
            readonly=False, required=False)
        field.validate(None)
        field.validate(self._convert('host'))
        field.validate(self._convert('123.123.123.123'))
        field.validate(self._convert('host:123'))
        field.validate(self._convert('www.host.com:123'))
        field.validate(self._convert('123.123.123.123:123'))

    def testValidateRequired(self):
        field = self._Field_Factory(title=u'HostName field', description=u'',
            readonly=False, required=True)
        field.validate(self._convert('host'))
        self.assertRaises(RequiredMissing, field.validate, None)

    def testBadStringType(self):
        field = self._Field_Factory(title=u'HostName field')
        self.assertRaises(InvalidHostName, field.validate, u'123.123')

    def test_newlines(self):
        field = self._Field_Factory(title=u'HostName field')
        self.assertRaises(InvalidHostName, field.validate,
            self._convert('host\nfoo'))


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,),
        unittest.makeSuite(HostNameTest),
        ))
