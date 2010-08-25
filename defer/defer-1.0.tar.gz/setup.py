#!/usr/bin/env python
import os
from setuptools import setup

import defer

readme = open(os.path.join(os.path.dirname(__file__), "README")).read()

setup(name="defer",
      version=defer.__version__,
      description="Simple framework for asynchronous programming",
      long_description=readme,
      author="Sebastian Heinlein",
      author_email="devel@glatzor.de",
      license = "GNU GPL",
      url="http://launchpad.net/python-defer",
      keywords="async defer dbus asynchronous",
      classifiers=["Development Status :: 5 - Production/Stable",
                   "License :: OSI Approved :: " \
                           "GNU General Public License (GPL)",
                   "Programming Language :: Python",
                   "Topic :: Software Development :: Libraries :: " \
                           "Python Modules"],
      packages=["defer"],
      test_suite="nose.collector",
      test_requires=["Nose"],
      platforms = "posix")

