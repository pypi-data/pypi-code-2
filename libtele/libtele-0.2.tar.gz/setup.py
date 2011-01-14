#!/usr/bin/env python
#-*- coding: utf8 -*-
from setuptools import setup
from __init__ import __version__

readme = ""
with open("README") as fp:
    readme = fp.read()

setup(name="libtele",
      version=__version__,
      description="Library for interfacing http://tele.at/.",
      author="Michael Kainer",
      author_email="kaini1123@gmail.com",
      url="https://github.com/kaini/libtele",
      package_dir={"tele": "."},
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
      long_description=readme
     )
