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

"""Monetary features."""

from decimal import Decimal


class Money(object):
    """ Convert decimal, str, int or float to a money formatted string.
        Money value is internally stored in Decimal format.

        Optional arguments:
        curr:    optional currency symbol (may be blank)
        sep:     optional grouping separator (comma, period, space, or blank)
        dp:      decimal point indicator (comma or period)
        pos:     optional sign for positive numbers: '+', space or blank
        neg:     optional sign for negative numbers: '-', '(', space or blank
        trailneg:optional trailing minus indicator:  '-', ')', space or blank
        quantize: None => no quantization,
                  integer (> 0) => quantize to this many decimals
    """

    def __init__(self, value, curr='', sep=' ', dp=',',
                 pos='', neg='-', trailneg='', quantize=2):
        if isinstance(value, Decimal):
            self._value = Money.quantize(value, quantize)
        elif isinstance(value, str):
            self._value = Money.quantize(Decimal(value.replace(",", ".")),
                                         quantize)
        elif isinstance(value, unicode):
            self._value = Money.quantize(Decimal(value.replace(",", ".")),
                                         quantize)
        elif isinstance(value, int):
            self._value = Decimal(value)
        elif isinstance(value, float):
            self._value = Money.quantize(Decimal(str(value)), quantize)
        else:
            print value
            print type(value)
            raise ValueError

        self._curr = curr
        self._sep = sep
        self._dp = dp
        self._pos = pos
        self._neg = neg
        self._trailneg = trailneg
        self._quantize = None

    def machine_format(self):
        return self._value

    def human_format(self):
        """Return money amount in human format"""
        return Money.moneyfmt(self._value, self._curr, self._sep, self._dp,
                       self._pos, self._neg, self._trailneg, self._quantize)

    def __repr__(self):
        return '<Money: %s>' % self.human_format()

    def __str__(self):
        return self.human_format()

    def __int__(self):
        return int(self._value)

    def __float__(self):
        return float(self._value)

    def __unicode__(self):
        return unicode(self.human_format())

    @staticmethod
    def quantize(value, quantize):
        if quantize != None:
            if quantize < 1:
                raise ValueError
            q = Decimal(10) ** - quantize
            return value.quantize(q)
        else:
            return value

    @staticmethod
    def moneyfmt(value, curr='', sep=' ', dp=',',
                 pos='', neg='-', trailneg='', quantize=2):
        """ Convert decimal to a money formatted string.

            >>> d = Decimal('1234567.8901')
            >>> Money.moneyfmt(d)
            '1 234 567,89'
            >>> print Money.moneyfmt(-d)
            -1 234 567,89
            >>> Money.moneyfmt(-d, quantize=None, curr=u' euro')
            u'-1 234 567,8901 euro'
            >>> Money.moneyfmt(d, quantize=None, curr=u'$')
            u'1 234 567,8901$'
        """

        if quantize != None:
            value = Money.quantize(value, quantize)
        sign, digits, exp = value.as_tuple()
        places = -exp
        result = []
        digits = [str(value) for value in digits]
        build, next = result.append, digits.pop
        if sign:
            build(trailneg)
        build(curr)
        for i in range(places):
            build(next() if digits else '0')
        if exp != 0:
            build(dp)
        if not digits:
            build('0')
        i = 0
        while digits:
            build(next())
            i += 1
            if i == 3 and digits:
                i = 0
                build(sep)
        build(neg if sign else pos)
        return ''.join(reversed(result))
