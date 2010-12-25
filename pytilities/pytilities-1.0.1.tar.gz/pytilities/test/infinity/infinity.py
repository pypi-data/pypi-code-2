# Copyright (C) 2010 Tim Diels <limyreth@users.sourceforge.net>
# 
# This file is part of pytilities.
# 
# pytilities is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# pytilities is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with pytilities.  If not, see <http://www.gnu.org/licenses/>.
#

__docformat__ = 'reStructuredText'

import unittest

from pytilities.infinity import (
    infinity as positive_infinity, negative_infinity, nan,
    is_positive_infinity, is_negative_infinity, is_infinity, is_nan)

class IntegerInfinityTestCase(unittest.TestCase):
    def test_funcs(self):
        '''test the is* functions'''
        finf = float('inf')
        fnan = float('nan')

        self.assert_(is_positive_infinity(positive_infinity))
        self.assert_(is_positive_infinity(finf))
        self.assertFalse(is_positive_infinity(negative_infinity))
        self.assertFalse(is_positive_infinity(-finf))
        self.assertFalse(is_positive_infinity(nan))
        self.assertFalse(is_positive_infinity(fnan))
        self.assertFalse(is_positive_infinity(1))

        self.assert_(is_negative_infinity(negative_infinity))
        self.assert_(is_negative_infinity(-finf))
        self.assertFalse(is_negative_infinity(positive_infinity))
        self.assertFalse(is_negative_infinity(finf))
        self.assertFalse(is_negative_infinity(nan))
        self.assertFalse(is_negative_infinity(fnan))
        self.assertFalse(is_negative_infinity(1))

        self.assert_(is_infinity(positive_infinity))
        self.assert_(is_infinity(finf))
        self.assert_(is_infinity(negative_infinity))
        self.assert_(is_infinity(-finf))
        self.assertFalse(is_infinity(1))

        self.assert_(is_nan(nan))
        self.assert_(is_nan(fnan))
        self.assertFalse(is_nan(1))

    def test_comparisons(self):
        '''
        test comparison between int, +inf, -inf, and nan
        '''
        # +inf v +inf
        self.assert_(positive_infinity == positive_infinity)
        self.assertFalse(positive_infinity != positive_infinity)
        self.assert_(positive_infinity >= positive_infinity)
        self.assert_(positive_infinity <= positive_infinity)
        self.assertFalse(positive_infinity > positive_infinity)
        self.assertFalse(positive_infinity < positive_infinity)

        # +inf v -inf
        self.assertFalse(positive_infinity == negative_infinity)
        self.assert_(positive_infinity != negative_infinity)
        self.assert_(positive_infinity >= negative_infinity)
        self.assertFalse(positive_infinity <= negative_infinity)
        self.assert_(positive_infinity > negative_infinity)
        self.assertFalse(positive_infinity < negative_infinity)

        # +inf v nan
        self.assertFalse(positive_infinity == nan)
        self.assert_(positive_infinity != nan)
        self.assertFalse(positive_infinity >= nan)
        self.assertFalse(positive_infinity <= nan)
        self.assertFalse(positive_infinity > nan)
        self.assertFalse(positive_infinity < nan)

        # +inf v int
        self.assertFalse(positive_infinity == 1)
        self.assert_(positive_infinity != 1)
        self.assert_(positive_infinity >= 1)
        self.assertFalse(positive_infinity <= 1)
        self.assert_(positive_infinity > 1)
        self.assertFalse(positive_infinity < 1)

        # -inf v -inf
        self.assert_(negative_infinity == negative_infinity)
        self.assertFalse(negative_infinity != negative_infinity)
        self.assert_(negative_infinity >= negative_infinity)
        self.assert_(negative_infinity <= negative_infinity)
        self.assertFalse(negative_infinity > negative_infinity)
        self.assertFalse(negative_infinity < negative_infinity)

        # -inf v +inf
        self.assertFalse(negative_infinity == positive_infinity)
        self.assert_(negative_infinity != positive_infinity)
        self.assertFalse(negative_infinity >= positive_infinity)
        self.assert_(negative_infinity <= positive_infinity)
        self.assertFalse(negative_infinity > positive_infinity)
        self.assert_(negative_infinity < positive_infinity)

        # -inf v nan
        self.assertFalse(negative_infinity == nan)
        self.assert_(negative_infinity != nan)
        self.assertFalse(negative_infinity >= nan)
        self.assertFalse(negative_infinity <= nan)
        self.assertFalse(negative_infinity > nan)
        self.assertFalse(negative_infinity < nan)

        # -inf v int
        self.assertFalse(negative_infinity == 1)
        self.assert_(negative_infinity != 1)
        self.assertFalse(negative_infinity >= 1)
        self.assert_(negative_infinity <= 1)
        self.assertFalse(negative_infinity > 1)
        self.assert_(negative_infinity < 1)

        # nan v nan
        self.assertFalse(nan == nan)
        self.assert_(nan != nan)
        self.assertFalse(nan >= nan)
        self.assertFalse(nan <= nan)
        self.assertFalse(nan > nan)
        self.assertFalse(nan < nan)

        # nan v -inf
        self.assertFalse(nan == negative_infinity)
        self.assert_(nan != negative_infinity)
        self.assertFalse(nan >= negative_infinity)
        self.assertFalse(nan <= negative_infinity)
        self.assertFalse(nan > negative_infinity)
        self.assertFalse(nan < negative_infinity)

        # nan v +inf
        self.assertFalse(nan == positive_infinity)
        self.assert_(nan != positive_infinity)
        self.assertFalse(nan >= positive_infinity)
        self.assertFalse(nan <= positive_infinity)
        self.assertFalse(nan > positive_infinity)
        self.assertFalse(nan < positive_infinity)

        # nan v int
        self.assertFalse(nan == -1)
        self.assert_(nan != -1)
        self.assertFalse(nan >= -1)
        self.assertFalse(nan <= -1)
        self.assertFalse(nan > -1)
        self.assertFalse(nan < -1)

        # int v +inf
        self.assertFalse(1 == positive_infinity)
        self.assert_(1 != positive_infinity)
        self.assertFalse(1 >= positive_infinity)
        self.assert_(1 <= positive_infinity)
        self.assertFalse(1 > positive_infinity)
        self.assert_(1 < positive_infinity)

        # int v -inf
        self.assertFalse(1 == negative_infinity)
        self.assert_(1 != negative_infinity)
        self.assert_(1 >= negative_infinity)
        self.assertFalse(1 <= negative_infinity)
        self.assert_(1 > negative_infinity)
        self.assertFalse(1 < negative_infinity)

        # int v nan
        self.assertFalse(1 == nan)
        self.assert_(1 != nan)
        self.assertFalse(1 >= nan)
        self.assertFalse(1 <= nan)
        self.assertFalse(1 > nan)
        self.assertFalse(1 < nan)

    # Note: at first I tried, but getting float op int_inf working does not
    # seem possible
    def test_comparisons_float(self):
        '''
        test comparison between (int, +iinf, -iinf, inan) and (float, +finf,
        -finf, fnan)
        '''
        finf = float('inf')
        fnan = float('nan')

        # +inf v float
        self.assertFalse(positive_infinity == 1.2)
        self.assert_(positive_infinity != 1.2)
        self.assert_(positive_infinity >= 1.2)
        self.assertFalse(positive_infinity <= 1.2)
        self.assert_(positive_infinity > 1.2)
        self.assertFalse(positive_infinity < 1.2)

        # +inf v +finf
        self.assert_(positive_infinity == finf)
        self.assertFalse(positive_infinity != finf)
        self.assert_(positive_infinity >= finf)
        self.assert_(positive_infinity <= finf)
        self.assertFalse(positive_infinity > finf)
        self.assertFalse(positive_infinity < finf)

        # +inf v -finf
        self.assertFalse(positive_infinity == -finf)
        self.assert_(positive_infinity != -finf)
        self.assert_(positive_infinity >= -finf)
        self.assertFalse(positive_infinity <= -finf)
        self.assert_(positive_infinity > -finf)
        self.assertFalse(positive_infinity < -finf)

        # +inf v fnan
        self.assertFalse(positive_infinity == fnan)
        self.assert_(positive_infinity != fnan)
        self.assertFalse(positive_infinity >= fnan)
        self.assertFalse(positive_infinity <= fnan)
        self.assertFalse(positive_infinity > fnan)
        self.assertFalse(positive_infinity < fnan)

        # -inf v float
        self.assertFalse(negative_infinity == 1.2)
        self.assert_(negative_infinity != 1.2)
        self.assertFalse(negative_infinity >= 1.2)
        self.assert_(negative_infinity <= 1.2)
        self.assertFalse(negative_infinity > 1.2)
        self.assert_(negative_infinity < 1.2)

        # -inf v +finf
        self.assertFalse(negative_infinity == finf)
        self.assert_(negative_infinity != finf)
        self.assertFalse(negative_infinity >= finf)
        self.assert_(negative_infinity <= finf)
        self.assertFalse(negative_infinity > finf)
        self.assert_(negative_infinity < finf)

        # -inf v -finf
        self.assert_(negative_infinity == -finf)
        self.assertFalse(negative_infinity != -finf)
        self.assert_(negative_infinity >= -finf)
        self.assert_(negative_infinity <= -finf)
        self.assertFalse(negative_infinity > -finf)
        self.assertFalse(negative_infinity < -finf)

        # -inf v fnan
        self.assertFalse(positive_infinity == fnan)
        self.assert_(positive_infinity != fnan)
        self.assertFalse(positive_infinity >= fnan)
        self.assertFalse(positive_infinity <= fnan)
        self.assertFalse(positive_infinity > fnan)
        self.assertFalse(positive_infinity < fnan)

        # inan v float
        self.assertFalse(nan == 1.2)
        self.assert_(nan != 1.2)
        self.assertFalse(nan >= 1.2)
        self.assertFalse(nan <= 1.2)
        self.assertFalse(nan > 1.2)
        self.assertFalse(nan < 1.2)

        # inan v +finf
        self.assertFalse(nan == finf)
        self.assert_(nan != finf)
        self.assertFalse(nan >= finf)
        self.assertFalse(nan <= finf)
        self.assertFalse(nan > finf)
        self.assertFalse(nan < finf)

        # inan v -finf
        self.assertFalse(nan == -finf)
        self.assert_(nan != -finf)
        self.assertFalse(nan >= -finf)
        self.assertFalse(nan <= -finf)
        self.assertFalse(nan > -finf)
        self.assertFalse(nan < -finf)

        # inan v fnan
        self.assertFalse(nan == fnan)
        self.assert_(nan != fnan)
        self.assertFalse(nan >= fnan)
        self.assertFalse(nan <= fnan)
        self.assertFalse(nan > fnan)
        self.assertFalse(nan < fnan)

        # float v +inf
        self.assertFalse(1.2 == positive_infinity)
        self.assert_(1.2 != positive_infinity)
        self.assertFalse(1.2 >= positive_infinity)
        self.assert_(1.2 <= positive_infinity)
        self.assertFalse(1.2 > positive_infinity)
        self.assert_(1.2 < positive_infinity)

        # float v -inf
        self.assertFalse(1.2 == negative_infinity)
        self.assert_(1.2 != negative_infinity)
        self.assert_(1.2 >= negative_infinity)
        self.assertFalse(1.2 <= negative_infinity)
        self.assert_(1.2 > negative_infinity)
        self.assertFalse(1.2 < negative_infinity)

        # float v nan
        self.assertFalse(1.2 == nan)
        self.assert_(1.2 != nan)
        self.assertFalse(1.2 >= nan)
        self.assertFalse(1.2 <= nan)
        self.assertFalse(1.2 > nan)
        self.assertFalse(1.2 < nan)

        # finf v +inf
        self.assert_(finf == positive_infinity)
        self.assertFalse(finf != positive_infinity)
        self.assert_(finf >= positive_infinity)
        self.assert_(finf <= positive_infinity)
        self.assertFalse(finf > positive_infinity)
        self.assertFalse(finf < positive_infinity)

        # finf v -inf
        self.assertFalse(finf == negative_infinity)
        self.assert_(finf != negative_infinity)
        self.assert_(finf >= negative_infinity)
        self.assertFalse(finf <= negative_infinity)
        self.assert_(finf > negative_infinity)
        self.assertFalse(finf < negative_infinity)

        # finf v nan
        self.assertFalse(finf == nan)
        self.assert_(finf != nan)
        self.assertFalse(finf >= nan)
        self.assertFalse(finf <= nan)
        self.assertFalse(finf > nan)
        self.assertFalse(finf < nan)

        # -finf v +inf
        self.assertFalse(-finf == positive_infinity)
        self.assert_(-finf != positive_infinity)
        self.assertFalse(-finf >= positive_infinity)
        self.assert_(-finf <= positive_infinity)
        self.assertFalse(-finf > positive_infinity)
        self.assert_(-finf < positive_infinity)

        # -finf v -inf
        self.assert_(-finf == negative_infinity)
        self.assertFalse(-finf != negative_infinity)
        self.assert_(-finf >= negative_infinity)
        self.assert_(-finf <= negative_infinity)
        self.assertFalse(-finf > negative_infinity)
        self.assertFalse(-finf < negative_infinity)

        # -finf v nan
        self.assertFalse(-finf == nan)
        self.assert_(-finf != nan)
        self.assertFalse(-finf >= nan)
        self.assertFalse(-finf <= nan)
        self.assertFalse(-finf > nan)
        self.assertFalse(-finf < nan)

        # fnan v +inf
        self.assertFalse(fnan == positive_infinity)
        self.assert_(fnan != positive_infinity)
        self.assertFalse(fnan >= positive_infinity)
        self.assertFalse(fnan <= positive_infinity)
        self.assertFalse(fnan > positive_infinity)
        self.assertFalse(fnan < positive_infinity)

        # fnan v -inf
        self.assertFalse(fnan == negative_infinity)
        self.assert_(fnan != negative_infinity)
        self.assertFalse(fnan >= negative_infinity)
        self.assertFalse(fnan <= negative_infinity)
        self.assertFalse(fnan > negative_infinity)
        self.assertFalse(fnan < negative_infinity)

        # fnan v nan
        self.assertFalse(fnan == nan)
        self.assert_(fnan != nan)
        self.assertFalse(fnan >= nan)
        self.assertFalse(fnan <= nan)
        self.assertFalse(fnan > nan)
        self.assertFalse(fnan < nan)

    def test_arithmetic(self):
        '''test anything but comparison on our infinity'''
        # multiplications
        self.assertIs(positive_infinity * 2, positive_infinity)
        self.assertIs(positive_infinity * -2, negative_infinity)
        self.assertIs(positive_infinity * 0, nan)

        self.assertIs(negative_infinity * 2, negative_infinity)
        self.assertIs(negative_infinity * -2, positive_infinity)
        self.assertIs(negative_infinity * 0, nan)

        self.assertIs(nan * 2, nan)
        self.assertIs(nan * -2, nan)
        self.assertIs(nan * 0, nan)

        a = positive_infinity
        a *= 2
        self.assertIs(a, positive_infinity)
        a = positive_infinity
        a *= -2
        self.assertIs(a, negative_infinity)
        a = positive_infinity
        a *= 0
        self.assertIs(a, nan)

        a = negative_infinity
        a *= 2
        self.assertIs(a, negative_infinity)
        a = negative_infinity
        a *= -2
        self.assertIs(a, positive_infinity)
        a = negative_infinity
        a *= 0
        self.assertIs(a, nan)

        a = nan
        a *= 2
        self.assertIs(a, nan)
        a = nan
        a *= -2
        self.assertIs(a, nan)
        a = nan
        a *= 0
        self.assertIs(a, nan)

        # division
        self.assertIs(positive_infinity / positive_infinity, nan)
        self.assertIs(positive_infinity / negative_infinity, nan)
        self.assertRaises(ZeroDivisionError, lambda: positive_infinity / 0)
        self.assertIs(positive_infinity / 2, positive_infinity)
        self.assertIs(positive_infinity / -2, negative_infinity)

        self.assertIs(negative_infinity / negative_infinity, nan)
        self.assertIs(negative_infinity / positive_infinity, nan)
        self.assertRaises(ZeroDivisionError, lambda: negative_infinity / 0)
        self.assertIs(negative_infinity / 2, negative_infinity)
        self.assertIs(negative_infinity / -2, positive_infinity)

        self.assertIs(nan / nan, nan)

        a = positive_infinity
        a /= a
        self.assertIs(a, nan)

        a = negative_infinity
        a /= a
        self.assertIs(a, nan)

        # addition
        self.assertIs(positive_infinity + positive_infinity, positive_infinity)
        self.assertIs(positive_infinity + negative_infinity, nan)
        self.assertIs(positive_infinity + nan, nan)
        self.assertIs(positive_infinity + 1, positive_infinity)
        self.assertIs(1 + positive_infinity, positive_infinity)

        self.assertIs(negative_infinity + negative_infinity, negative_infinity)
        self.assertIs(negative_infinity + positive_infinity, nan)
        self.assertIs(negative_infinity + nan, nan)
        self.assertIs(negative_infinity + 1, negative_infinity)
        self.assertIs(1 + negative_infinity, negative_infinity)

        self.assertIs(nan + nan, nan)
        self.assertIs(nan + 1, nan)
        self.assertIs(1 + nan, nan)

        a = positive_infinity
        a += nan
        self.assertIs(a, nan)

        a = negative_infinity
        a += positive_infinity
        self.assertIs(a, nan)

        a = nan
        a += 1
        self.assertIs(a, nan)

        # substraction
        self.assertIs(positive_infinity - 1, positive_infinity)
        self.assertIs(1 - positive_infinity, positive_infinity)

        self.assertIs(negative_infinity - 1, negative_infinity)
        self.assertIs(1 - negative_infinity, negative_infinity)

        a = positive_infinity
        a -= 1
        self.assertIs(a, positive_infinity)

        # test for some very odd thingies
        self.assertIsNot(positive_infinity, nan)
        self.assertIsNot(negative_infinity, nan)
        self.assertIsNot(positive_infinity, negative_infinity)

