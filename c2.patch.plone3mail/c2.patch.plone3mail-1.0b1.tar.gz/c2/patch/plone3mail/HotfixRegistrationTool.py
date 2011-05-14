#!/usr/bin/env python
# encoding: utf-8
"""
HotfixRegistrationTool.py

Created by Manabu Terada on 2009-11-21.
Copyright (c) 2009 CMScom. All rights reserved.
"""
from email import message_from_string, MIMEText
from smtplib import SMTPRecipientsRefused
from logging import getLogger

from zope.component import getUtility
from zope.i18nmessageid import MessageFactory
from AccessControl import Unauthorized
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.utils import checkEmailAddress
from Products.CMFDefault.exceptions import EmailAddressInvalid

from Products.CMFPlone.RegistrationTool import _checkEmail
from Products.CMFPlone.RegistrationTool import RegistrationTool

from c2.patch.plone3mail import HAS_PLONE4

if HAS_PLONE4:
    from Products.CMFPlone.RegistrationTool import get_member_by_login_name

logger = getLogger(__name__)
# debug = logger.debug
info = logger.info

_ = MessageFactory('plone')

def _mailPassword(self, forgotten_userid, REQUEST):
    """ Wrapper around mailPassword """
    membership = getToolByName(self, 'portal_membership')
    if not membership.checkPermission('Mail forgotten password', self):
        raise Unauthorized(_(u"Mailing forgotten passwords has been disabled."))

    utils = getToolByName(self, 'plone_utils')
    props = getToolByName(self, 'portal_properties').site_properties
    # emaillogin = props.getProperty('use_email_as_login', False)
    if HAS_PLONE4:
        member = get_member_by_login_name(self, forgotten_userid)
    else:
        member = membership.getMemberById(forgotten_userid)

    if member is None:
        raise ValueError(_(u'The username you entered could not be found.'))

    # if emaillogin:
    #     # We use the member id as new forgotten_userid, because in
    #     # resetPassword we ask for the real member id too, instead of
    #     # the login name.
    #     forgotten_userid = member.getId()

    # assert that we can actually get an email address, otherwise
    # the template will be made with a blank To:, this is bad
    email = member.getProperty('email')
    if not email:
        raise ValueError(_(u'That user does not have an email address.'))
    else:
        # add the single email address
        if not utils.validateSingleEmailAddress(email):
            raise ValueError(_(u'The email address did not validate.'))
    check, msg = _checkEmail(email)
    if not check:
        raise ValueError(msg)

    # Rather than have the template try to use the mailhost, we will
    # render the message ourselves and send it from here (where we
    # don't need to worry about 'UseMailHost' permissions).
    reset_tool = getToolByName(self, 'portal_password_reset')
    if HAS_PLONE4:
        reset = reset_tool.requestReset(member.getId())
    else:
        reset = reset_tool.requestReset(forgotten_userid)

    encoding = getUtility(ISiteRoot).getProperty('email_charset', 'utf-8')
    mail_text = self.mail_password_template( self
                                           , REQUEST
                                           , member=member
                                           , reset=reset
                                           , password=member.getPassword()
                                           , charset=encoding
                                           )
    # The mail headers are not properly encoded we need to extract
    # them and let MailHost manage the encoding.
    if isinstance(mail_text, unicode):
        mail_text = mail_text.encode(encoding, 'replace')
    message_obj = message_from_string(mail_text)
    subject = message_obj['Subject']
    m_to = message_obj['To']
    m_from = message_obj['From']
    host = getToolByName(self, 'MailHost')
    try:
        if HAS_PLONE4:
            # host.send(message_obj, subject=subject, charset=encoding)
            host.send( mail_text, m_to, m_from, subject=subject,
                       charset=encoding)
        else:
            host.secureSend( message_obj, m_to, m_from, subject=subject,
                   charset=encoding)

        return self.mail_password_response( self, REQUEST )
    except SMTPRecipientsRefused:
        # Don't disclose email address on failure
        raise SMTPRecipientsRefused(_(u'Recipient address rejected by server.'))


def _registeredNotify(self, new_member_id):
    """ Wrapper around registeredNotify """
    membership = getToolByName( self, 'portal_membership' )
    utils = getToolByName(self, 'plone_utils')
    member = membership.getMemberById( new_member_id )

    if member and member.getProperty('email'):
        # add the single email address
        if not utils.validateSingleEmailAddress(member.getProperty('email')):
            raise ValueError(_(u'The email address did not validate.'))

    email = member.getProperty( 'email' )
    try:
        checkEmailAddress(email)
    except EmailAddressInvalid:
        raise ValueError(_(u'The email address did not validate.'))

    pwrt = getToolByName(self, 'portal_password_reset')
    reset = pwrt.requestReset(new_member_id)

    # Rather than have the template try to use the mailhost, we will
    # render the message ourselves and send it from here (where we
    # don't need to worry about 'UseMailHost' permissions).
    mail_text = self.registered_notify_template( self
                                               , self.REQUEST
                                               , member=member
                                               , reset=reset
                                               , email=email
                                               )

    encoding = getUtility(ISiteRoot).getProperty('email_charset', 'utf-8')
    # The mail headers are not properly encoded we need to extract
    # them and let MailHost manage the encoding.
    if isinstance(mail_text, unicode):
        mail_text = mail_text.encode(encoding, 'replace')
    message_obj = message_from_string(mail_text)
    subject = message_obj['Subject']
    m_to = message_obj['To']
    m_from = message_obj['From']
    host = getToolByName(self, 'MailHost')
    if HAS_PLONE4:
        # host.send(message_obj, subject=subject, charset=encoding, immediate=True)
        host.send(mail_text, m_to, m_from, subject=subject, charset=encoding, immediate=True)
    else:
        host.secureSend(message_obj, m_to, m_from, subject=subject, charset=encoding)

    return self.mail_password_response( self, self.REQUEST )


RegistrationTool.mailPassword = _mailPassword
RegistrationTool.registeredNotify = _registeredNotify
info('patched %s', str(RegistrationTool.mailPassword))
info('patched %s', str(RegistrationTool.registeredNotify))