#! /usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
from httpforgelib import VERSION

setup(
  name="httpforge",
  version=VERSION,
  author="Antoine d'Otreppe de Bouvette",
  author_email="a.dotreppe@aspyct.org",
  py_modules=["httpforgelib"],
  scripts=["httpforge", "httpextract", "httpsend"],
  url="http://www.aspyct.org/",
  license="MIT",
  description="Command line tools to manipulate HTTP requests and responses"
)
