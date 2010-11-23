#!/usr/bin/env python2.6

import sys, os
from distutils.core import setup, Extension
from distutils.sysconfig import get_python_inc

setup(
    name = "nimbstor",
    version = "0.2",
    description = "Store incrementally, compressed and encrypted data failsafe in filesystems, IMAPs or other backends.",
    author = "Oleksandr Kozachuk",
    author_email = "ddeus.pypi@mailnull.com",
    url = "http://pypi.python.org/pypi/nimbstor",
    license = "WTFPL",
    packages = ["nimbstor"],
    ext_modules = [
      Extension("nimbstor.adler64",
	sources = ["nimbstor/adler64.c"],
	include_dirs = [get_python_inc(plat_specific=1)],
      ),
    ],
    requires = ['argparse', 'alo_aes', 'pyliblzma'],
    scripts = ["nimbstor/nimbtar"],
    classifiers = [
      'Development Status :: 3 - Alpha',
      'Environment :: Console',
      'Intended Audience :: End Users/Desktop',
      'Intended Audience :: System Administrators',
      'Operating System :: Unix',
      'Operating System :: POSIX',
      'Programming Language :: Python',
      'Topic :: System :: Archiving',
      'Topic :: System :: Archiving :: Backup',
      'Topic :: System :: Archiving :: Compression',
      'Topic :: System :: Archiving :: Mirroring',
      'Topic :: System :: Archiving :: Packaging',
      'Topic :: Utilities',
    ],
)
