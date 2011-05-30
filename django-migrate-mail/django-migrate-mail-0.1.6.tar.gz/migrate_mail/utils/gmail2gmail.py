#!/usr/bin/env python

from gdata.apps.migration import service
from gdata.service import CaptchaRequired, BadAuthentication
from ProcImap.ImapServer import ImapServer
from imaplib import IMAP4

class CaptchaError(Exception):
    def __init__(self, token, url):
        self.token = token
        self.url = url

class ServerError(Exception):
    pass

class AuthenticationError(Exception):
    pass

def domainize(username, domain):
    if not username.endswith(domain) and '@' not in username:
        username += '@' + domain
    return username

def get_server(from_email, from_password):
    try:
        server = ImapServer(
            servername='imap.gmail.com', # FIXME: unhardcode
            username=from_email,
            password=from_password
        )
    except IMAP4.error, e:
        raise ServerError(unicode(e))
    return server

def build_migration_service(domain, admin_email, admin_password, captcha_token=None, captcha=None, auth_token=None):
    admin_email = domainize(admin_email, domain)
    migration_service = service.MigrationService(
        email=admin_email, 
        password=admin_password,
        domain=domain, 
        source="Machiavelli-Gmail2Gmail-v1")
    if auth_token:
        migration_service.SetClientLoginToken(auth_token)
    else:
        try:
            migration_service.ProgrammaticLogin(captcha_token, captcha)
        except CaptchaRequired, e:
            raise CaptchaError(migration_service.captcha_token, migration_service.captcha_url)
        except BadAuthentication, e:
            raise AuthenticationError(e)
    return migration_service
