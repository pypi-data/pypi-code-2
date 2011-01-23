#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from distutils.core import setup

setup(
    name='ConflictsOptionParser',
    version='0.1.1',
    author='Christopher D. Lasher',
    author_email='chris.lasher@gmail.com',
    packages=['conflictsparse', 'conflictsparse.tests'],
    url='http://pypi.python.org/pypi/ConvUtils/',
    license='MIT License',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries'
    ],
    description=("A command line interface that recognizes "
        "conflicting options given as arguments."),
    long_description=open('README.rst').read(),
)

