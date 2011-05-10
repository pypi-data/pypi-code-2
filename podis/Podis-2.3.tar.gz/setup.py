#! /usr/bin/env python
# -*- coding: utf-8 -*-


# Podis -- Retrieve INSEE codes of french communes from their postal distributions
# By: Romain Soufflet <rsoufflet@easter-eggs.com>
#
# Copyright (C) 2010 Easter-eggs
#
# This file is part of Podis.
#
# Podis is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Podis is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""Retrieve INSEE codes of french territories from their postal distributions

Podis provide an API and some scripts to manage French territories in order
to retrieve INSEE codes and their link to postal distributions.
"""


try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages


classifiers = """\
Development Status :: 5 - Production/Stable
Environment :: Console
Intended Audience :: Information Technology
License :: OSI Approved :: GNU Affero General Public License v3
Operating System :: OS Independent
Programming Language :: Python
"""

doc_lines = __doc__.split('\n')


setup(
    name = 'Podis',
    version = '2.3',

    author = 'Romain Soufflet',
    author_email = 'podis@infos-pratiques.org',
    classifiers = [classifier for classifier in classifiers.split('\n') if classifier],
    data_files = [
        ('share/doc/python-podis', ['README']),
        ],
    description = doc_lines[0],
    keywords = 'code depcom insee postal routing',
    license = 'http://www.fsf.org/licensing/licenses/agpl-3.0.html',
    long_description = '\n'.join(doc_lines[2:]),
    include_package_data = True,
    install_requires = [
        #"pymongo >= 1.8.1",
        ],
    packages = find_packages(),
    url = "http://packages.python.org/Podis/",
    zip_safe = False,
    )
