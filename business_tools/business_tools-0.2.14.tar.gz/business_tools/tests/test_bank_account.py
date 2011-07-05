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

"""Unit tests for bank_account.py"""

import unittest

from business_tools.bank_account import (BBAN, IBAN, bban_to_iban, iban_to_bban,
                                         get_swift_code)


class TestBBAN(unittest.TestCase):

    def test_machine_format(self):
        """
        Test that machine_format returns machine parseable output.
        """
        v = BBAN('123456-1234565')
        self.assertEqual(v.machine_format(), '12345601234565')

    def test_human_format(self):
        """
        Test that human_format returns human readable output.
        """
        v = BBAN('123456-1234565')
        self.assertEqual(v.human_format(), '123456-1234565')

    def test_bank_name(self):
        """
        Test that bank_name can parse bank name from the account number.
        """
        v = BBAN('123456-1234565')
        self.assertEqual(v.bank_name(), 'Nordea')

    def test_str(self):
        """
        Test string conversion.
        """
        self.assertEqual(str(BBAN('123456-1234565')), '123456-1234565')

    def test_is_valid(self):
        """
        Test validation.
        """
        self.failUnless(BBAN.is_valid('123456-1234565'))
        self.failIf(BBAN.is_valid('123456-1234567'))


class TestIBAN(unittest.TestCase):

    def test_validate(self):
        """
        Test validation.
        """
        v = IBAN('FI8912345601234565')

    def test_str(self):
        """
        Test string conversion.
        """
        self.assertEqual(str(IBAN('FI8912345601234565')), 'FI8912345601234565')

    def test_bank_name(self):
        """
        Test that bank_name can parse bank name from the IBAN account number.
        """
        v = IBAN('FI8912345601234565')
        self.assertEqual(v.bank_name(), 'Nordea')

        v = IBAN('FI1840551010234569')
        self.assertEqual(v.bank_name(), 'Aktia')

class TestHelpers(unittest.TestCase):

    def test_bban_to_iban(self):
        """
        Test bban->iban conversion.
        """
        for v in (('123456-1234565', 'FI8912345601234565'),
                  ('159030-776', 'FI3715903000000776'), ):
            bban = BBAN(v[0])
            iban = bban_to_iban(bban)
            self.assertEqual(iban, v[1])

    def test_iban_to_bban(self):
        """
        Test bban->iban conversion.
        """
        for v in (('123456-1234565', 'FI8912345601234565'),
                  ('159030-776', 'FI3715903000000776'), ):
            iban = IBAN(v[1])
            bban = iban_to_bban(iban)
            self.assertEqual(bban, v[0])

    def test_get_swift_code(self):
        """
        Test that swift code is found with a bank name.
        """
        values = [('Nordea', 'NDEAFIHH'),
                  (u'nordea', 'NDEAFIHH'),
                  (u'nandelsbanken', 'HANDFIHH'),
                  (u'seb', 'ESSEFIHX'),
                  (u'danske bank', 'DABAFIHX'),
                  (u'tapiola', 'TAPIFI22'),
                  (u'dnb nor', 'DNBAFIHX'),
                  (u'swedbank', 'SWEDFIHH'),
                  (u's-pankki', 'SBANFIHH'),
                  (u'säästöpankki', 'HELSFIHH'),
                  (u'pop', 'HELSFIHH'),
                  (u'osuuspankki', 'OKOYFIHH'),
                  (u'ålandsbanken', 'AABAFI22'),
                  (u'sampo', 'DABAFIHH'),
                  (u'aktia', 'HELSFIHH'), ]
        for v in values:
            swift = get_swift_code(v[0])
            self.assertEqual(swift, v[1])
