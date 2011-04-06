#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2011 Volvox Development Team
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Author: Konstantin Lepa <konstantin.lepa@gmail.com>

import sys
import os
import re

def touch(*args):
    return open(os.path.join(*args), 'w')

prjdir = os.path.dirname(__file__)

# Ugly hack for setuptools
try:
    import Cython

    pyrexdir = os.path.join(prjdir, '.pyrex', 'Pyrex')
    if not os.path.exists(pyrexdir):
        os.makedirs(os.path.join(pyrexdir, 'Distutils'))
        touch(pyrexdir, '__init__.py')
        touch(pyrexdir, 'Distutils', '__init__.py')
        touch(pyrexdir, 'Distutils', 'build_ext.py').write('build_ext = 1')

    sys.path.append(os.path.join(prjdir, '.pyrex'))

    CYTHON_INSTALLED = True
except ImportError:
    CYTHON_INSTALLED = False
    pass

from setuptools import setup

if CYTHON_INSTALLED:
    from Cython.Distutils.extension import Extension

    if 'setuptools.extension' in sys.modules:
        m = sys.modules['setuptools.extension']
        m.Extension.__dict__ = m._Extension.__dict__

    from Cython.Distutils import build_ext as _build_ext
    CYTHON_PYX = 'vxrpc.pyx'
else:
    from setuptools.extension import Extension
    from setuptools.command.build_ext import build_ext as _build_ext
    CYTHON_PYX = 'vxrpc_py%s.c' % sys.version_info[0]

from distutils.version import LooseVersion

srcdir = os.path.join(prjdir, 'src')
touch(os.path.join(srcdir, 'pyversion.pxi')).write(
    'DEF PYTHON_VERSION = %s' % sys.version_info[0]
    )

def read(filename):
    return open(os.path.join(prjdir, filename)).read()

LONG_DESC = read('README.rst') + '\nCHANGES\n=======\n\n' + read('CHANGES.rst')

sys.path.append(srcdir)
from version import VERSION

library_dirs = ['/usr/local/lib',
                '/usr/lib',
                '/opt/local/lib'
                ]

include_dirs = [srcdir,
                '/usr/local/include',
                '/usr/include',
                '/opt/local/include'
                ]

class BuildVxRPC(_build_ext):
    def build_extension(self, ext):
        _build_ext.build_extension(self, ext)
        if not CYTHON_INSTALLED:
            print("WARNING: Used pre-generated `vxrpc.c'")

    def finalize_options(self):
        _build_ext.finalize_options(self)
        config = self.get_finalized_command('config')
        if not config.compiler:
            config.compiler = self.compiler
        if not config.check_lib('xmlrpc_client', library_dirs=library_dirs):
            raise Exception('Failed to found xmlrpc-c client library.')
        if not config.check_header('xmlrpc-c/client.h',
                include_dirs=include_dirs):
            raise Exception('Failed to found xmlrpc-c/client.h header.')
        for incdir in include_dirs:
            path = os.path.join(incdir, 'xmlrpc-c/client.h')
            if os.path.isfile(path):
                break

        self.run_command('config')

module = Extension(
        'vxrpc',
        [ os.path.join(srcdir, CYTHON_PYX),
          os.path.join(srcdir, 'structsize.c')
          ],
        include_dirs=include_dirs,
        library_dirs=library_dirs,
        libraries=['xmlrpc_client'],
        define_macros=[('NDEBUG',)]
        )

setup(
        name='vxrpc',
        version='.'.join([str(v) for v in VERSION]),
        author="Konstantin Lepa",
        author_email="konstantin.lepa@gmail.com",
        maintainer="Konstantin Lepa",
        maintainer_email="konstantin.lepa@gmail.com",
        contact_email="konstantin.lepa@gmail.com",
        url='http://bitbucket.org/klepa/vxrpc',
        package_dir={'': 'src'},
        license='MIT',
        description='XML-RPC client',
        long_description=LONG_DESC,
        cmdclass={ 'build_ext': BuildVxRPC },
        ext_modules=[module],
        classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: POSIX',
            'Programming Language :: Cython',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Topic :: Internet'
            ],
        requires=['Cython(>=0.14)']
    )

