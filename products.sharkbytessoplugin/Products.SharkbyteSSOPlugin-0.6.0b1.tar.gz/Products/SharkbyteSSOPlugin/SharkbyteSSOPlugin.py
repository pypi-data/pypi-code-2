""" SharkbyteSSOPlugin
Copyright(C), 2006, Sharkbyte Studios Ltd

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

from AccessControl import ClassSecurityInfo

from Globals import InitializeClass
from OFS.Cache import Cacheable

from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from zope.interface import classImplements
from zope.interface import implementedBy
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin
from Products.PluggableAuthService.interfaces.plugins import IChallengePlugin
from Products.PluggableAuthService.interfaces.plugins import IExtractionPlugin

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

def manage_addSharkbyteSSOPlugin(dispatcher, id='sbs_sso', title=None, REQUEST=None):
    """ Add a SharkbyteSSOPlugin to a Pluggable Auth Service. """

    obj = SharkbyteSSOPlugin(id, title)
    dispatcher._setObject(obj.getId(), obj)

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(
                                '%s/manage_workspace'
                                '?manage_tabs_message='
                                'SharkbyteSSOPlugin+added.'
                            % dispatcher.absolute_url())

class SharkbyteSSOPlugin(BasePlugin, Cacheable):
    """PAS plugin for using SSO credentials to log in.
    """

    uservar = 'X_REMOTE_USER'
    meta_type = 'SharkbyteSSOPlugin'
    protocol = 'http'
    auth_scheme = 'NTLM'

    security = ClassSecurityInfo()

    _properties = ({'id':'uservar','type':'string'},)

    def __init__(self, id, title=None):
        self._id = self.id = id
        self.title = title
        return

    security.declarePrivate('authenticateCredentials')
    def authenticateCredentials(self, credentials):
        """Authentication Part
        """
        userid = credentials.get('user_id')

        # Check if user exists
        user = self.getUserById(userid)
        if user is not None:
            return userid, userid
        else:
            LOG.info('Unauthorized user, ID : ' + userid)
        return None

    security.declarePrivate('extractCredentials')
    def extractCredentials(self, request):
        """Extraction Part
        """
        creds = {}
        userid = request.environ.get(self.uservar, '')
        if userid:
            # User id may be "<domain>\\<userid>" or "<userid>"
            creds.update({'user_id': userid.split('\\')[-1]})
        return creds

    security.declarePrivate('challenge')
    def challenge(self, request, response):
        """Assert via the response that credentials will be gathered.
        We don't need to make a real challenge as it is done by IIS
        """
        response.addHeader('WWW-Authenticate', self.auth_scheme)
        userid = request.environ.get(self.uservar, '')
        if not userid:
            response.setStatus(401)
        return

classImplements(SharkbyteSSOPlugin,
                IAuthenticationPlugin,
                IExtractionPlugin,
                IChallengePlugin,
                *implementedBy(BasePlugin))

InitializeClass(SharkbyteSSOPlugin)
