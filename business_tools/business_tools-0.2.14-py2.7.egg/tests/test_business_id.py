# coding: utf-8
#
# Copyright (c) 2009, Norfello Oy
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the Norfello Oy nor the
#      names of its contributors may be used to endorse or promote products
#      derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY NORFELLO OY ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL NORFELLO OY BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Unit tests for business_id.py."""

import unittest

from business_tools.business_id import BusinessID


class TestBusinessID(unittest.TestCase):

    def test_init(self):
        """
        Test initialization.
        """
        values = ('1234567-1', '12345671', 'FI12345671', 'FI1234567-1')
        for v in values:
            b = BusinessID(v)
            self.assertEqual('12345671', str(b._value))

    def test_unexpanded_human_format(self):
        """
        Test __init__ with internal formatting.
        """
        b = BusinessID('244679-4')
        self.assertEqual('02446794', str(b._value))

    def test_unexpanded_international(self):
        """
        Test __init__ with internal formatting of international format.
        """
        b = BusinessID('FI2446794')
        self.assertEqual('02446794', str(b._value))

    def test_machine_format(self):
        """
        Test machine parseable output.
        """
        b = BusinessID('1234567-1')
        self.assertEqual(b.machine_format(), '12345671')

    def test_human_format(self):
        """
        Test human readable output.
        """
        b = BusinessID('1234567-1')
        self.assertEqual(b.human_format(), '1234567-1')

    def test_international_format(self):
        """
        Test international formatting of finnish business id.
        """
        b = BusinessID('1234567-1')
        self.assertEqual(b.international_format(), 'FI12345671')

    def test_equality(self):
        b1 = BusinessID('FI1234567-1')
        for b2 in ('1234567-1', 'FI12345671', BusinessID('1234567-1')):
            self.failUnless(b1 == b2)

    def test_non_equality(self):
        b1 = BusinessID('1109953-6')
        for b2 in ('1234567-1', None, BusinessID('1234567-1')):
            self.failUnless(b1 != b2)

    def test_split(self):
        b = BusinessID('1234567-1')
        self.assertEqual(b.split(b._value), ('1234567', '1'))

    def test_expand(self):
        """
        Test expanding.
        """
        values = {'1234567-1': '12345671'}
        for k, v in values.iteritems():
            b = BusinessID(k)
            self.assertEqual(b.expand(b._value), v)

    def test_str(self):
        """
        Test string conversion.
        """
        for v in ('1234567-1', '12345671'):
            b = BusinessID(v)
            self.assertEqual('1234567-1', str(b))

    def test_unicode(self):
        """
        Test unicode conversion.
        """
        for v in ('1234567-1', '12345671'):
            b = BusinessID(v)
            self.assertEqual(u'1234567-1', str(b))

    def test_conversions(self):
        # Test conversions
        for val in ('1234567-1', 12345671):
            b = BusinessID(val)
            msg = u'While trying to convert from %s' % type(val)
            self.assertEqual(str(b), '1234567-1', msg)
            self.assertEqual(b.machine_format(), '12345671', msg)
            self.assertEqual(b.human_format(), '1234567-1', msg)

    def test_validation(self):
        """
        Test validation.
        """
        values = ('1234567-8', '13213231231233', u'Moi äiti!',
                  u'Älöäläläöä')
        for val in values:
            self.assertEqual(BusinessID.is_valid(val), False)

    def test_import(self):
        from business_tools import BusinessID
        b = BusinessID('1234567-1')
