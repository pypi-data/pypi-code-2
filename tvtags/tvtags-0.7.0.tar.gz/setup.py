#!/usr/bin/env python

__version__ = "0.7.0"

from setuptools import setup, find_packages
setup(
name = 'tvtags',
version = __version__,
author ='tuxtof',
author_email ='dev@geo6.net',
description ='Automagicly media tagger.',
url ='http://github.com/tuxtof/tvtags',
license ='GPLv2',
long_description ='tvtags use thetvdb database to automaticly tag media file.',

install_requires = ['progressbar>=2.2'],

py_modules = ['tvtags'],
packages = find_packages(),


entry_points = {
    'console_scripts': [
        'tvtags = tvtags:main',
    ],
},

)
