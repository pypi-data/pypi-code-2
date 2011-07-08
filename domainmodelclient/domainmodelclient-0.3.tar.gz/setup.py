#!/usr/bin/env python
import os
import sys

from setuptools import setup, find_packages

sys.path.insert(0, './src')
from dmclient import __version__

long_description = open('README').read() + open('INSTALL').read()

setup(
    name='domainmodelclient',
    version=__version__,
    package_dir={'': 'src'},
    packages=find_packages('src'),
    zip_safe = False,
    install_requires = [],
    author='Appropriate Software Foundation',
    author_email='domainmodel-support@appropriatesoftware.net',
    license='MIT',
    url='http://appropriatesoftware.net/domainmodel',
    description='Python client for the Domain Model API',
    long_description = long_description,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',],
)
