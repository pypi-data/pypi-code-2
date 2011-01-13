#!/usr/bin/env python

from distutils.core import setup

setup(
    name = 'msparser',
    py_modules = ['msparser'],
    version = '1.1',
    description = 'Valgrind massif.out parser',
    long_description = open('README.txt').read(),
    author='Mathieu Turcotte',
    author_email='turcotte.mat@gmail.com',
    url='http://mathieuturcotte.ca/',
    keywords = ["valgrind", "massif", "parser"],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: General",
    ]
)
