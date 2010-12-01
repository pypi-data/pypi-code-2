
from Acquisition import aq_inner, aq_parent, aq_base

from time import time
from plone.memoize import instance

from zope.component import ComponentLookupError
from zope.interface import implements, directlyProvides

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import IFolderish

from anthill.skinner.interfaces import IPublicSkinLayer, IRuleOverwrite

from anthill.skinner.config import VIEW_CMS_PERMISSION, \
                                        PREVIEW_MODE, \
                                            RQ_PREVIEW_VAR

from interfaces import ISkinHandler

class SkinHandling(BrowserView):
    """ @see ISkinHandler """

    implements(ISkinHandler)

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.pm = getToolByName(self.context, 'portal_membership')

        # provide folderish context
        self.folder = aq_inner(self.context)
        if not IFolderish.providedBy(self.folder):
            self.folder = aq_parent(self.folder)

    def _provideAuth(self):
        # before traversing zope hasn't yet authenticated the user
        # so we need to authenticate user here - this relies
        # on code found in BaseRequest.py(424ff) and can break in future
        # releases (but is unlikely) of Plone or Zope.
        # This code performs more or less the same steps as Zope does
        # to authenticate user so blame others for this :-)

        # first we need to find all acl_users folders
        acls = []
        for ob in self.request['PARENTS']:

            # aq-aware search
            if hasattr(ob, 'acl_users'):
                acls.append(getattr(ob, 'acl_users'))

            # also support having acl_users folder in chain
            if hasattr(aq_base(ob), 'id') and ob.id == 'acl_users':
                acls.append(ob)

        # we absolutely need at least two acl_users folder
        # one for the plone site and one for the app root
        if len(acls) >= 2:

            # hack the request to hide the fact that we don't
            # have anything published yet
            self.request['PUBLISHED'] = self.folder

            for acl in acls:
                user = acl.validate(self.request, self.request._auth)
                if user and 'Anonymous' not in user.getRoles():
                    self.request['AUTHENTICATED_USER'] = user
                    return user

            return None

        else:
            raise Exception, 'Error looking up auth validation provider!'

    def _removeAuth(self):
        # removes authentication if performed by _provideAuth
        if self.request.has_key('PUBLISHED'):
            try:
                del self.request.__dict__['other']['PUBLISHED']
                del self.request.__dict__['other']['AUTHENTICATED_USER']
            except: pass

    def _isAnonymous(self):
        isanon = self.pm.isAnonymousUser()

        # there can be cases where user seems unauthed
        # http://mail.zope.org/pipermail/zope/2001-May/090253.html
        if isanon and \
                (self.request.cookies.has_key('__ac') or \
                 hasattr(self.request, '_auth')):
                
                # try to auth user so that we can check permissions
                provided = self._provideAuth()
                if provided != None and 'Anonymous' not in provided.getRoles():
                    return False

        return isanon and True or False

    @instance.memoize
    def _checkPermission(self, permission, context):
        checkPermission = getToolByName(context, 'portal_membership').checkPermission
        return checkPermission(permission, context)

    def _hasViewCMSPermission(self): 
        if not self._isAnonymous():
            ok = self._checkPermission(VIEW_CMS_PERMISSION, self.context)

            # allow fallback to container
            if not ok and self.folder != self.context:
                ok = self._checkPermission(VIEW_CMS_PERMISSION, self.folder)
            return ok and True or False

        else: 
            return False

    def _redirectToCaller(self):
        return self.request.RESPONSE.redirect(self.folder.absolute_url())

    def mustDisplayPublicView(self):
        """ @see ISkinHandler """

        # check adapter first if available
        try:
            adapted = IRuleOverwrite(self)
            return adapted.mustDisplayPublicView(self.context, self.request)
        except (ComponentLookupError, TypeError):
            pass

        doit = self._isAnonymous() or \
                not self._hasViewCMSPermission() or \
                 self.inPreview()

        self._removeAuth()
        return doit

    def activatePreview(self):
        """ @see ISkinHandler """

        if not self.inPreview() and not self._isAnonymous():
            self.request.SESSION.set(PREVIEW_MODE, True)
            self._removeAuth()
            self._redirectToCaller()

    def deactivatePreview(self):
        """ @see ISkinHandler """

        if self.inPreview():
            self.request.SESSION.set(PREVIEW_MODE, False)
            self._removeAuth()
            self._redirectToCaller()

    def inPreview(self):
        """ @see ISkinHandler """

        if not self._isAnonymous():
            self._removeAuth()
            return self.request.SESSION.get(PREVIEW_MODE, False) or \
                    self.request.form.has_key(RQ_PREVIEW_VAR)

    def inPublicView(self):
        """ @see ISkinHandler """

        return self.mustDisplayPublicView()

    def activatePublicSkin(self):
        self.context.changeSkin('publicview', self.request)
        directlyProvides(self.request, IPublicSkinLayer)

