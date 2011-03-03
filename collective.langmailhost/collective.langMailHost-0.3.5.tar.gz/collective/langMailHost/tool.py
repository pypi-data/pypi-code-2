import re
from email import message_from_string
from smtplib import SMTPRecipientsRefused
from zope.app.component.hooks import getSite
from Products.CMFDefault.utils import checkEmailAddress
from Products.CMFDefault.exceptions import EmailAddressInvalid
from Products.CMFCore.utils import getToolByName
from collective.langMailHost.interfaces import ILangCharset
from AccessControl import ClassSecurityInfo, Unauthorized
from Products.CMFPlone.RegistrationTool import (
    RegistrationTool,
    get_member_by_login_name
)
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('plone')

class LangRegistrationTool(RegistrationTool):

    security = ClassSecurityInfo()

    security.declarePublic('mailPassword')
    def mailPassword(self, forgotten_userid, REQUEST):
        """ Wrapper around mailPassword """
        membership = getToolByName(self, 'portal_membership')
        if not membership.checkPermission('Mail forgotten password', self):
            raise Unauthorized(_(u"Mailing forgotten passwords has been disabled."))

        utils = getToolByName(self, 'plone_utils')
        props = getToolByName(self, 'portal_properties').site_properties
        emaillogin = props.getProperty('use_email_as_login', False)
        if emaillogin:
            member = get_member_by_login_name(self, forgotten_userid)
        else:
            member = membership.getMemberById(forgotten_userid)

        if member is None:
            raise ValueError(_(u'The username you entered could not be found.'))

        if emaillogin:
            # We use the member id as new forgotten_userid, because in
            # resetPassword we ask for the real member id too, instead of
            # the login name.
            forgotten_userid = member.getId()

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
        reset = reset_tool.requestReset(forgotten_userid)


#        encoding = getUtility(ISiteRoot).getProperty('email_charset', 'utf-8')
        portal = getSite()
        encoding = ILangCharset(portal).effective_charset() or portal.getProperty('email_charset', 'UTF-8')
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
            mail_text = mail_text.encode(encoding)
        message_obj = message_from_string(mail_text)
        subject = message_obj['Subject']
        m_to = message_obj['To']
        m_from = message_obj['From']
        host = getToolByName(self, 'MailHost')
        try:
            host.send( mail_text, m_to, m_from, subject=subject,
                       charset=encoding)

            return self.mail_password_response( self, REQUEST )
        except SMTPRecipientsRefused:
            # Don't disclose email address on failure
            raise SMTPRecipientsRefused(_(u'Recipient address rejected by server.'))



    security.declarePublic('registeredNotify')
    def registeredNotify(self, new_member_id):
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

#        encoding = getUtility(ISiteRoot).getProperty('email_charset', 'utf-8')
        portal = getSite()
        encoding = ILangCharset(portal).effective_charset() or portal.getProperty('email_charset', 'UTF-8')
        # The mail headers are not properly encoded we need to extract
        # them and let MailHost manage the encoding.
        if isinstance(mail_text, unicode):
            mail_text = mail_text.encode(encoding)
        message_obj = message_from_string(mail_text)
        subject = message_obj['Subject']
        m_to = message_obj['To']
        m_from = message_obj['From']
        host = getToolByName(self, 'MailHost')
        host.send(mail_text, m_to, m_from, subject=subject, charset=encoding, immediate=True)

        return self.mail_password_response( self, self.REQUEST )

_TESTS = ( ( re.compile("^[0-9a-zA-Z\.\-\_\+\']+\@[0-9a-zA-Z\.\-]+$")
           , True
           , "Failed a"
           )
         , ( re.compile("^[^0-9a-zA-Z]|[^0-9a-zA-Z]$")
           , False
           , "Failed b"
           )
         , ( re.compile("([0-9a-zA-Z_]{1})\@.")
           , True
           , "Failed c"
           )
         , ( re.compile(".\@([0-9a-zA-Z]{1})")
           , True
           , "Failed d"
           )
         , ( re.compile(".\.\-.|.\-\..|.\.\..|.\-\-.")
           , False
           , "Failed e"
           )
         , ( re.compile(".\.\_.|.\-\_.|.\_\..|.\_\-.|.\_\_.")
           , False
           , "Failed f"
           )
         , ( re.compile(".\.([a-zA-Z]{2,3})$|.\.([a-zA-Z]{2,4})$")
           , True
           , "Failed g"
           )
         )

def _checkEmail( address ):
    for pattern, expected, message in _TESTS:
        matched = pattern.search( address ) is not None
        if matched != expected:
            return False, message
    return True, ''
