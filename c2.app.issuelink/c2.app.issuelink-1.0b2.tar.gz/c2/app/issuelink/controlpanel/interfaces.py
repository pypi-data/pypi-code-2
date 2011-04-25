#!/usr/bin/env python
# encoding: utf-8
"""
interfaces.py

Created by Manabu Terada on 2011-04-22.
Copyright (c) 2011 CMScom. All rights reserved.
"""
from zope.interface import Interface
from zope.schema import Bool, TextLine, URI, List

from c2.app.issuelink import IssuelinkMassage as _

class IIssuelinkSchema(Interface):
    
    use_issuelink = Bool(title=_(u'use_issuelink'), 
            description=_(u'use_issuelink_help'))
    
    issuetracker_url = TextLine(title=_(u'issuetracker_url'), 
            description=_(u'issuetracker_url_help'),
            required=False,
            )
    link_rules = List(title=_(u'link_rules'), default=[],
            description=_(u'link_rules_help'),
            value_type=TextLine(title=u'rule and path'),
            required=False)


class IIssuelinkConfig(IIssuelinkSchema):
    """ utility to hold the configuration """
