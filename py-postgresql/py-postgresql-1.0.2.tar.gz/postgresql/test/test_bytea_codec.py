##
# .test.test_bytea_codec
##
import unittest
import struct
from ..encodings import bytea

byte = struct.Struct('B')

class test_bytea_codec(unittest.TestCase):
	def testDecoding(self):
		for x in range(255):
			c = byte.pack(x)
			b = c.decode('bytea')
			# normalize into octal escapes
			if c == b'\\' and b == "\\\\":
				b = "\\" + oct(b'\\'[0])[2:]
			elif not b.startswith("\\"):
				b = "\\" + oct(ord(b))[2:]
			if int(b[1:], 8) != x:
				self.fail(
					"bytea encoding failed at %d; encoded %r to %r" %(x, c, b,)
				)

	def testEncoding(self):
		self.failUnlessEqual('bytea'.encode('bytea'), b'bytea')
		self.failUnlessEqual('\\\\'.encode('bytea'), b'\\')
		self.failUnlessRaises(ValueError, '\\'.encode, 'bytea')
		self.failUnlessRaises(ValueError, 'foo\\'.encode, 'bytea')
		self.failUnlessRaises(ValueError, r'foo\0'.encode, 'bytea')
		self.failUnlessRaises(ValueError, r'foo\00'.encode, 'bytea')
		self.failUnlessRaises(ValueError, r'\f'.encode, 'bytea')
		self.failUnlessRaises(ValueError, r'\800'.encode, 'bytea')
		self.failUnlessRaises(ValueError, r'\7f0'.encode, 'bytea')
		for x in range(255):
			seq = ('\\' + oct(x)[2:].lstrip('0').rjust(3, '0'))
			dx = ord(seq.encode('bytea'))
			if dx != x:
				self.fail(
					"generated sequence failed to map back; current is %d, " \
					"rendered %r, transformed to %d" %(x, seq, dx)
				)

if __name__ == '__main__':
	from types import ModuleType
	this = ModuleType("this")
	this.__dict__.update(globals())
	unittest.main(this)
