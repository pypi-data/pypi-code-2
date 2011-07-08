#!/usr/bin/env python
import os
import sys

from setuptools import setup, find_packages

long_description = open('README').read() + open('INSTALL').read()

sys.path.insert(0, './src')
from quantclient import __version__

setup(
    name='quantclient',
    version=__version__,
    package_dir={'': 'src'},
    packages=find_packages('src'),
    zip_safe = False,
    install_requires = [
        'domainmodelclient==0.3',
    ],
    author='Appropriate Software Foundation',
    author_email='quant-support@appropriatesoftware.net',
    license='MIT',
    url='http://appropriatesoftware.net/quant',
    description='Python client for the Quant API',
    long_description = long_description,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Office/Business :: Financial',
        'Topic :: Office/Business :: Financial :: Investment',
        'Topic :: Office/Business :: Financial :: Spreadsheet',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Software Development :: Libraries :: Python Modules'],
)
