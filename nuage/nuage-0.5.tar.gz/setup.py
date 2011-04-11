#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from nuage import get_version

fd = open("README")
long_description = fd.read()
fd.close()

setup(
    name='nuage',
    version=get_version(),
    description='Command line client for manage applications in nuage platform',
    author='The Nuage Team',
    author_email='team@nuagehq.com',
    license='BSD',
    keywords='cloud django wsgi deployment',
    url="http://www.nuagehq.com/",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['argparse', 'argh', 'httplib2', 'simplejson'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: BSD License",
        ],
    entry_points="""
    [console_scripts]
    nuage = nuage.cli:main
    """,
    )
