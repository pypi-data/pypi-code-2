#!/usr/bin/env python
# encoding: utf-8
"""
addinglink.py

Created by Manabu Terada on 2011-04-22.
Copyright (c) 2011 CMScom. All rights reserved.
"""
import re
from Products.CMFCore.utils import getToolByName
from zope.component import queryUtility

from c2.app.issuelink.controlpanel.interfaces import IIssuelinkConfig
from c2.app.issuelink import IssuelinkMassage as _

# RE_ISSUE_MARK = re.compile(r'(#(\d+))', re.UNICODE)

def addinglink(obj, event):
    config = queryUtility(IIssuelinkConfig)
    if config is not None and config.use_issuelink:
        fields = ['text',]
        for field_name in fields:
            _adding_link(obj, field_name)

def _get_marks_for_html():
    config = queryUtility(IIssuelinkConfig)
    link_rules = config.link_rules
    for rule_link in link_rules:
        rule, link = rule_link.split()
        yield re.compile(r'([\s>])(%s)(?!</a>)([\s<])' % rule, re.UNICODE), link

def _get_marks_for_rest():
    config = queryUtility(IIssuelinkConfig)
    link_rules = config.link_rules
    for rule_link in link_rules:
        rule, link = rule_link.split()
        yield re.compile(r'(\s)(%s)(?!\s<https?://)([\s])' % rule, re.UNICODE), link
    
def _adding_link(obj, field_name):
    kwargs = {}
    config = queryUtility(IIssuelinkConfig)
    url = config.issuetracker_url
    if not url.endswith('/'):
        url += '/'
    data = obj.getField(field_name).getRaw(obj)
    format = 'text/html'
    if field_name == 'text':
        format = obj.text_format
    changed_to_unicode = False
    if not isinstance(data, unicode):
        data = data.decode('utf-8', 'replace')
        changed_to_unicode = True
    result = data
    is_modify_filed = False
    if format == 'text/html':
        for re_mark, link in _get_marks_for_html():
            if link.startswith('/'):
                link = link[1:]
            if not link.endswith('/'):
                link = link + '/'
            repl = r'\1<a href="%s%s\3" class="issuelink">\2</a>\4' % (url, link)
            result = re_mark.sub(repl, result)
            kwargs['mimetype'] = 'text/html'
            is_modify_filed = True
    elif format == 'text/x-rst':
        for re_mark, link in _get_marks_for_rest():
            if link.startswith('/'):
                link = link[1:]
            if not link.endswith('/'):
                link = link + '/'
            repl = r'\1`\2 <%s%s\3>`_\4' % (url, link)
            result = re_mark.sub(repl, result)
            kwargs['mimetype'] = 'text/restructured'
            is_modify_filed = True
    if not is_modify_filed:
        return field_name
    if changed_to_unicode:
        result = result.encode('utf-8', 'replace')
    kwargs['field'] = field_name
    obj.getField(field_name).set(obj, result, **kwargs)
    obj.reindexObject()
    return field_name
