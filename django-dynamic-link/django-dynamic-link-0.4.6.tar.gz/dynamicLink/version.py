#!/usr/bin/python
# -*- coding:utf-8 -*-
# This Python file uses the following encoding: utf-8

VERSION = (0,4,6)
VERSION_str = str(VERSION).strip('()').replace(',','.').replace(' ','')

VERSION_INFO = """
Version: %s
Date: 21.07.2011

Hints:
- 0.4.6 -   changes in setup.py to avoid to install the example project.
- 0.4.5 -   Small adjustments at the example project.
- 0.4.4 -   1. Because of incomplete setup.py the last distributed package
            does't contained temples and language files.
            2. Readme updated.
            3. Example project added.
- 0.4.3 -   ImportError in admin.py solved.
- 0.4.2 -   setup.py createtd. Now listed in pypi.
- 0.4.1 -   Remove small bug with links created with the action menu.

TODO:
    - write more unittests
""" % (VERSION_str,)

APPLICATION_NAME = "Dynamic Link"