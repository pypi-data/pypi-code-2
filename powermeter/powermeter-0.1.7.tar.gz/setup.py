#!/usr/bin/env python
# encoding: utf-8

__version__ = "0.1.7"

from setuptools import setup

setup(
name = 'powermeter',
version= __version__,
author='tuxtof',
author_email='dev@geo6.net',
description='Google powermeter teleinfo daemon',
license='GPLv2',

install_requires = ['pyserial>=2.5', 'python-daemon>=1.6'],

py_modules = ['powermeter', 'google_meter', 'units', 'rfc3339'],

entry_points = {
    'console_scripts': [
        'powermeter = powermeter:main',
    ],
},

)
