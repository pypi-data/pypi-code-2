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

from __future__ import print_function
import sys
import os
import re

def touch(*args):
    return open(os.path.join(*args), 'w')

pyrexdir = os.path.join(os.path.dirname(__file__), '.pyrex', 'Pyrex')
if not os.path.exists(pyrexdir):
    os.makedirs(os.path.join(pyrexdir, 'Distutils'))
    touch(pyrexdir, '__init__.py')
    touch(pyrexdir, 'Distutils', '__init__.py')
    touch(pyrexdir, 'Distutils', 'build_ext.py').write('build_ext = 1')

sys.path.append(os.path.join(os.path.dirname(__file__), '.pyrex'))

from setuptools import setup
from Cython.Distutils.extension import Extension

if 'setuptools.extension' in sys.modules:
    m = sys.modules['setuptools.extension']
    m.Extension.__dict__ = m._Extension.__dict__

from distutils.version import LooseVersion
from Cython.Distutils import build_ext as _build_ext

with open(os.path.join(os.path.dirname(__file__),
                       'src', 'pyversion.pxi'), 'w') as F:
    print('DEF PYTHON_VERSION = %s' % sys.version_info[0], file=F)

def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

LONG_DESC = read('README.txt') + '\nCHANGES\n=======\n\n' + read('CHANGES.txt')

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from version import VERSION, CTPP2_VERSION

library_dirs = ['/usr/local/lib',
                '/usr/lib',
                '/opt/local/lib'
                ]

include_dirs = [os.path.join(os.path.dirname(__file__), 'src'),
                '/usr/local/include/ctpp2',
                '/usr/include/ctpp2',
                '/usr/local/include',
                '/usr/include',
                '/opt/local/include/ctpp2'
                ]

class BuildPyCTPP2(_build_ext):
    def finalize_options(self):
        _build_ext.finalize_options(self)
        config = self.get_finalized_command('config')
        if not config.compiler:
            config.compiler = self.compiler
        if not config.check_lib('ctpp2', library_dirs=library_dirs):
            raise Exception('Failed to found ctpp2 library.')
        if not config.check_header('CTPP2SysHeaders.h',
                include_dirs=include_dirs):
            raise Exception('Failed to found ctpp2 header.')
        for incdir in include_dirs:
            path = os.path.join(incdir, 'CTPP2SysHeaders.h')
            if os.path.isfile(path):
                break

        p = re.compile('define\s+CTPP_VERSION\s+"(\d+\.\d+)(?:\.[^"]*)?"')
        m = p.search(open(path).read())
        if m:
            ctpp2_version = m.group(1)
        else:
            raise Exception('Failed to check ctpp2 version.')

        required_version = '.'.join([str(v) for v in CTPP2_VERSION])
        if LooseVersion(ctpp2_version) != LooseVersion(required_version):
            raise Exception('Required ctpp2 library is %s' % required_version)

        self.run_command('config')

module = Extension(
        'pyctpp2',
        [ os.path.join(os.path.dirname(__file__), 'src', 'pyctpp2.pyx'),
          os.path.join(os.path.dirname(__file__), 'src', 'cengine.cc'),
          os.path.join(os.path.dirname(__file__), 'src', 'ctemplate.cc')
          ],
        language='c++',
        include_dirs=include_dirs,
        library_dirs=library_dirs,
        libraries=['stdc++', 'ctpp2'],
        extra_compile_args=['-fno-rtti', '-fomit-frame-pointer'],
        define_macros=[('NDEBUG',)],
        pyrex_c_in_temp=True
        )

setup(
        name='pyctpp2',
        version='.'.join([str(v) for v in VERSION]),
        author="Konstantin Lepa",
        author_email="konstantin.lepa@gmail.com",
        maintainer="Konstantin Lepa",
        maintainer_email="konstantin.lepa@gmail.com",
        contact_email="konstantin.lepa@gmail.com",
        url='http://bitbucket.org/klepa/pyctpp2',
        package_dir={'': 'src'},
        license='MIT',
        description='Python interface to CTPP2 library.',
        long_description=LONG_DESC,
        cmdclass={ 'build_ext': BuildPyCTPP2 },
        ext_modules=[module],
        classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: POSIX',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
            'Topic :: Text Processing :: Markup :: HTML'
            ],
        setup_requires=['Cython>=0.14', 'setuptools']
    )

