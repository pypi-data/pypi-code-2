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

import unittest

from business_tools.reference_number import ReferenceNumber


class TestReferenceNumber(unittest.TestCase):

    def test_repr(self):
        ref = ReferenceNumber('12344')
        self.assertEqual(ref.__repr__(), '<Reference number: 12344>')

    def test_str(self):
        ref = ReferenceNumber('12344')
        self.assertEqual(str(ref), '12344')

    def test_unicode(self):
        ref = ReferenceNumber('12344')
        self.assertEqual(unicode(ref), u'12344')

    def test_human_format(self):
        values = ('123 45672', '12345672', '1 2345672')
        for val in values:
            ref = ReferenceNumber(val)
            self.assertEqual('123 45672', ref.human_format())

    def test_machine_format(self):
        values = ('123 45672', '12345672')
        for val in values:
            ref = ReferenceNumber(val)
            self.assertEqual('00000000000012345672', ref.machine_format())

    def test_validate(self):
        self.assertEqual(ReferenceNumber.validate('12344'), True)
        self.assertEqual(ReferenceNumber.validate('12341'), False)

    def test_calculate_checksum(self):
        chksum = ReferenceNumber.calculate_checksum('1234')
        self.assertEqual(chksum, '4')

        chksum = ReferenceNumber.calculate_checksum('1 23456 78912 34567')
        self.assertEqual(chksum, '9')

        self.assertRaises(ValueError, ReferenceNumber.calculate_checksum,
                          None)

        self.assertRaises(ValueError, ReferenceNumber.calculate_checksum,
                          '')

        self.assertRaises(ValueError, ReferenceNumber.calculate_checksum,
                          'HelloWorld')
