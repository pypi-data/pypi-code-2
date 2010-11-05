#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright © 2010 Ryan Senkbeil
# 
# This file is part of repoze.what.plugins.mongodb.
#
#    repoze.what.plugins.mongodb is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    repoze.what.plugins.mongodb is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with repoze.what.plugins.mongodb.  If not, see <http://www.gnu.org/licenses/>.
from setuptools import setup, find_packages

setup(name = 'repoze.what.plugins.mongodb',
      version = '0.1',
      description = 'MongoDB adapter plugins for repoze.what',
      author = 'Ryan Senkbeil',
      author_email = 'rsenk330@gmail.com',
      url = 'https://bitbucket.org/rsenk330/repoze.what.plugins.mongodb/',
      classifiers = [
          "Programming Language :: Python",
          "Development Status :: 4 - Beta",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Operating System :: OS Independent"
      ],
      packages = find_packages(),
      install_requires = ['repoze.what',]
)
