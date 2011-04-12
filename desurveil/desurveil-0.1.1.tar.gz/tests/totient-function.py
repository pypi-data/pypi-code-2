#!/usr/bin/env python3

# desurveil: a cryptography tool with support for RSA and OAEP
# Copyright (C) 2011 Niels Serup

# This file is part of desurveil.
#
# desurveil is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# desurveil is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with desurveil.  If not, see <http://www.gnu.org/licenses/>.

"""
This test examines the spread in Euler's totient function.
"""

import sys
import os

try: import desurveil
except ImportError: sys.path.insert(0, os.path.split(os.path.dirname(
            os.path.realpath(__file__)))[0])

import desurveil.basemath as bmath

class DictWithStartValue(dict):
    def __init__(self, start_value):
        self.start_value = start_value
        dict.__init__(self)

    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            dict.__setitem__(self, key, self.start_value())
            return dict.__getitem__(self, key)

def prime_factorize(n):
    # If an already existing factor appears, add the exponent with 1 instead of
    # thinking of it as a new factor
    fs = DictWithStartValue(lambda: 0)

    while n > 1:
        for i in range(2, bmath.integer_sqrt(n) + 1):
            if n % i == 0:
                # If i is a divisor of n, i is a factor to n (and since we
                # start at the bottom, i is also a prime number)
                fs[i] += 1
                break
        else:
            # At the end a prime number which cannot be factored further will
            # be found. This is added to the list.
            fs[n] += 1
            return fs
        # Now the factor is already in the list, so by dividing n with i a
        # smaller range in the next loop is achieved while there is still place
        # for other factors
        n //= i

def totient(n):
    if n < 1 or not isinstance(n, int):
        raise ValueError('n must be a positive integer')
    if n == 1:
        return 1
    ps = prime_factorize(n)
    pr = 1
    for p, k in ps.items():
        pr *= (p - 1) * p**(k - 1)
    return pr

def find_totients(start=1, end=5000, step=1):
    for i in range(start, end + 1, step):
        yield i, totient(i)

if __name__ == '__main__':
    try: fmt = sys.argv[4]
    except IndexError: fmt = '{}\t{}' # tsv format
    for i, number in find_totients(*(map(int, sys.argv[1:4]))):
        info = fmt.format(i, number)
        print(info)
        print(info, file=sys.stderr)
