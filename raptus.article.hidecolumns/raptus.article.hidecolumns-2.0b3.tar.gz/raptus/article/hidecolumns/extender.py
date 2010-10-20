from zope.component import adapts
from zope.interface import implements
from archetypes.schemaextender.interfaces import ISchemaExtender
from Products.Archetypes.atapi import BooleanWidget
from raptus.article.core.interfaces import IArticle
from raptus.article.core import RaptusArticleMessageFactory as _

from Products.Archetypes.atapi import BooleanField
from archetypes.schemaextender.field import ExtensionField
   
class ExtensionBooleanField(ExtensionField, BooleanField):
    """A booleanfield"""    
    
class ArticleSchemaExtender(object):
    adapts(IArticle)
    implements(ISchemaExtender)

    def __init__(self, context):
        self.context = context
     
    def getFields(self):
        
        fields = [
            ExtensionBooleanField('hideLeftPortletslot',
                         required = False,
                         languageIndependent = True,
                         schemata = 'settings',
                         widget = BooleanWidget(
                                  description=_(u'description_hide_left_portletslot', default=u'If selected, the left Portletslot is hidden'),
                                  label = _(u'label_hide_left_portletslot', default=u'Hide left portletslot'),
                                  visible={'view' : 'hidden',
                                           'edit' : 'visible'},
                                  ),
            ),
            
            ExtensionBooleanField('hideRightPortletslot',
                         required = False,
                         languageIndependent = True,
                         schemata = 'settings',
                         widget = BooleanWidget(
                                  description=_(u'description_hide_right_portletslot', default=u'If selected, the right Portletslot is hidden'),
                                  label = _(u'label_hide_right_portletslot', default=u'Hide right portletslot'),
                                  visible={'view' : 'hidden',
                                           'edit' : 'visible'},
                                  ),
            ),
            
        ]
        
        return fields