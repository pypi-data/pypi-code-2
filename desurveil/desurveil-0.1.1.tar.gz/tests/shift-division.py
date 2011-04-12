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
This test checks the speed of shifts and of divisions with 2.
"""

import sys
import os

try: import desurveil
except ImportError: sys.path.insert(0, os.path.split(os.path.dirname(
            os.path.realpath(__file__)))[0])

from desurveil.testing import time_exec

def _run_shift(start, stop, step):
    for i in range(start, stop, step):
        i >> 1

def _run_division(start, stop, step):
    for i in range(start, stop, step):
        i // 2

def test_shift_division(start=0, end=10000000, step=1):
    stop = end + 1
    return time_exec(lambda: _run_shift(start, stop, step)), \
        time_exec(lambda: _run_division(start, stop, step))

if __name__ == '__main__':
    shift_time, division_time = test_shift_division(
        *(map(int, sys.argv[1:4])))
    print(shift_time, division_time)
