"""Definition of the Flash content type
"""
from zope.interface import implements

try:
    from Products.LinguaPlone import public as atapi
except ImportError:
    # No multilingual support
    from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content import file
from Products.validation import V_REQUIRED

from Products.ContentTypeValidator.validator import ContentTypeValidator

from raptus.article.flash.interfaces import IFlash
from raptus.article.flash.config import PROJECTNAME
from raptus.article.core import RaptusArticleMessageFactory as _
from raptus.article.core.componentselection import ComponentSelectionWidget

FlashSchema = file.ATFileSchema.copy() + atapi.Schema((
        atapi.FileField('file',
                required=True,
                primary=True,
                searchable=False,
                languageIndependent=False,
                storage = atapi.AnnotationStorage(migrate=True),
                validators = (('isNonEmptyFile', V_REQUIRED),
                              ('checkFileMaxSize', V_REQUIRED),
                              ContentTypeValidator(('application/x-shockwave-flash', 'application/futuresplash',))),
                widget = atapi.FileWidget(
                        description = '',
                        label=_(u'label_flash', default=u'Flash file'),
                        show_content_type = False,),
        ),
        atapi.LinesField('components',
            enforceVocabulary = True,
            vocabulary_factory = 'componentselectionvocabulary',
            storage = atapi.AnnotationStorage(),
            schemata = 'settings',
            widget = ComponentSelectionWidget(
                description = _(u'description_component_selection_flash', default=u'Select the components in which this flash movie should be displayed.'),
                label= _(u'label_component_selection', default=u'Component selection'),
            )
        ),
    ))

FlashSchema['title'].storage = atapi.AnnotationStorage()
FlashSchema['description'].storage = atapi.AnnotationStorage()

for field in ('creators','allowDiscussion','contributors','location','language', 'nextPreviousEnabled', 'rights' ):
    if FlashSchema.has_key(field):
        FlashSchema[field].widget.visible = {'edit': 'invisible', 'view': 'invisible'}

schemata.finalizeATCTSchema(FlashSchema, folderish=False, moveDiscussion=True)

class Flash(file.ATFile):
    """A flash movie"""
    implements(IFlash)
    
    portal_type = "Flash"
    schema = FlashSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

atapi.registerType(Flash, PROJECTNAME)
