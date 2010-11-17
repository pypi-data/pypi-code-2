#!/usr/bin/env python

from distutils.core import setup

setup(name = "Datat",
      version = "1.1.0",
      description = "Intuitive data tables, with translation to R data frames.",
      long_description = """A *datat* is an intuitive 2D data table, inspired by R's "data frames".
      
      Datats can hold rows in a sequence (behaving like a Python list), or by name (behaving like a Python dictionary). They can be saved to, and loaded from, CSV files, and translated into an R data frame using rpy2_.
      
      For more details, see the `user guide`_.
      
      .. _rpy2: http://pypi.python.org/pypi/rpy2
      .. _user guide: http://packages.python.org/Datat/""",
      author = "Thomas Kluyver",
      author_email = "takowl@gmail.com",
      url = "http://packages.python.org/Datat/",
      packages = ["datat"],
      classifiers = ["Intended Audience :: Science/Research",
      "License :: OSI Approved :: MIT License",
      "Programming Language :: Python",
      "Programming Language :: Python :: 2",
      "Programming Language :: Python :: 3",])
