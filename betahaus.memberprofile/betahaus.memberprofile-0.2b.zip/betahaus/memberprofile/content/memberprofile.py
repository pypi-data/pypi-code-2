from zope.interface import implements

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import View, ModifyPortalContent

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from AccessControl import ClassSecurityInfo

from archetypes.memberdatastorage.memberpropertyfield import MemberPropertyField

from betahaus.memberprofile import MemberProfileMessageFactory as _
from betahaus.memberprofile.content.interfaces import IMemberProfile
from betahaus.memberprofile.config import PROJECTNAME
from betahaus.memberprofile.content import mixin
from betahaus.memberprofile.interfaces import IMemberProfileSettingsAdapter  



Schema = folder.ATFolderSchema.copy() + mixin.BaseProfile.schema.copy() + mixin.ImageMixin.schema.copy() + atapi.Schema((
    atapi.TextField(
        name='text',
        required=False,
        searchable=True,
        primary=True,
        storage = atapi.AnnotationStorage(migrate=True),
        validators = ('isTidyHtmlWithCleanup',),
        default_output_type = 'text/x-html-safe',
        widget = atapi.RichWidget(
                  label = _(u'text_label', default = u'Presentation of you'),
                  description = _(u'text_description', default = u''),
                  rows = 10
        ),
    ),
))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

#Don't show content type in navigation portlets etc.
Schema['excludeFromNav'].default = True

# Title uses the fullname field instead so we preserve compatibility with Plones fullname property.
Schema['title'].storage = atapi.AnnotationStorage()
Schema['title'].searchable = True
#Schema['title'].widget.label = _(u'label_memberprofile_title', default=u'Your full name or display name')
Schema['title'].widget.visible = {'view':'invisible','edit':'invisible'}

# Description is used as biography in some views, 
# for instance personalize_form
Schema['description'].storage = atapi.AnnotationStorage() 
Schema['description'].searchable = False
Schema['description'].widget.label= _(u'label_memberprofile_description', default=u'Short biography or description')
Schema['description'].widget.description = _(u'description_memberprofile_description', default = u'Shown in listings and as description in searches.')

Schema.moveField('lastname', pos='top')
Schema.moveField('firstname', pos='top')

schemata.finalizeATCTSchema(Schema, moveDiscussion=False)

class MemberProfile(folder.ATFolder, mixin.BaseProfile, mixin.ImageMixin):
    """Member profile content type"""
    implements(IMemberProfile)
    security = ClassSecurityInfo()

    portal_type = meta_type = "MemberProfile"
    archetype_name = _(u'Member profile')
    schema = Schema


    security.declareProtected(View, 'getTitle')
    def getTitle(self):
        """Override accessor for title"""
        return self.Title()
    
    security.declareProtected(View, 'Title')
    def Title(self):
        """ Override accessor for title.
            This gets called lots of times on edit, even before schema init, hence the try-except.
            Watch out...
        """
        url_tool = getToolByName(self, 'portal_url', None)
        if url_tool is None:
            return ''
        portal = url_tool.getPortalObject()
        title_as = IMemberProfileSettingsAdapter(portal).get('title_as')
        if title_as == 'firstname_lastname':
            try:
                name_title = "%s %s" % (self.getFirstname(),self.getLastname())
                name_title = name_title.strip()
                if len(name_title) == 0:
                    # there is no name set, fallback to username
                    name_title = self.getId()
                return name_title
            
            except AttributeError:
                return ''
        #Use userid as title
        else:
            #Profiles always have the same id as the user who owns them
            return self.getId()
    
    security.declareProtected(ModifyPortalContent, 'setTitle')
    def setTitle(self, value, **kwargs):
        """Override mutator for title"""
        #Userid is immutable, firstname/lastname is already setable.
        pass

atapi.registerType(MemberProfile, PROJECTNAME)
