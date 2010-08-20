# -*- coding: utf-8 -*-

import os
from zExceptions import Unauthorized
from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
import OFS.Moniker
from OFS.CopySupport import _cb_decode
from AccessControl import ClassSecurityInfo
import AccessControl.Permissions
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.utils import shasattr
from Products.SimpleAlias.config import TOOL_ID
from Products.SimpleAlias.Permissions import ADD_ALIAS_PERMISSION
from Products.SimpleAlias import logger
from Products.SimpleAlias import SimpleAliasMessageFactory as _

_zmi = os.path.join(os.path.dirname(__file__), 'zmi')

class SimpleAliasTool(UniqueObject, SimpleItem, PropertyManager):
    """Utilities for the SimpleAlias type"""

    id = TOOL_ID
    meta_type= 'SimpleAlias tool'
    plone_tool = 1

    _properties = (
        {'id': 'title',
         'type': 'string',
         'mode': 'w'},

        {'id': 'portal_type_filters',
         'label': 'portal_type_filters: These portal types cannot be aliased',
         'type': 'multiple selection',
         'select_variable': 'potentialLinkableTypes',
         'mode': 'w'}
        )

    title = __doc__
    portal_type_filters = ()

    manage_options = (
        ({'label' : 'Overview',
          'action' : 'manage_overview'
          },)
        + PropertyManager.manage_options
        + SimpleItem.manage_options)

    security = ClassSecurityInfo()

    ##
    # ZMI
    ##

    security.declareProtected(AccessControl.Permissions.view_management_screens,
                              'manage_overview')
    manage_overview = PageTemplateFile('manage_overview', _zmi)

    security.declareProtected(AccessControl.Permissions.view_management_screens,
                              'potentialLinkableTypes')
    def potentialLinkableTypes(self):
        """Vocabulary for portal_type_filters property"""

        portal_types = getToolByName(self, 'portal_types')
        return portal_types.listContentTypes()


    security.declarePublic('getLinkableTypes')
    def getLinkableTypes(self, content=None):
        exclude = self.getProperty('portal_type_filters', [])
        portal_types = getToolByName(self, 'portal_types')
        return tuple([t for t in portal_types.listContentTypes() if t not in exclude])


    security.declarePublic('manage_pasteAsAlias')
    def manage_pasteAsAlias(self, context, cb_copy_data=None):

        # first check if the user has the proper permissions in the 'context'
        portal_membership = getToolByName(self, 'portal_membership')
        if not portal_membership.checkPermission(ADD_ALIAS_PERMISSION, context):
            msg = "Insufficient priviledge to perform this action. It requires the permission: " + ADD_ALIAS_PERMISSION
            raise Unauthorized(msg, needed={'permission': ADD_ALIAS_PERMISSION})

        cp = None
        REQUEST = context.REQUEST

        if cb_copy_data is not None:
            cp = cb_copy_data
        elif REQUEST and REQUEST.has_key('__cp'):
            cp = REQUEST['__cp']
        else:
            cp = None

        if cp is None:
            raise ValueError("No clipboard data")

        try:
            cp = _cb_decode(cp)
        except:
            raise ValueError("can't decode clipboard: %r" % cp)

        oblist = []
        app = self.getPhysicalRoot()
        failed = ''
        success = ''
        types = self.getLinkableTypes()

        for mdata in cp[1]:
            m = OFS.Moniker.loadMoniker(mdata)
            try:
                ob = m.bind(app)
            except:
                raise ValueError("Objects not found in %s" % app)
            oblist.append(ob)

        for ob in oblist:
            if shasattr(ob, 'isReferenceable') and ob.portal_type in types:
                # create an Alias for this object
                id = context.generateUniqueId('Alias')
                new_id = context.invokeFactory(id=id, type_name='Alias')
                if new_id is None or new_id == '':
                    new_id = id
                o = getattr(context, new_id, None)
                # now set the reference
                o.setAlias(ob.UID())
                oid = o._renameAfterCreation()
                logger.debug("New alias created: %s", str(oid))
                o.reindexObject()
                o = None
                success = _('Alias(es) created.')
            else:
                if failed == '':
                    failed = _('Ignored (not linkable): ') + ob.Title()
                else:
                    failed = failed + u', ' + ob.Title()

        return success + failed


    def getAliasIcon(self, content):
        objIcon = content.getIcon(relative_to_portal=1)
        aliasIcon = objIcon.replace('.gif', '_alias.gif')

        # check if it exists
        if getattr(self.portal_skins.aq_explicit, aliasIcon, None):
            return aliasIcon
        else:
            return 'alias_icon.gif'


InitializeClass(SimpleAliasTool)
