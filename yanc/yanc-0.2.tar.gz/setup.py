#!/usr/bin/env python

import os

from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), "README.rst")).read()


setup(name="yanc",
      version="0.2",
      description="Yet another nose colorer",
      long_description=README,
      license="MIT",
      keywords="nose color",
      author="Ischium",
      author_email="support@ischium.net",
      url="https://github.com/ischium/yanc",
      install_requires=("termcolor",),
      py_modules=("yanc",),
      entry_points={
          "nose.plugins" : ("yanc=yanc:YANC",),
          },
      )
