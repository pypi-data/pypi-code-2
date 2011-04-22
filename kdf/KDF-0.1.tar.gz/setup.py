#!/usr/bin/env python

from distutils.core import setup

setup(name='KDF',
      py_modules=['KDF'],
      version='0.1',
      description='Key Derivation functions from ISO 18033',    
      keywords = ["key derivation", "kdf", 'KDF1','KDF2','KDF3','KDF4', "ISO 18033", "ISO-18033"],

      author='Peio Popov',
      author_email='peio@peio.org',
      license = 'Public Domain',
      url = 'http://peio.org/code/',

      classifiers = ['Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Education',
        'License :: Public Domain',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Security :: Cryptography'],
        long_description = '''\


KDF -  ISO 18033 Key derivation functions
------------------------------

Key derivation functions (KDF1,KDF2,KDF3,KDF4) as defined in section 6.2 of ISO 18033

A key derivation function is a function KDF (x, l) that takes as input an octet string x and
an integer l >= 0, and outputs an octet string of length l. The string x is of arbitrary length,
although an implementation may define a (very large) maximum length for x and maximum size
for l, and fail if these bounds are exceeded.

'''
      )

