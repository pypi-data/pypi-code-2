#!/usr/bin/python3

from distutils.core import setup

setup(name='qfathom', version='0.1.0', 
      packages=['qfathom'], scripts=['scripts/qfathom'],
      description='database administration tool', author='Filip Gruszczyński',
      author_email='gruszczy@gmail.com', url='http://code.google.com/p/qfathom',
      classifiers = ["Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent"])

