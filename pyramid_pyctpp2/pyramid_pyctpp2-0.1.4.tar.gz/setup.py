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

from setuptools import setup, find_packages
import os

def read(filename):
    prjdir = os.path.dirname(__file__)
    return open(os.path.join(prjdir, filename)).read()

LONG_DESC = read('README.rst') + '\nCHANGES\n=======\n\n' + read('CHANGES.rst')

setup(name='pyramid_pyctpp2',
      version='0.1.4',
      description="pyctpp2 template bindings for the Pyramid web framework",
      long_description=LONG_DESC,
      classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Framework :: Pylons',
        'License :: OSI Approved :: MIT License',
          ],
      keywords='web wsgi pylons pyramid',
      author='Konstantin Lepa',
      author_email='konstantin.lepa@gmail.com',
      url='http://bitbucket.org/klepa/pyramid_pyctpp2',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=['pyramid>=1.0a10', 'pyctpp2'],
      )
