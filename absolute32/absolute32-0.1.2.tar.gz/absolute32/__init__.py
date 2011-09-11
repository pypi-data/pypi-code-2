# -*- coding:utf-8 -*-

_hash = hash

def hash(s):
	t = _hash(s) & 0xFFFFFFFF
	if t >= 0x80000000:
		return int(-0x100000000 + t)
	return int(t)

def add(lhs, rhs):
	t = lhs + rhs
	if t >= 0x80000000:
		return int(-0x100000000 + t)
	return int(t)

import zlib

def crc(data, value = None):
	if value is not None:
		t = zlib.crc32(data, value)
	else:
		t = zlib.crc32(data)
	if t >= 0x80000000:
		return int(-0x100000000 + t)
	return int(t)

def adler(data, value = None):
	if value is not None:
		t = zlib.adler32(data, value)
	else:
		t = zlib.adler32(data)
	if t >= 0x80000000:
		return int(-0x100000000 + t)
	return int(t)

