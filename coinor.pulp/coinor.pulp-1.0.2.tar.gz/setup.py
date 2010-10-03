#!/usr/bin/env python

# Bootstrap installation of Distribute
import distribute_setup
distribute_setup.use_setuptools()

import os

from setuptools import setup


PROJECT = u'coinor.pulp'
VERSION = '1.0.2'
URL = 'http://www.coin-or.org/PuLP/'
AUTHOR = u'Stuart Mitchell'
AUTHOR_EMAIL = u's.mitchell@auckland.ac.nz'
DESC = """This is a package that wraps pulp and imports it into the namespace
package coinor."""

def read_file(file_name):
    file_path = os.path.join(
        os.path.dirname(__file__),
        file_name
        )
    return open(file_path).read()

setup(
    name=PROJECT,
    version=VERSION,
    description=DESC,
    long_description=read_file('README.rst'),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license=read_file('LICENSE'),
    namespace_packages=[u'coinor'],
    packages=[u'coinor.pulp', u'coinor'],
    package_dir = {'': os.path.abspath(os.path.dirname(__file__))},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "pulp"
    ],
    classifiers=[
         'Development Status :: 5 - Production/Stable',
         'Environment :: Console',
         'Intended Audience :: Science/Research',
         'License :: OSI Approved :: BSD License',
         'Natural Language :: English',
         'Programming Language :: Python',
         'Topic :: Scientific/Engineering :: Mathematics',
    ],
)
