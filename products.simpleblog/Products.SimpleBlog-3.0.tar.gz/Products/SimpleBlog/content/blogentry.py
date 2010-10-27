from Products.Archetypes.public import *
from Products.CMFCore import permissions

from Products.CMFCore.permissions import View
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.permissions import ManageProperties

from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import *
from Products.SimpleBlog.Permissions import CROSS_POST_PERMISSION
from Products.SimpleBlog.config import ENTRY_IS_FOLDERISH
from Products.SimpleBlog.config import PROJECTNAME
from Products.ATContentTypes.content.document import finalizeATCTSchema
from Products.ATContentTypes.content.base import ATCTContent, ATCTFolder


if ENTRY_IS_FOLDERISH:
    schema = ATCTFolder.schema.copy()
    parentClass = ATCTFolder
else:
    schema = ATCTContent.schema.copy()
    parentClass = ATCTContent

schema = schema +  Schema((
    StringField('description',
                searchable=1,
                isMetadata=1,
                accessor='Description',
                widget=TextAreaWidget(label='Description',
                                      label_msgid="label_entry_description",
                                      description_msgid="help_entry_description",
                                      i18n_domain="SimpleBlog",
                                      description='Give a description for this entry.')),
    TextField('body',
              searchable=1,
              required=0,
              primary=1,
              default_content_type='text/html',
              default_output_type = 'text/x-html-safe',
              allowable_content_types=('text/plain','text/structured', 'text/html', 'text/restructured'),
              widget=RichWidget(label='Body',
                                label_msgid="label_entry_body",
                                description_msgid="help_entry_body",
                                i18n_domain="SimpleBlog",
                                description="")),

    ReferenceField('crossPosts',
                   multiValued=1,
                   required=0,
                   relationship='AppearsIn',
                   write_permission=CROSS_POST_PERMISSION,
                   allowed_types=('Blog',),
                   widget=ReferenceBrowserWidget(
                       force_close_on_insert=1,
                       i18n_domain="SimpleBlog",
                       label_msgid="label_crosspost",
                       description_msgid="help_crosspost",
                       label='Cross posts',
                       description='Select one or more other blogs where this entry will appear in when published additionally to this blog.')),
    LinesField('categories',
               accessor='EntryCategory',
               edit_accessor='EntryCategory',
               index='KeywordIndex',
               schemata='categorization',
               vocabulary='listCategories',
               widget=MultiSelectionWidget(format='select',
                                           label_msgid="label_entry_categories",
                                           description_msgid="help_entry_categories",
                                           i18n_domain="SimpleBlog",
                                           label='Categories',
                                           description='Select to which categories this Entry belongs to')),
    BooleanField('alwaysOnTop',
                 default=0,
                 schemata='settings',
                 index='FieldIndex:schema',
                 widget=BooleanWidget(label='Entry is always listed on top',
                                      label_msgid="label_always_top",
                                      description_msgid="help_always_top",
                                      i18n_domain="SimpleBlog",
                                      description='Controls if the Entry (when published) shown as the first Entry. If not checked, the effective date is used.')),

))

# Finalise the schema according to ATContentTypes standards. This basically
# moves the Related items and Allow discussion fields to the bottom of the
# form. See ATContentTypes.content.schemata for details.

schema['subject'].widget.visible={'view':'invisible', 'edit':'invisible'} # we already have the category field. having subject too is confusing
finalizeATCTSchema(schema)

class BlogEntry(parentClass):
    """
    A BlogEntry can exist inside a SimpleBlog Folder or an EntryFolder
    """

    schema = schema

    # Make sure we get title-to-id generation when an object is created
    _at_rename_after_creation = True

    if ENTRY_IS_FOLDERISH:
        filter_content_types=1
        allowed_content_types=('Link', 'Image', 'File')

    #actions = ({
        #'id': 'view',
        #'name': 'View',
        #'action': 'string:${object_url}/blogentry_view',
        #'permissions': (permissions.View,)
        #},)

    def canSetDefaultPage(self):
        return False


    def getAlwaysOnTop(self):
        if hasattr(self, 'alwaysOnTop'):
            if self.alwaysOnTop==None or self.alwaysOnTop==0:
                return 0
            else:
                return 1
        else:
            return 0

    def getIcon(self, relative_to_portal=0):
        try:
            if self.getAlwaysOnTop()==0:
                return 'entry_icon.gif'
            else:
                return 'entry_pin.gif'
        except:
            return 'entry_icon.gif'

    def listCategories(self):
        # traverse upwards in the tree to collect all the available categories
        # stop collecting when a SimpleBlog object is reached

        cats=[]
        parent=self.aq_parent
        portal=self.portal_url.getPortalObject()

        while parent!=portal:
            if parent.portal_type=='Blog' or parent.portal_type=='BlogFolder':
                # add cats
                pcats=parent.getCategories()
                for c in pcats:
                    if c not in cats:
                        cats.append(c)
                if parent.portal_type=='Blog':
                    break
            parent=parent.aq_parent

        # add the global categories
        for c in self.simpleblog_tool.getGlobalCategories():
            if not c in cats:
                cats.append(c)
        cats.sort()
        return tuple(cats)

    def start(self):
        return self.getEffectiveDate()

    def end(self):
        """
        return the same data as start() since an entry is not an event but an item that is published on a specific
        date. We want the entries in the calendar to appear on only one day.
        """
        return self.getEffectiveDate()

registerType(BlogEntry, PROJECTNAME)
