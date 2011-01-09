#!/usr/bin/env python
#-*- coding: utf8 -*-
from setuptools import setup

setup(name="libtele",
      version="0.1",
      description="Library for interfacing http://tele.at/.",
      author="Michael Kainer",
      author_email="kaini1123@gmail.com",
      url="https://github.com/kaini/libtele",
      package_dir={"tele": "."},
      package_data={"tele": ["test/mockups/*"]},
      packages=["tele"],
      license="GPLv3",
      requires=["lxml", "pytz", "twisted"],
      provides=["tele"],
      classifiers=[
          "Development Status :: 4 - Beta",
          "Framework :: Twisted",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Natural Language :: English",
          "Natural Language :: German",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Topic :: Utilities",
          "Topic :: Internet"],
      long_description="""
          ``libtele``
          ===========
          This is a simple library that uses Twisted to fetch the TV guide from
          http://tele.at/ and parses it into an pythonic manner.
          
          Please read the documentation for further details:
		  http://kaini.github.com/libtele/index.html
      """
     )
