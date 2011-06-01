import logging
logger = logging.getLogger('PloneHotfix20110531')

from Products.CMFCore.utils import getToolByName


def initialize(context):
    try:
        from plone.app.users.browser.account import AccountPanelSchemaAdapter
    except ImportError:
        pass
    else:
        def __init__(self, context):
            mt = getToolByName(context, 'portal_membership')
            if context.REQUEST.other.get('userid'):
                self.context = mt.getMemberById(context.REQUEST.other.get('userid'))
            elif (context.REQUEST.form.get('userid')
                  and (mt.checkPermission('Plone Site Setup: Users and Groups', context)
                  or mt.checkPermission('Manage Users', context))):
                self.context = mt.getMemberById(context.REQUEST.form.get('userid'))
            else:
                self.context = mt.getAuthenticatedMember()
        AccountPanelSchemaAdapter.__init__ = __init__
        logger.debug('Patched plone.app.users.browser.account.AccountPanelSchemaAdapter')

    try:
        from Products.PortalTransforms.transforms import safe_html
    except ImportError:
        pass
    else:
        import re
        CSS_COMMENT = re.compile(r'/\*.*\*/')
        def decode_htmlentities(s):
            """ XSS code can be hidden with htmlentities """

            entity_pattern = re.compile("&(amp;)?#(?P<htmlentity>x?\w+)?;?")
            s = entity_pattern.sub(safe_html.decode_htmlentity, s)
            return s
        def hasScript(s):
            """Dig out evil Java/VB script inside an HTML attribute.

            >>> hasScript('script:evil(1);')
            True
            >>> hasScript('expression:evil(1);')
            True
            >>> hasScript('http://foo.com/ExpressionOfInterest.doc')
            False
            """
            s = decode_htmlentities(s)
            s = s.replace('\x00', '')
            s = CSS_COMMENT.sub('', s)
            s = ''.join(s.split()).lower()
            for t in ('script:', 'expression:', 'expression(', 'data:'):
                if t in s:
                    return True
            return False
        safe_html.hasScript = hasScript
        logger.debug('Patched Products.PortalTransforms.transforms.safe_html.hasScript')
        
        from sgmllib import SGMLParser, SGMLParseError
        def parse_declaration(self, i):
            """Fix handling of CDATA sections. Code borrowed from BeautifulSoup.
            """
            j = None
            if self.rawdata[i:i+9] == '<![CDATA[':
                k = self.rawdata.find(']]>', i)
                if k == -1:
                    k = len(self.rawdata)
                data = self.rawdata[i+9:k]
                j = k+3
                self.result.append("<![CDATA[%s]]>" % data)
            else:
                try:
                    j = SGMLParser.parse_declaration(self, i)
                except SGMLParseError:
                    j = len(self.rawdata)
            return j
        safe_html.StrippingParser.parse_declaration = parse_declaration
        logger.debug('Patched Products.PortalTransforms.transforms.safe_html.StrippingParser.parse_declaration')

    from Shared.DC.Scripts.Bindings import Bindings
    from zExceptions import Forbidden
    DO_NOT_PUBLISH = [
        'selectedTabs',
        'pwreset_constructURL',
        'createMultiColumnList',
        'create_query_string',
        'getPopupScript',
        'getObjectsFromPathList',
        ]
    def _patched_bindAndExec(self, args, kw, caller_namespace):
        '''Prepares the bound information and calls _exec(), possibly
        with a namespace.
        '''
        template_id = hasattr(self, 'getId') and self.getId() or ''
        request = getattr(self, 'REQUEST', None)
        if (template_id and request and template_id in DO_NOT_PUBLISH and
            request.get('PUBLISHED') is self):
            raise Forbidden('Script may not be published.')
        return self._original_bindAndExec(args, kw, caller_namespace)
    Bindings._original_bindAndExec = Bindings._bindAndExec
    Bindings._bindAndExec = _patched_bindAndExec
    logger.debug('Patched Shared.DC.Scripts.Bindings.Bindings._bindAndExec')

    try:
        from Products.PluggableAuthService.plugins.ZODBUserManager import ZODBUserManager
    except ImportError:
        pass
    else:
        def updateUser(self, user_id, login_name):

            # The following raises a KeyError if the user_id is invalid
            old_login = self.getLoginForUserId(user_id)

            if old_login != login_name:
            
                if self._login_to_userid.get(login_name) is not None:
                    raise ValueError('Login name not available: %s' % login_name)
            
                del self._login_to_userid[old_login]
                self._login_to_userid[login_name] = user_id
                self._userid_to_login[user_id] = login_name
        ZODBUserManager.updateUser = updateUser
        logger.debug('Patched Products.PluggableAuthService.plugins.ZODBUserManager.ZODBUserManager.updateUser')

    logger.info('Hotfix installed.')
