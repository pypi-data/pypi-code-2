"""Showcase content-type
"""
from AccessControl import ClassSecurityInfo

from zope.interface import implements

try:
  from Products.LinguaPlone.public import *
except ImportError:
  # No multilingual support
  from Products.Archetypes.public import *
  
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.content.folder import ATFolder

from Products.CMFCore.permissions import View

from raptus.showcase.interfaces import IShowcase
from raptus.showcase.config import PROJECTNAME
from raptus.showcase import ShowcaseMessageFactory as _


ShowcaseSchema = ATFolder.schema.copy() + Schema((
        
    StringField('showcaseEditor',
        widget = StringWidget(label = _('Showcase editor'),
                              macro = 'showcaseboxwidget',
                              helper_js = ('showcaseboxwidget.js', 'jquery.rightClick.js', 'jquery.leftClick.js'),
                              helper_css = ('showcaseboxwidget.css',), )
    ),
))

for field in ('text', 'image', 'allowDiscussion', 'creators','contributors','location','subject','language','rights','presentation', 'tableContents',):
    if ShowcaseSchema.has_key(field):
        ShowcaseSchema[field].widget.visible = 0

finalizeATCTSchema(ShowcaseSchema, folderish=True, moveDiscussion=True)

class Showcase (ATFolder):
    """ A Showcase
    """
    implements(IShowcase)
    
    portal_type = meta_type = "Showcase"
    schema = ShowcaseSchema
    _at_rename_after_creation = True
    
    security = ClassSecurityInfo()

    security.declareProtected(View, 'tag')
    def tag(self, **kwargs):
        """Generate image tag using the api of the ImageField
        """
        if 'title' not in kwargs:
            kwargs['title'] = self.getImageCaption()
        return self.getField('image').tag(self, **kwargs)
    
    
registerType(Showcase, PROJECTNAME)