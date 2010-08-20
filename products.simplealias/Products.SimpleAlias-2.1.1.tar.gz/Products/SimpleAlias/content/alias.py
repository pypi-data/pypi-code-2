# -*- coding: utf-8 -*-

from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import INonStructuralFolder
from Products.Archetypes.atapi import registerType
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import BooleanField
from Products.Archetypes.atapi import ReferenceField
from Products.Archetypes.atapi import BooleanWidget
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import StringWidget
from Products.Archetypes.atapi import TextAreaWidget
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.content.document import finalizeATCTSchema
from Products.SimpleAlias.config import TOOL_ID
from Products.CMFDynamicViewFTI.interface import ISelectableBrowserDefault
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget


schema = ATCTContent.schema.copy() +  Schema((
    StringField('title',
                required=False,
                searchable=True,
                default='Link not set',
                accessor='Title',
                widget=StringWidget(
                    visible={'view' : 'visible', 'edit':'visible'})),
    StringField('description',
                searchable=True,
                accessor='Description',
                widget=TextAreaWidget(
                    visible={'view' : 'visible', 'edit':'visible'})),
    ReferenceField('alias',
                   edit_accessor="getAliasUID",
                   multiValued=False,
                   relationship='linksTo',
                   allowed_types_method='getTypes',
                   vocabulary_display_path_bound=0,
                   widget=ReferenceBrowserWidget(
                       size=80,
                       checkbox_bound=True,
                       populate=True,
                       label='Target object',
                       description='Select the target object this alias links '
                                   'to. <br/> <b>Note:</b> if a user may view '
                                   'this Alias then he can always see the '
                                   'title and description of this target '
                                   'object. <br />Even when he has no view '
                                   'permissions for this target object. Beware '
                                   'if you want this.',
                       label_msgid="label_alias",
                       description_msgid="desc_alias",
                       force_close_on_insert=1,
                       i18n_domain="simplealias"),
                   ),
    BooleanField('autoTitle',
                 default=1,
                 widget=BooleanWidget(
                     label='Auto title',
                     description="Check if you want to auto set title and "
                                 "description of alias with title and "
                                 "description of targeted object. Uncheck if "
                                 "you want specify another title and "
                                 "description for the alias.",
                     label_msgid="label_auto_title",
                     description_msgid="desc_auto_title",
                     i18n_domain="simplealias")),
    BooleanField('showTarget',
                 default=1,
                 widget=BooleanWidget(
                     label='Show target',
                     description="Check if you want to include the target "
                                 "object's content while viewing this alias. "
                                 "Uncheck will only show the title and "
                                 "description.",
                     label_msgid="label_show_target",
                     description_msgid="desc_show_target",
                     i18n_domain="simplealias")),
    BooleanField('showHint',
                 default=False,
                 widget=BooleanWidget(
                     label='Show alias hint',
                     description="Check if you want to include text 'This is "
                                 "an alias for ....' above the rendered target "
                                 "object.",
                     label_msgid="label_show_hint",
                     description_msgid="desc_show_hint",
                     i18n_domain="simplealias")),
))

finalizeATCTSchema(schema)

class Alias(ATCTContent):
    """
An Alias is a link to another object in the portal.
    """

    schema = schema

    meta_type = "Alias"

    _at_rename_after_creation = True
    removed = 0

    def getTypes(self, object=None):
        simplealias_tool = getToolByName(self, TOOL_ID)
        return simplealias_tool.getLinkableTypes(object)


    def Title(self):
        if self.getAutoTitle():
            refObject = self.getAlias()

            if refObject is None:
                if self.getAliasUID():
                    return 'Removed: '+self.getField('title').get(self)
                else:
                    return 'Alias not set'
            try:
                return refObject.title_or_id()
            except AttributeError:
                return refObject.Title()

        return self.getField('title').get(self)


    def Description(self):
        if self.getAutoTitle():
            refObject = self.getAlias()

            if refObject is None:
                return 'Object is removed or deleted.'

            return refObject.Description()

        return self.getField('description').get(self)


    def getIcon(self, relative_to_portal=0):
        refObject = self.getAlias()
        if refObject is not None:
            simplealias_tool = getToolByName(self, TOOL_ID)
            return simplealias_tool.getAliasIcon(refObject)
        else:
            return 'alias_icon.gif'


    def getIsPrincipiaFolderish(self):
        refObject = self.getAlias()
        if refObject is not None:
            return (refObject.isPrincipiaFolderish
                    and not INonStructuralFolder.providedBy(refObject))
        else:
            return False

    # zegor : set folderish to false to solve folder_contents tab problem
    # isPrincipiaFolderish=ComputedAttribute(getIsPrincipiaFolderish, 1)
    isPrincipiaFolderish = property(getIsPrincipiaFolderish)

    def listFolderContents(self, spec=None, contentFilter=None, suppressHiddenFiles=0 ):
        return []

    def hasPermission(self):
        refObject = self.getAlias()
        if refObject is not None:
            if self.portal_membership.checkPermission('View', refObject):
                return 1 # user has permission
            else:
                return 0 # user has no permission
        else:
            uid = self.getAliasUID()

            if uid:
                return -1
            else:
                return -2


    def getTargetObjectLayout(self, target):
        """
        Returns target object 'view' action page template
        """
        if ISelectableBrowserDefault.providedBy(target):
            return target.getLayout()
        else:
            view = target.getTypeInfo().getActionById('view')
            # If view action is view, try to guess correct template
            if view == 'view':
                view = target.portal_type.lower() + '_view'
            return view


    def targetMainMacro(self):
        """The macro that renders the central stuff of the body,
        or False if no"""

        target = self.getAlias()
        if ISelectableBrowserDefault.providedBy(target):
            layout = target.getLayout()
        else:
            portal_types = getMultiAdapter((self, self.REQUEST),
                                            name=u'plone_tools').types()
            type_info = portal_types.getTypeInfo(target)
            try:
                view_action = type_info.getActionInfo('object/view')
                layout = view_action['url'].split('/')[-1] or \
                                getattr(type_info, 'default_view', 'view')
            except:
                # We can't have a layout
                return False
        return target.restrictedTraverse(layout).macros.get('main', False)


registerType(Alias)
