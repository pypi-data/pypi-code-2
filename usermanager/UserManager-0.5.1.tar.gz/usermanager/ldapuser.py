import ldap
from pipestack.pipe import Marble, MarblePipe
from conversionkit import Field
from stringconvert import unicodeToUnicode
import logging

log = logging.getLogger(__name__)


def listOfUsernames(split_name=False, extract_organisation=False):
    def listOfUsernames_converter(conversion, state=None):
        try:
            conversion.result = [
                v.strip() for v in conversion.value.split(',')
            ]
        except:
            conversion.error = (
                'Could not parse comma separated list of '
                'strings'
            )
    return listOfUsernames_converter

class LdapUserMarble(Marble):
    def user_has_password(self, username, password):
        if self.config.bypass_username is not None and \
           self.config.bypass_password is not None and \
           username == self.config.bypass_username:
            if password == self.config.bypass_password:
                return True
            else:
                return False
        if self.config.restrict_ldap_usernames and \
           username not in self.config.restrict_ldap_usernames:
            log.debug(
                '%r is not one of the allowed LDAP usernames', 
                username
            )
            return False
        try:
            l = ldap.open(self.config.server)
            bind_dn = self.config.bind_dn%{'user_id':username}
            log.debug(
                "Binding %s %s %s...", 
                self.config.server,
                bind_dn, 
                password,
            )
            l.simple_bind_s(bind_dn, password)
        except Exception, e:
            log.error("LDAP bind failed: %r", e)
            return False
        else:
            return True

class LdapUserPipe(MarblePipe):
    options = {
        'server': Field(
            unicodeToUnicode(), 
            missing_or_empty_error=(
                "Please enter the hostname or IP of the LDAP server in "
                "'%(name)s.server'"
            ),
        ),
        'bind_dn': Field(
            unicodeToUnicode(), 
            empty_error=(
                "Please enter the DN which should be used for binding users "
                "in the '%(name)s.bind_dn option; any strings '%%(user_id)s'"
                "in the string you enter will be replaced with the username "
                "of the user trying to sign in'",
            ),
            missing_default=False,
        ),
        'bypass_username': Field(
            unicodeToUnicode(), 
            missing_or_empty_default=None,
        ),
        'restrict_ldap_usernames': Field(
            listOfUsernames(), 
            missing_or_empty_default=None,
        ),
        'bypass_password': Field(
            unicodeToUnicode(), 
            missing_or_empty_default=None,
        ),
    }
    marble_class = LdapUserMarble

