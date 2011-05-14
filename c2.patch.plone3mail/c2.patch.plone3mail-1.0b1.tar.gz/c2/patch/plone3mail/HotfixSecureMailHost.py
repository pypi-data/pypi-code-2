#!/usr/bin/env python
# encoding: utf-8
"""
HotfixSecureMailHost.py

Created by Manabu Terada on 2009-05-24.
Copyright (c) 2009 CMScom. All rights reserved.
"""
from Products.SecureMailHost.config import BAD_HEADERS
from copy import deepcopy

import email.Message
import email.Header
import email.MIMEText
import email
from email.Utils import getaddresses
from email.Utils import formataddr

from AccessControl.Permissions import use_mailhost_services
from Globals import Persistent, DTMLFile, InitializeClass
from Products.CMFCore.utils import getToolByName
from Products.MailHost.MailHost import MailHostError

from Products.SecureMailHost.SecureMailHost import encodeHeaderAddress
from Products.SecureMailHost.SecureMailHost import SecureMailHost

from logging import getLogger
logger = getLogger(__name__)
# debug = logger.debug
info = logger.info

def _to_unicode_to_str(s, old_chr, new_chr):
    if s is None:
        return s
    if isinstance(s, unicode):
        return s.encode(new_chr, 'replace')
    else:
        return s.decode(old_chr).encode(new_chr, 'replace')

def _secureSend(self, message, mto, mfrom, subject='[No Subject]',
               mcc=None, mbcc=None, subtype='plain', charset='us-ascii',
               debug=False, **kwargs):
    """A more secure way to send a message

    message:
        The plain message text without any headers or an
        email.Message.Message based instance
    mto:
        To: field (string or list)
    mfrom:
        From: field
    subject:
        Message subject (default: [No Subject])
    mcc:
        Cc: (carbon copy) field (string or list)
    mbcc:
        Bcc: (blind carbon copy) field (string or list)
    subtype:
        Content subtype of the email e.g. 'plain' for text/plain (ignored
        if message is a email.Message.Message instance)
    charset:
        Charset used for the email, subject and email addresses
    kwargs:
        Additional headers
    """
    portal_prop = getToolByName(self, 'portal_properties')
    site_charset = portal_prop.site_properties.getProperty('default_charset', 'utf-8')
    mto  = self.emailListToString(_to_unicode_to_str(mto, site_charset, charset))
    mcc  = self.emailListToString(_to_unicode_to_str(mcc, site_charset, charset))
    mbcc = self.emailListToString(_to_unicode_to_str(mbcc, site_charset, charset))
    # validate email addresses
    # XXX check Return-Path
    for addr in mto, mcc, mbcc:
        if addr:
            result = self.validateEmailAddresses(addr)
            if not result:
                raise MailHostError, 'Invalid email address: %s' % addr
    result = self.validateSingleEmailAddress(mfrom)
    if not result:
        raise MailHostError, 'Invalid email address: %s' % mfrom

    # create message
    if isinstance(message, email.Message.Message):
        # got an email message. Make a deepcopy because we don't want to
        # change the message
        msg = deepcopy(message)
    else:
        if isinstance(message, unicode):
            message = message.encode(charset, 'replace')
        else:
            message = message.decode(site_charset).encode(charset, 'replace')
        msg = email.MIMEText.MIMEText(message, subtype, charset)
    
    mfrom = encodeHeaderAddress(mfrom, charset)
    mto = encodeHeaderAddress(mto, charset)
    mcc = encodeHeaderAddress(mcc, charset)
    mbcc = encodeHeaderAddress(mbcc, charset)

    # set important headers
    subject = _to_unicode_to_str(subject, site_charset, charset)
    self.setHeaderOf(msg, skipEmpty=True, From=mfrom, To=mto,
             Subject=str(email.Header.Header(subject, charset)),
             Cc=mcc, Bcc=mbcc)

    for bad in BAD_HEADERS:
        if bad in kwargs:
            raise MailHostError, 'Header %s is forbidden' % bad
    self.setHeaderOf(msg, **kwargs)

    # we have to pass *all* recipient email addresses to the
    # send method because the smtp server doesn't add CC and BCC to
    # the list of recipients
    to = msg.get_all('to', [])
    cc = msg.get_all('cc', [])
    bcc = msg.get_all('bcc', [])
    #resent_tos = msg.get_all('resent-to', [])
    #resent_ccs = msg.get_all('resent-cc', [])
    recipient_list = getaddresses(to + cc + bcc)
    all_recipients = [formataddr(pair) for pair in recipient_list]

    # finally send email
    return self._send(mfrom, all_recipients, msg, debug=debug)

SecureMailHost.secureSend = _secureSend
info('patched %s', str(SecureMailHost.secureSend))