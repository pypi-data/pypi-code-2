#!/usr/bin/env python

from distutils.core import setup

'Packaging instructions from: http://diveintopython3.org/packaging.html'

setup(name='DataPrimitives',
      py_modules=['DataPrimitives'],
      version='0.51',
      description='Data primitives conversions from ISO 18033 and PKCS#1',    
      keywords = ['Data Primitives', 'bit string', 'octet string', 'integer', 'conversion', 'OS2BSP', 'BS2OSP', 'BS2IP', 'I2BSP','OS2IP','I2OSP', 'strxor', 'strings xor', 'ISO', 'PKCS', 'ISO 18033', 'PKCS#1'],

      author='Peio Popov',
      author_email='peio@peio.org',
      license = 'Public Domain',
      url = 'http://pypi.python.org/pypi/DataPrimitives',

      classifiers = ['Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Education',
        'License :: Public Domain',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Security :: Cryptography'],
        long_description = '''\


Data primitives conversions from ISO 18033 and PKCS#1
-----------------------------------------------------

Classes to convert between Data Primitives such as 'bit string', 'octet string' and 'integer' as defined and explained in ISO 18033 and PKCS#1.

The implementation created for educational purposes. No optimisations and "tricks" are used and is more easy to be read than optimal to use.

You may turn on detailed explanation mode by suppling a True argument to the main class. Examples included in the README.txt file.
'''
      )

