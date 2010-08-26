#!/usr/bin/env python
# encoding: utf-8
"""
config.py

Created by Manabu Terada on 2010-08-03.
Copyright (c) 2010 CMScom. All rights reserved.
"""

PROJECTNAME = 'c2.app.shorturl'


from persistent import Persistent
from zope.interface import implements
from c2.app.shorturl.interfaces import IShortUrlConfig

class ShortUrlConfig(Persistent):
    """ utility to hold the configuration related to Short URL """
    implements(IShortUrlConfig)

    def __init__(self):
        self.base_url = u""
        self.folder_id = u""

    def getId(self):
        """ return a unique id to be used with GenericSetup """
        return 'shorturl_config'

