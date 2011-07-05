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
from decimal import Decimal

from business_tools.money import Money


class TestMoney(unittest.TestCase):

    def test_repr(self):
        ref = Money(Decimal('123456.123456'))
        self.assertEqual(ref.__repr__(), '<Money: 123 456,12>')

    def test_str(self):
        ref = Money(Decimal('123456.123456'))
        self.assertEqual(str(ref), '123 456,12')

    def test_float(self):
        ref = Money(Decimal('123456.123456'))
        self.assertEqual(float(ref), float('123456.12'))

    def test_unicode(self):
        ref = Money(Decimal('123456.123456'))
        self.assertEqual(unicode(ref), u'123 456,12')

    def test_human_format(self):
        # Decimal argument
        alist = ((Decimal('123456.789012345'), '123 456,79'),
                ('123456,789012345', '123 456,79'),
                (u'123456,789012345', '123 456,79'),
                (float('123456.789012345'), '123 456,79'),
                (int(Decimal('123456.789012345')), '123 456'),
                (Decimal('-123456.789012345'), '-123 456,79'),
                ('-123456,789012345', '-123 456,79'),
                (u'-123456,789012345', '-123 456,79'),
                (float('-123456.789012345'), '-123 456,79'),
                (int(Decimal('-123456.789012345')), '-123 456'),
                )
        for item in alist:
            self.assert_human_format(item[0], item[1])

    def assert_human_format(self, value, assert_value):
        ref = Money(value)
        self.assertEqual(assert_value, ref.human_format())

    def test_quantize(self):
        test_value = Decimal("987654321.987654321")
        ref = Money(test_value, quantize=None)
        self.assertEqual(test_value, ref.machine_format())
        self.assertEqual("987 654 321,987654321", ref.human_format())
        self.assertRaises(ValueError, Money, test_value, quantize=-2)

    def test_dp(self):
        test_value = Decimal("987654321.987654321")
        ref = Money(test_value, dp=" XXX ")
        self.assertEqual("987 654 321 XXX 99", ref.human_format())

    def test_sep(self):
        test_value = Decimal("987654321.987654321")
        ref = Money(test_value, sep=" thousand ")
        self.assertEqual('987 thousand 654 thousand 321,99',
                         ref.human_format())

    def test_curr(self):
        test_value = Decimal("987654321.987654321")
        ref = Money(test_value, curr=u"€")
        self.assertEqual(u'987 654 321,99€',
                         ref.human_format())

    def test_pos_and_neg(self):
        test_value = Decimal("987654321.987654321")
        ref = Money(test_value, pos="POSITIVE: ")
        self.assertEqual(u'POSITIVE: 987 654 321,99',
                         ref.human_format())
        ref = Money(-test_value, neg="NEGATIVE: ")
        self.assertEqual(u'NEGATIVE: 987 654 321,99',
                         ref.human_format())

    def test_trailneg(self):
        test_value = Decimal("-987654321.987654321")
        ref = Money(test_value, trailneg="<<<<<")
        self.assertEqual(u'-987 654 321,99<<<<<',
                         ref.human_format())
