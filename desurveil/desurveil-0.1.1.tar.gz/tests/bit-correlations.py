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
This test checks for correlations in the number of bits, keypair generation,
encryption, and decryption. For each bit length, speed is checked. The
following combinations are checked:

* RSA only
* RSA and overflow
* RSA, OAEP, and overflow

(RSA and OAEP without overflow is not tested, because OAEP in most cases
requires more space than a single RSA encryption allows for.) The inputs for
encryption and decryption are pseudo-random.
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

def test_bit_correlations(start=16, end=1024, step=4,
                          key_gens=10, crypts_for_each_key_gen=10):
    keys_range = tuple(range(key_gens))
    crypts_range = tuple(range(crypts_for_each_key_gen))
    c = key_gens * crypts_for_each_key_gen
    for i in range(start, end + 1, step):
        key_time = 0
        enc_rsa_time = 0
        enc_rsa_overflow_time = 0
        enc_rsa_oaep_overflow_time = 0
        dec_rsa_time = 0
        dec_rsa_overflow_time = 0
        dec_rsa_oaep_overflow_time = 0
        for j in keys_range:
            tmp_time, pubpriv = time_exec(
                lambda: generate_keypair(i), True)
            key_time += tmp_time
            pub, priv = pubpriv
            for k in crypts_range:
                r = random.randrange(0, pub.numbers['n'])
                enc_rsa_time += time_exec(
                    lambda: pub.encrypt(r, False, False))
                dec_rsa_time += time_exec(
                    lambda: priv.decrypt(r, False, False))

                # 64 bytes is an acceptable tester
                r = bmath.i2osp(bmath.create_number(512))
                tmp_time, encr = time_exec(
                    lambda: pub.encrypt(r, False, True), True)
                enc_rsa_overflow_time += tmp_time
                dec_rsa_overflow_time += time_exec(
                    lambda: priv.decrypt(encr, False, True))
                
                tmp_time, encr = time_exec(
                    lambda: pub.encrypt(r, True, True), True)
                enc_rsa_oaep_overflow_time += tmp_time
                dec_rsa_oaep_overflow_time += time_exec(
                    lambda: priv.decrypt(encr, True, True))

        yield i, key_time / key_gens, enc_rsa_time / c, \
            dec_rsa_time / c, enc_rsa_overflow_time / c, \
            dec_rsa_overflow_time / c, \
            enc_rsa_oaep_overflow_time / c, \
            dec_rsa_oaep_overflow_time / c

if __name__ == '__main__':
    try: infofmt = sys.argv[6]   # tsv format
    except IndexError: infofmt = '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}'
    try: helpfmt = sys.argv[7]
    except IndexError: helpfmt = '''\
bits: {}, key: {}
RSA enc: {}, RSA dec: {}
RSA-overflow enc: {}, RSA-overflow dec: {}
RSA-OAEP-overflow enc: {}, RSA-OAEP-overflow dec: {}
'''

    for bits, key, enc_rsa, dec_rsa, enc_rsa_overflow, \
            dec_rsa_overflow, enc_rsa_overflow_oaep, \
            dec_rsa_overflow_oaep in \
            test_bit_correlations(*(map(int, sys.argv[1:6]))):

        infostr = infofmt.format(bits, key, enc_rsa, dec_rsa,
                                 enc_rsa_overflow, dec_rsa_overflow,
                                 enc_rsa_overflow_oaep,
                                 dec_rsa_overflow_oaep)

        helpstr = helpfmt.format(bits, key, enc_rsa, dec_rsa,
                                 enc_rsa_overflow, dec_rsa_overflow,
                                 enc_rsa_overflow_oaep,
                                 dec_rsa_overflow_oaep)

        print(helpstr, file=sys.stderr)
        print(infostr)
