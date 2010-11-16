#!/usr/bin/env python

from setuptools import setup

import os
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='transdb',
    version='0.9',
    description="I18n django reusable app ",
    author='garcia.marc',
    url='http://code.google.com/p/transdb/',
    packages=['transdb'],
    maintainer_email = "di@sferos.com",
    keywords = ["django", "translation", 
        "internationalization", "i18n", "database", "model"],
    classifiers = [
        "Programming Language :: Python",
        "Topic :: Software Development :: Internationalization",
        "Framework :: Django",
        ],
    long_description = read('README'),    
    )
