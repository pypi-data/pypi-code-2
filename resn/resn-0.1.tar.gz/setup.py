#!/usr/bin/env python
# Copyright (c) 2007 Qtrac Ltd. All rights reserved.
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

import os

from setuptools import setup

setup(name='resn',
      version = '0.1',
      author="Vivek.Narayanan",
      author_email="mail@vivekn.co.cc",
      url="http://github.com/vivekn/resn",
      classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      packages=['resn'],
      platforms=["Any"],
      license="BSD",
      keywords='redis, social network',
      description="resn (REdis Social Network) is a simple library to create social networks. It provides a backend for data models using Redis, supporting friends, followers, updates and a news feed out of the box.",
      long_description="""\
resn
====
resn (REdis Social Network) is a simple library to create social networks. It provides a backend for data models using Redis, supporting friends, followers, updates and a news feed out of the box. You can use it with any web framework like Django, Flask, Pylons etc. For examples see the file **tests.py**. 

Requires:

* Latest version of [redis-py](http://github.com/andymccurdy/redis-py)
* Latest version of [redis_wrap](http://github.com/amix/redis_wrap)

Author: Vivek Narayanan <mail@vivekn.co.cc> 

License: BSD, see LICENSE for more info.

Installation
============
First install redis_py and redis_wrap if you haven't already:

    $ easy_install redis
    $ easy_install resis_wrap

Then install resn:

    $ easy_install resn


Setting up
==========
To use resn, import the module resn and add this to the beginning of the file.
    
    from resn import *
    setup_system('default', host, port) # host and port of your redis server, default is localhost:6379

There are a couple of other settings you might want to change.
    
    resn_settings['Feed Size'] = 100 # default value = 1000,  No of messages in a user's feed.
    resn_settings['Token Validity'] = 72 * 3600 # This is the default value in seconds

Examples
==========

For examples see https://github.com/vivekn/resn/blob/master/tests.py

Future
======
Support for integrating with Facebook and Twitter APIs is planned.""")
