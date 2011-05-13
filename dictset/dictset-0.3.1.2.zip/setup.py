# Copyright (c) 2011, Roger Lew [see LICENSE.txt]
# This software is funded in part by NIH Grant P20 RR016454.

##from distutils.core import setup
from setuptools import setup

setup(name='dictset',
    version='0.3.1.2',
    description='A specialized Python container datatype for managing collections of sets.',
    author='Roger Lew',
    author_email='rogerlew@gmail.com',
    license = "BSD",
    classifiers=["Development Status :: 5 - Production/Stable",
                 "Intended Audience :: Developers",
                 "License :: OSI Approved :: BSD License",
                 "Natural Language :: English",
                 "Programming Language :: Python :: 2.5",
                 "Programming Language :: Python :: 2.6",
                 "Programming Language :: Python :: 2.7",
                 "Programming Language :: Python :: 3",
                 "Programming Language :: Python :: 3.0",
                 "Programming Language :: Python :: 3.1",
                 "Programming Language :: Python :: 3.2",
                 "Topic :: Scientific/Engineering :: Information Analysis",
                 "Topic :: Scientific/Engineering :: Mathematics",
                 "Topic :: Software Development :: Libraries :: Python Modules"],
    url='http://code.google.com/p/dictset/',
    py_modules=['dictset'],
      )

"""setup.py sdist upload --identity="Roger Lew" --sign"""
