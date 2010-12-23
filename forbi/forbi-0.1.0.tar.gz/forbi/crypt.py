#!/usr/bin/env python
# -*- coding: utf-8 -*-

# forbi: a TCP-based communication tool
# Copyright (C) 2010  Niels Serup

# This file is part of forbi.
#
# forbi is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# forbi is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General
# Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with forbi. If not, see
# <http://www.gnu.org/licenses/>.

##[ Maintainer  ]## Niels Serup <ns@metanohi.org>
##[ Description ]## Cryptography-related functions

import tempfile
import M2Crypto
import base64

def generate_keys():
    """Generate a 1024-bit keypair"""
    priv = M2Crypto.RSA.gen_key(1024, 65537)
    tf = tempfile.NamedTemporaryFile()
    priv.save_pub_key(tf.name)
    pub = M2Crypto.RSA.load_pub_key(tf.name)
    tf.seek(0)
    pub_str = tf.read()
    return priv, pub, pub_str

def create_pub_key_from_string(string):
    """Transform a string in the PEM format into a public key object"""
    tf = tempfile.NamedTemporaryFile()
    tf.write(string)
    tf.seek(0)
    pub = M2Crypto.RSA.load_pub_key(tf.name)
    return pub

def encrypt(msg, pub):
    """Encrypt plaintext with a public key"""
    padding = M2Crypto.RSA.pkcs1_oaep_padding
    ctxt=pub.public_encrypt(msg, padding)
    return ctxt

def decrypt(msg, priv):
    """Decrypt ciphertext with a private key"""
    padding = M2Crypto.RSA.pkcs1_oaep_padding
    ctxt=priv.private_decrypt(msg, padding)
    return ctxt

def generate_random_bytes():
    """Generate 128 bytes of pseudo-randomness"""
    return base64.b64encode(M2Crypto.Rand.rand_bytes(128))
