#!/usr/bin/env python

from distutils.core import setup

VERSION = '0.2.3'
DESCRIPTION = 'An extension of multiprocessing.Pool with extra functionality'

setup(
    name='smartpool',
    version=VERSION,
    description=DESCRIPTION,
    author='Jeffrey Jenkins',
    license='MIT',
    author_email='jeff@qcircles.net',
    url='https://github.com/jeffjenkins/smartpool',
    packages=['smartpool'],
    package_data={
        "" : ["*.js", "*.css", "*.sass"],
    },
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)