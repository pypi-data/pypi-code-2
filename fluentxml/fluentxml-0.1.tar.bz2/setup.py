#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  Copyright (c) 2009, 2010, 2011 Anaël Verrier
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, version 3 only.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from distutils.core import setup

import fluentxml

description, long_description = fluentxml.__doc__.split('\n\n', 1)

setup(name='fluentxml',
      version='0.1',
      description=description,
      long_description=long_description,
      author='Anaël Verrier',
      author_email='elghinn@free.fr',
      license='GNU GPLv3',
      url='http://fluentxml.last-exile.org/',
      download_url='http://fluentxml.last-exile.org/#download',
      provides=['fluentxml'],
      keywords=['xml'],
      classifiers=(
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Text Processing :: Markup :: XML'),
      py_modules=['fluentxml'])
