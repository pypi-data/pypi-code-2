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
This test checks the encryption and decryption speed with RSA-overflow-OAEP at
different message lengths.
"""

import sys
import os
import random

try: import desurveil
except ImportError: sys.path.insert(0, os.path.split(os.path.dirname(
            os.path.realpath(__file__)))[0])

from desurveil.keypair import generate_keypair
from desurveil.testing import time_exec
import desurveil.basemath as bmath

def _enc(pub, data, each):
    for x in each:
        pub.encrypt(data)

def _dec(priv, data, each):
    for x in each:
        priv.decrypt(data)

def test_for_data(bl=1024, begin=4, end=1024, step=4, each=10):
    pub, priv = generate_keypair(bl)
    eachr = tuple(range(each))
    for i in range(begin, end + 1, step):
        in_data = bmath.i2osp(bmath.create_number(i * 8))
        out_data = pub.encrypt(in_data)
        enc_time = time_exec(lambda: _enc(pub, in_data, eachr)) / each
        dec_time = time_exec(lambda: _dec(priv, out_data, eachr)) / each
        yield i, enc_time, len(out_data), dec_time

if __name__ == '__main__':
    try: fmt = sys.argv[6]
    except IndexError: fmt = '{}\t{}\t{}\t{}' # tsv format
    for enc_bytes, enc, dec_bytes, dec in \
            test_for_data(*(map(int, sys.argv[1:6]))):
        info = fmt.format(enc_bytes, enc, dec_bytes, dec)
        print(info)
        print(info, file=sys.stderr)
