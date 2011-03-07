"""ShowcaseImage content-type
"""
from AccessControl import ClassSecurityInfo

from zope.interface import implements

try:
  from Products.LinguaPlone.public import *
except ImportError:
  # No multilingual support
  from Products.Archetypes.public import *
  
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.content.image import ATImage

from Products.CMFPlone import PloneMessageFactory as _p
from Products.CMFCore.permissions import View

from raptus.showcase.interfaces import IShowcaseImage
from raptus.showcase.config import PROJECTNAME
from raptus.showcase import ShowcaseMessageFactory as _

from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget
from Products.CMFCore.permissions import ModifyPortalContent

ShowcaseImageSchema = ATImage.schema.copy() + Schema((
    
    IntegerField ('x',
                  widget = IntegerWidget(label = _(u'X Position'),
                                         description = _(u'The X position in the showcase box'),
                                         )
                  ),
                  
    IntegerField ('y',
                  widget = IntegerWidget(label = _(u'Y Position'),
                                         description = _(u'The Y position in the showcase box'),
                                         )
                  ),

                  
    IntegerField ('clipWidth',
                  widget = IntegerWidget(label = _(u'clip width'),
                                         description = _(u'width before it will cut image'),
                                         )
                  ),
                  
    IntegerField ('clipHeight',
                  widget = IntegerWidget(label = _(u'clip height'),
                                         description = _(u'height before it will cut the image'),
                                         )
                  ),
    IntegerField ('clipLeft',
                  widget = IntegerWidget(label = _(u'clip left'),
                                         description = _(u'left position'),
                                         )
                  ),
                  
    IntegerField ('clipTop',
                  widget = IntegerWidget(label = _(u'clip top'),
                                         description = _(u'top position'),
                                         )
                  ),
    
    ReferenceField('referenceField',
            relationship = 'relatesTo',
            multiValued = False,
            isMetadata = True,
            languageIndependent = False,
            index = 'KeywordIndex',
            write_permission = ModifyPortalContent,
            widget = ReferenceBrowserWidget(
                     allow_search = True,
                     allow_browse = True,
                     show_indexes = False,
                     force_close_on_insert = True,
                     label = _p(u'label_related_items', default=u'Related Items'),
                     description = '',
                     visible = {'edit' : 'visible', 'view' : 'invisible' }
                )
            ),
))
for field in ('creators', 'contributors', 'rights', 'subject', 'language', 'location', 'allowDiscussion'):
    if ShowcaseImageSchema.has_key(field):
        ShowcaseImageSchema[field].widget.visible = 0

ShowcaseImageSchema.changeSchemataForField('x', 'settings')
ShowcaseImageSchema.changeSchemataForField('y', 'settings')
ShowcaseImageSchema.changeSchemataForField('clipWidth', 'settings')
ShowcaseImageSchema.changeSchemataForField('clipHeight', 'settings')
ShowcaseImageSchema.changeSchemataForField('clipLeft', 'settings')
ShowcaseImageSchema.changeSchemataForField('clipTop', 'settings')


finalizeATCTSchema(ShowcaseImageSchema, folderish=True, moveDiscussion=True)

class ShowcaseImage (ATImage):
    """ A ShowcaseImage
    """
    
    implements(IShowcaseImage)
    
    portal_type = meta_type = "ShowcaseImage"
    schema = ShowcaseImageSchema
    _at_rename_after_creation = True
    
    security = ClassSecurityInfo()

    security.declareProtected(View, 'tag')
    def tag(self, **kwargs):
        """Generate image tag using the api of the ImageField
        """
        if 'title' not in kwargs:
            kwargs['title'] = self.getImageCaption()
        return self.getField('image').tag(self, **kwargs)
    
registerType(ShowcaseImage, PROJECTNAME)