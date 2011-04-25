#!/usr/bin/env python
# encoding: utf-8
"""
config.py

Created by Manabu Terada on 2011-04-22.
Copyright (c) 2011 CMScom. All rights reserved.
"""
from persistent import Persistent
from zope.interface import implements
from c2.app.issuelink.controlpanel.interfaces import IIssuelinkConfig


class IssuelinkConfig(Persistent):
    """ utility to hold the configuration related to Accessiblity """
    implements(IIssuelinkConfig)

    def __init__(self):
        self.use_issuelink = False
        self.issuetracker_url = ""
        self.link_rules = []

    def getId(self):
        """ return a unique id to be used with GenericSetup """
        return 'issuelink_config'

