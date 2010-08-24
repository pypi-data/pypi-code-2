#!/usr/bin/env python

import os
import shutil
import sys

from distutils.core import setup, Extension

MAJOR, MINOR = sys.version_info[:2]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PKG_BASE = 'Python%i' % MAJOR
SRC_DIR = os.path.join(BASE_DIR, PKG_BASE)

if (MAJOR, MINOR) in ((2,5), (2,6), (2,7), (3,1)):
    unicodedata_db_h = os.path.join(SRC_DIR, 'Python%i%i' % (MAJOR, MINOR),
                                    'unicodedata_db.h')
    shutil.copy(unicodedata_db_h, SRC_DIR)
else:
    sys.exit("No unicodedata_db.h could be prepared for Python %s"
             % sys.version)

setup(
    name='regex',
    version='0.1.20100824',
    description='Alternate regular expression module, to replace re.',
    long_description=open(os.path.join(SRC_DIR, 'Features.rst')).read(),

    # PyPI does spam protection on email addresses, no need to do it here
    author='Matthew Barnett',
    author_email='regex@mrabarnett.plus.com',

    # PyPI appears to overwrite author field with maintainer field
    # avoid apparent plagarism for now.
    #maintainer='Alex Willmer',
    #maintainer_email='alex@moreati.org.uk',

    url='http://bugs.python.org/issue2636',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Python Software Foundation License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: General',
        ],
    license='Python Software Foundation License',

    py_modules = ['regex', '_regex_core'],
    package_dir={'': PKG_BASE},

    ext_modules=[Extension('_regex', [os.path.join(PKG_BASE, '_regex.c')])],
    )
