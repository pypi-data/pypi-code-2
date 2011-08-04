#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
import os
from progbar import ProgBar

setup(name='progbar',
    version='0.1',
    author='Yves-Gwenael Bourhis',
    author_email='ybourhis at mandriva.com',
    description = 'simple progression bar for shell scripts',
    license = 'GNU General Public License version 2.0',
    platforms = ['Windows','Linux','Mac OS',],
    long_description = ProgBar.__doc__,
    py_modules = ['progbar']
)
