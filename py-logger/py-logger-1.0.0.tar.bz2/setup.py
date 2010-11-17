#!/usr/bin/env python

from setuptools import setup, find_packages
setup(name='py-logger',
      version='1.0.0',
      description='Multi-instantiable logger for python projects',
      author='Alexey Loshkarev',
      author_email='elf2001@gmail.com',
      url='http://code.google.com/p/py-logger/',
      packages=find_packages(),
      license='GPL',
      classifiers=[
          "Development Status :: 5 - Production/Stable", 
          "Intended Audience :: Developers",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Natural Language :: English",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          ],
      )
