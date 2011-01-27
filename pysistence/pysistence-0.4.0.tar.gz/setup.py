# Technically, we don't need this in python 2.6+, but it isn't hurting anything.
from __future__ import with_statement

import sys
import tarfile
from tempfile import mkdtemp
from shutil import copy, rmtree
from os.path import abspath, join, isdir, isfile
from os import mkdir, remove

from setuptools import setup, find_packages
from distutils.extension import Extension


name = 'pysistence'
version = '0.4.0'
base_name = '%s-%s' % (name, version)
tarball_name = '%s.tar.gz' % base_name

ext_modules = []
if '--with-cext' in sys.argv:
    ext_modules.append(
            Extension('pysistence._persistent_list',
                      ['source/pysistence/_persistent_list.c'], ))
    sys.argv.remove('--with-cext')

with open("README") as README:
    # See?  The installer reads the README for the user!
    README_text = README.read()

setup(
    name=name,
    packages=find_packages('source'),
    package_dir = {'':'source'},
    version=version,
    url="http://packages.python.org/pysistence",
    description='A set of functional data structures for Python',
    long_description=README_text,
    author="Jason Baker",
    author_email="amnorvend@gmail.com",
    test_suite = 'nose.collector',
    tests_require = ['nose', 'coverage'],
    license='License :: OSI Approved :: MIT License',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    ext_modules = ext_modules,
    zip_safe=False,
)
