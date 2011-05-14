#!/usr/bin/env python
# encoding: utf-8
"""
HotfixPasswordResetTool.py

Created by Manabu TERADA on 2011-04-24.
Copyright (c) 2011 CMScom. All rights reserved.
"""
from email.Header import Header
from email.charset import Charset, add_charset
from Acquisition import aq_inner
from zope.component import getUtility
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFPlone.utils import getSiteEncoding, safe_unicode

from Products.PasswordResetTool.browser import PasswordResetToolView


def _encode_mail_header(self, text):
    """ Encodes text into correctly encoded email header """
    context = aq_inner(self.context)
    site_encoding = getSiteEncoding(context)
    encoding = getUtility(ISiteRoot).getProperty('email_charset', 'utf-8')
    return Header(safe_unicode(text, site_encoding), encoding)

def _encoded_mail_sender(self):
    """ returns encoded version of Portal name <portal_email> """
    portal = self.portal_state().portal()
    from_ = portal.getProperty('email_from_name')
    mail  = portal.getProperty('email_from_address')
    return '"%s" <%s>' % (self.encode_mail_header(from_).encode(), mail)

PasswordResetToolView.encode_mail_header = _encode_mail_header
PasswordResetToolView.encoded_mail_sender = _encoded_mail_sender