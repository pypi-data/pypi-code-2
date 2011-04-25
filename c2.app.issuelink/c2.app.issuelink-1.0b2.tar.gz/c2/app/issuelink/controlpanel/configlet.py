#!/usr/bin/env python
# encoding: utf-8
"""
configlet.py

Created by Manabu Terada on 2011-04-22.
Copyright (c) 2011 CMScom. All rights reserved.
"""
from zope.component import adapts, queryUtility
from zope.formlib.form import FormFields
from zope.interface import implements
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from plone.app.controlpanel.form import ControlPanelForm

from c2.app.issuelink.controlpanel.interfaces import IIssuelinkSchema
from c2.app.issuelink.controlpanel.interfaces import IIssuelinkConfig
from c2.app.issuelink import IssuelinkMassage as _


class IssuelinkControlPanelAdapter(SchemaAdapterBase):
    adapts(IPloneSiteRoot)
    implements(IIssuelinkSchema)

    def getUseIssuelink(self):
        util = queryUtility(IIssuelinkConfig)
        return getattr(util, 'use_issuelink', False)

    def setUseIssuelink(self, value):
        util = queryUtility(IIssuelinkConfig)
        if util is not None:
            util.use_issuelink = value

    use_issuelink = property(getUseIssuelink, setUseIssuelink)

    def getIssuetrackerUrl(self):
        util = queryUtility(IIssuelinkConfig)
        return getattr(util, 'issuetracker_url', "")

    def setIssuetrackerUrl(self, value):
        util = queryUtility(IIssuelinkConfig)
        if util is not None:
            util.issuetracker_url = value

    issuetracker_url = property(getIssuetrackerUrl, setIssuetrackerUrl)
    
    def getLinkRules(self):
        util = queryUtility(IIssuelinkConfig)
        return getattr(util, 'link_rules', [])
        
    def setLinkRules(self, value):
        util = queryUtility(IIssuelinkConfig)
        if util is not None:
            li = []
            for link_rule in value:
                if len(link_rule.split()) == 2:
                    li.append(link_rule)
            util.link_rules = li
    
    link_rules = property(getLinkRules, setLinkRules)

class IssuelinkControlPanel(ControlPanelForm):
    
    form_fields = FormFields(IIssuelinkSchema)

    label = _('Issuelink settings')
    description = _('Settings to enable and configure queued Issuelink.')
    form_name = _('Issuelink settings')

