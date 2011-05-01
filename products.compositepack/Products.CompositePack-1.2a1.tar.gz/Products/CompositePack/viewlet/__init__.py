##############################################################################
#
# Copyright (c) 2004-2006 CompositePack Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""CompositePack Viewlet :
   placeholder for a method found by acquisition
   this method is used to display a composite element.


$Id: __init__.py 238392 2011-05-01 03:46:07Z hathawsh $
"""
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import copy_or_move as permission_copy_or_move
from OFS.ObjectManager import BeforeDeleteException
from OFS import PropertyManager
from OFS.SimpleItem import Item

from Products.Archetypes.public import *
from Products.Archetypes.utils import insert_zmi_tab_before

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ManagePortal

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CompositePack.viewlet.interfaces import IViewlet
from Products.CompositePack.viewlet.interfaces import ILayout
from Products.CompositePack.config import PROJECTNAME, TOOL_ID
from Products.CompositePack.config import zmi_dir
from Products.CompositePack.exceptions import CompositePackError
from md5 import md5
from zope.interface import implements


base_schema = Schema((

    StringField(
        name='id',
        required=1,
        mode='rw',
        permission=permission_copy_or_move,
        accessor='getId',
        mutator='setId',
        default='',
        widget=RequiredIdWidget(
            ignore_visible_ids=True,  # Always show the widget
        ),
    ),

    StringField(
        name='title',
        required=1,
        searchable=1,
        default='',
        accessor='Title',
        widget=StringWidget(
            label_msgid='label_title',
            visible={'view' : 'invisible'},
            i18n_domain='plone',
        ),
    ),

    ), marshall = RFC822Marshaller())


class SkinMethod(BaseContentMixin):

    meta_type = portal_type = archetype_name = 'CompositePack Skin Method'
    global_allow = 0

    schema = base_schema + Schema((
        StringField(
        'skin_method',
        accessor='getSkinMethod',
        mutator='setSkinMethod',
        widget=StringWidget(label='Skin Method',
                            description=('Method called for rendering '
                                         'the viewlet/layout.'))
        ),
        ))

    def getId(self):
        if getattr(self, '_at_is_fake_instance', False):
            return ''
        return super(SkinMethod, self).getId()

    def getTemplate(self):
        """ Return the template """
        purl = getToolByName(self, 'portal_url')
        portal = purl.getPortalObject()
        return portal.restrictedTraverse(self.getSkinMethod())

    def indexObject(self):
        '''skin method is never catalogued'''
        pass

    def reindexObject(self, idxs=[]):
        '''skin method is never catalogued'''
        pass

    def unindexObject(self):
        '''skin method is never catalogued'''
        pass


class Viewlet(SkinMethod, PropertyManager.PropertyManager):
    implements(IViewlet)

    _properties=({'id':'title', 'type': 'string','mode':'wd'},)

    security = ClassSecurityInfo()

    meta_type = portal_type = archetype_name = 'CompositePack Viewlet'

    factory_type_information={
            'content_icon':'composite.gif',
            }

    _manage_registerTypes = PageTemplateFile('registerViewlet.pt',
        zmi_dir)

    manage_options = insert_zmi_tab_before('Dublin Core',
                                   {'label':'Composables',
                                    'action':'manage_registerTypes'},
                                   BaseContent.manage_options)

    security.declareProtected( ManagePortal, 'manage_registerTypes' )
    def manage_registerTypes(self, REQUEST, manage_tabs_message=None):
        '''
        manage registered types for viewlet
        '''
        reg_types_info = list()
        unreg_types_info = list()
        ct = getToolByName(self, TOOL_ID)
        for type in ct.getRegisteredComposables():
            type_info = {}
            type_info['title'] = type
            type_info['default'] = self.isDefaultForType(type)
            type_info['nodefault'] = ct.noDefaultViewletForType(type)
            if self.isRegisteredForType(type) and not ct.getTypeUseDefaultSetup(type):
                reg_types_info.append(type_info)
            else:
                unreg_types_info.append(type_info)
        return self._manage_registerTypes(REQUEST,
                                          reg_types_info=reg_types_info,
                                          unreg_types_info=unreg_types_info)

    security.declareProtected( ManagePortal, 'manage_addComposables' )
    def manage_addComposables(self, REQUEST, manage_tabs_message=None, types=None):
        '''
        register composables for viewlet
        '''
        if types is None:
           types = []
        self.registerForTypes(types)
        return self.REQUEST.RESPONSE.redirect('manage_registerTypes')

    security.declareProtected( ManagePortal, 'manage_unregisterComposable' )
    def manage_unregisterComposable(self, REQUEST, manage_tabs_message=None, type=None):
        '''
        unregister composable for viewlet
        '''
        if type is not None:
            self.unregisterForType(type)
        return self.REQUEST.RESPONSE.redirect('manage_registerTypes')

    security.declareProtected( ManagePortal, 'manage_defaultViewlets' )
    def manage_defaultViewlets(self, REQUEST, manage_tabs_message=None, types=[]):
        '''
        associate viewlet as default viewlet
        '''
        for type in types:
            setting = REQUEST.get(type, None)
            if setting is not None:
                self.setDefaultForType(type)
            else:
                if self.isDefaultForType(type):
                    self.clearDefaultForType(type)
        #return self.manage_registerTypes(REQUEST)
        return self.REQUEST.RESPONSE.redirect('manage_registerTypes')

    def registerForTypes(self, list):
        for type in list:
            self.registerForType(type)

    def registerForDefaultSetup(self):
        ct = getToolByName(self, TOOL_ID)
        ct.registerViewletForDefaultSetup(self)

    def unregisterForDefaultSetup(self, force=False):
        ct = getToolByName(self, TOOL_ID)
        ct.unregisterViewletForDefaultSetup(self, force)

    def setDefaultForDefaultSetup(self):
        ct = getToolByName(self, TOOL_ID)
        ct.setDefaultViewletForDefaultSetup(self)

    def clearDefaultForDefaultSetup(self):
        ct = getToolByName(self, TOOL_ID)
        ct.clearDefaultViewletForDefaultSetup()

    def isRegisteredForDefaultSetup(self):
        ct = getToolByName(self, TOOL_ID)
        return self in ct.getRegisteredViewletsForDefaultSetup()

    def isDefaultForDefaultSetup(self):
        ct = getToolByName(self, TOOL_ID)
        try:
            return self == ct.getDefaultViewletForDefaultSetup()
        except CompositePackError:
            return False

    def registerForType(self, type):
        ct = getToolByName(self, TOOL_ID)
        ct.registerViewletForType(self, type)

    def unregisterForType(self, type, force=False):
        ct = getToolByName(self, TOOL_ID)
        ct.unregisterViewletForType(self, type, force)

    def setDefaultForType(self, type):
        ct = getToolByName(self, TOOL_ID)
        ct.setDefaultViewletForType(self, type)

    def clearDefaultForType(self, type):
        ct = getToolByName(self, TOOL_ID)
        ct.clearDefaultViewletForType(type)

    def isRegisteredForType(self, type):
        ct = getToolByName(self, TOOL_ID)
        return self in ct.getRegisteredViewletsForType(type)

    def isDefaultForType(self, type):
        ct = getToolByName(self, TOOL_ID)
        try:
            return self == ct.getDefaultViewletForType(type)
        except CompositePackError:
            return False

    def setStableUID(self):
        """Set a UID generated from the viewlet's path
        """
        path = []
        ct = getToolByName(self, TOOL_ID)

        obj = self
        while obj != ct:
            path.append(obj.getId())
            obj = obj.aq_parent
        path.append(obj.getId())

        uid = md5(self.meta_type + ' ' + '/'.join(path)).hexdigest()
        if uid != self.UID():
            # XXX Archetypes bug: _setUID sometimes randomises UID unless we clear
            # the copy flag
            self._v_is_cp = None
            self._setUID(uid)

    def manage_afterAdd(self, item, container):
        SkinMethod.manage_afterAdd(self, item, container)
        self.setStableUID()

    def manage_afterClone(self, item):
        SkinMethod.manage_afterClone(self, item)
        self.setStableUID()


class Layout(SkinMethod):
    implements(ILayout)

    security = ClassSecurityInfo()

    meta_type = portal_type = archetype_name = 'CompositePack Layout'

    factory_type_information={
            'content_icon':'composite.gif',
            }

    _manage_registerTypes = PageTemplateFile('registerLayout.pt',
        zmi_dir)

    manage_options = insert_zmi_tab_before('Dublin Core',
                                   {'label':'Composites',
                                    'action':'manage_registerTypes'},
                                   BaseContent.manage_options)

    security.declareProtected( ManagePortal, 'manage_registerTypes' )
    def manage_registerTypes(self, REQUEST, manage_tabs_message=None):
        '''
        manage registered composites for layout
        '''
        reg_types_info = list()
        unreg_types_info = list()
        ct = getToolByName(self, TOOL_ID)
        for type in ct.getRegisteredComposites():
            type_info = {}
            type_info['title'] = type
            type_info['default'] = self.isDefaultForType(type)
            type_info['nodefault'] = ct.noDefaultLayoutForType(type)
            if self.isRegisteredForType(type):
                reg_types_info.append(type_info)
            else:
                unreg_types_info.append(type_info)
        return self._manage_registerTypes(REQUEST,
                                          reg_types_info=reg_types_info,
                                          unreg_types_info=unreg_types_info)

    security.declareProtected( ManagePortal, 'manage_addComposites' )
    def manage_addComposites(self, REQUEST, manage_tabs_message=None, types=None):
        '''
        register composites for layout
        '''
        if types is None:
           types = []
        self.registerForTypes(types)
        return self.REQUEST.RESPONSE.redirect('manage_registerTypes')

    security.declareProtected( ManagePortal, 'manage_unregisterComposite' )
    def manage_unregisterComposite(self, REQUEST, manage_tabs_message=None, type=None):
        '''
        unregister composite for layout
        '''
        if type is not None:
            self.unregisterForType(type)
        return self.REQUEST.RESPONSE.redirect('manage_registerTypes')

    security.declareProtected( ManagePortal, 'manage_defaultLayouts' )
    def manage_defaultLayouts(self, REQUEST, manage_tabs_message=None, types=[]):
        '''
        associate layout as default layout
        '''
        for type in types:
            setting = REQUEST.get(type, None)
            if setting is not None:
                self.setDefaultForType(type)
            else:
                if self.isDefaultForType(type):
                    self.clearDefaultForType(type)
        #return self.manage_registerTypes(REQUEST)
        return self.REQUEST.RESPONSE.redirect('manage_registerTypes')

    def registerForType(self, type):
        ct = getToolByName(self, TOOL_ID)
        ct.registerLayoutForType(self, type)

    def registerForTypes(self, list):
        for type in list:
            self.registerForType(type)

    def unregisterForType(self, type, force=False):
        ct = getToolByName(self, TOOL_ID)
        ct.unregisterLayoutForType(self, type, force)

    def setDefaultForType(self, type):
        ct = getToolByName(self, TOOL_ID)
        ct.setDefaultLayoutForType(self, type)

    def clearDefaultForType(self, type):
        ct = getToolByName(self, TOOL_ID)
        ct.clearDefaultLayoutForType(type)

    def isRegisteredForType(self, type):
        ct = getToolByName(self, TOOL_ID)
        return self in ct.getRegisteredLayoutsForType(type)

    def isDefaultForType(self, type):
        ct = getToolByName(self, TOOL_ID)
        try:
            return self == ct.getDefaultLayoutForType(type)
        except CompositePackError:
            return False

# Prevents from deleting the tool and doesn't call's the base class
# manage_beforeDelete!
#     security.declarePrivate('manage_beforeDelete')
#     def manage_beforeDelete(self, item, container):
#         ct = getToolByName(self, TOOL_ID)
#         if ct.getDefaultLayout() == self.getId():
#             raise BeforeDeleteException, 'cannot unregister default layout'


registerType(SkinMethod, PROJECTNAME)
registerType(Viewlet, PROJECTNAME)
registerType(Layout, PROJECTNAME)
