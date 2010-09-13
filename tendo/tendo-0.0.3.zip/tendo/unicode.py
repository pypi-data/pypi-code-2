#!/usr/bin/python
from __future__ import unicode_literals
import codecs, sys, types, unittest, logging, tempfile

# Author: Sorin Sbarnea <ssbarnea@adobe.com>

# This file does add some additional Unicode support to Python, like:
# * auto-detect BOM on text-file open: open(file, "r") and open(file, "rU")

# we save the file function handler because we want to override it
open_old = open

def open(filename, mode='r', bufsize=-1, fallback_encoding='utf_8'):
		"""
		This respects Python documentation (2.6):
		* mode is by default 'r' if not specified and text mode
		* negative bufsize makes it use the default system one (same as not specified)
		"""
		# Do not assign None to bufsize or mode because calling original open will fail

		# we read the first 4 bytes just to be sure we use the right encoding
		if("r" in mode or "a" in mode): # we are interested of detecting the mode only for read text
			try:
				f = open_old(filename, "rb")
				aBuf = f.read(4)
				f.close()
			except:
				aBuf=''
			if aBuf[:3] ==   b'\xEF\xBB\xBF' :
				f = codecs.open(filename, mode, "utf_8")
				f.seek(3,0)
				f.BOM = codecs.BOM_UTF8
			elif aBuf[:2] == b'\xFF\xFE':
				f = codecs.open(filename, mode, "utf_16_le")
				f.seek(2,0)
				f.BOM = codecs.BOM_UTF16_LE
			elif aBuf[:2] == b'\xFE\xFF':
				f = codecs.open(filename, mode, "utf_16_be")
				f.seek(2,0)
				f.BOM = codecs.BOM_UTF16_BE
			elif aBuf[:4] == b'\xFF\xFE\x00\x00':
				f = codecs.open(filename, mode, "utf_32_le")
				f.seek(4,0)
				f.BOM = codecs.BOM_UTF32_LE
			elif aBuf[:4] == b'\x00\x00\xFE\xFF': 
				f = codecs.open(filename, mode, "utf_32_be")
				f.seek(4,0)
				f.BOM = codecs.BOM_UTF32_BE
			else:  # we assume that if there is no BOM, the encoding is UTF-8
				f = codecs.open(filename, mode, fallback_encoding)
				f.seek(0)
				f.BOM = None
			return f
		else:
			import traceback
			logging.warning("Calling unicode.open(%s,%s,%s) that may be wrong." % (filename, mode, bufsize))
			traceback.print_exc(file=sys.stderr)
			
			return open_old(filename, mode, bufsize)

class testUnicode(unittest.TestCase):

	def test_read_utf8(self):
		try:
			f = open("tests/utf8.txt","rU")
			r = f.readlines()
			f.close()
		except Exception as e:
			self.assertTrue(False, "Unable to properly read valid utf8 encoded file.")

	def test_read_invalid_utf8(self):
		passed = False
		try:
			f = open("tests/utf8-invalid.txt","rU")
			r = f.readlines()
			f.close()
		except Exception as e:
			if isinstance(e, UnicodeDecodeError):
				passed = True # yes, we expect an exception
			pass
		self.assertTrue(passed, "Unable to detect invalid utf8 file")		

	def test_write_on_existing_utf8(self):
		import shutil, filecmp, os
		(ftmp, fname_tmp) = tempfile.mkstemp()
		shutil.copyfile("tests/utf8.txt", fname_tmp)
		f = open(fname_tmp,"a") # encoding not specified, should use utf-8
		f.write("\u0061\u0062\u0063\u0219\u021B\u005F\u1E69\u0073\u0323\u0307\u0073\u0307\u0323\u005F\u0431\u0434\u0436\u005F\u03B1\u03B2\u03CE\u005F\u0648\u062A\u005F\u05D0\u05E1\u05DC\u005F\u6C38\U0002A6A5\u9EB5\U00020000")
		f.close()
		passed = filecmp.cmp("tests/utf8-after-append.txt", fname_tmp, shallow=False)
		self.assertTrue(passed, "Appending to existing UTF-8 file test failed.")
		os.close(ftmp)
		os.unlink(fname_tmp)


if __name__ == '__main__':
	unittest.main()

	#lines = open("test/utf8.txt","rU")
	
	#for line in lines:
	#	print(line)

