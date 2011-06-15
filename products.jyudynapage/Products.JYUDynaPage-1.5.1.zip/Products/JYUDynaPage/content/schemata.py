try:
    from Products.LinguaPlone.atapi import *
except ImportError:
    # No multilingual support
    from Products.Archetypes.atapi import *

from Products.ATContentTypes.configuration import zconf
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget
from Products.JYUDynaPage import DynaPageMessageFactory as _

STYLELIST = DisplayList((
    ('normal',  _(u'Normal')),
    ('box',     _(u'Box')),
    ('batch',   _(u'Batch')),
    ('small',   _(u'Small')),
))

POSITIONLIST = DisplayList((
    ('top',     _(u'Top')),
    ('bottom',  _(u'Bottom')),
))

LISTORDER = DisplayList((
    ('reverse',   _(u'Descending (newest first)')),
    ('ascending', _(u'Ascending (oldest first)')),
))

ORDER_BY = DisplayList((
    ('created', _(u'Creation date')),
    ('effective', _(u'Publication date')),
    ('start', _(u'Start date (for events)')),
    ('sortable_title', _(u'Title')),
))

DynaPageSchema = OrderedBaseFolderSchema.copy() + Schema((
                                                                                  
    TextField('text',
        required = True,
        searchable = True,
        mutator = 'setText',
        storage = AnnotationStorage(),
        validators = ('isTidyHtmlWithCleanup',),
        default_content_type = 'text/html',
        default_output_type = 'text/x-html-safe',
        allowable_content_types = zconf.ATNewsItem.allowed_content_types,
        widget = RichWidget(
            label = _(u'Body Text'),
            rows = 25,
            allow_file_upload = zconf.ATDocument.allow_document_upload)
    ),

    BooleanField('inheritImage',
        required   = False,
        searchable = False,
        storage    = AnnotationStorage(),
        default    = False,
        widget     = BooleanWidget(
            label = _(u'Inherit header image from upper level?')
        )
    ),


    BooleanField('first_list_active',
        schemata = "1st_list",
        required = False,
        searchable = False,
        default = '1',
        storage = AnnotationStorage(),
        widget = BooleanWidget(
            label = _(u"Show list"),
        )
    ),
        
    StringField('first_list_style',
        schemata = "1st_list",
        required = False,
        searchable = False,
        vocabulary = STYLELIST,
        storage = AnnotationStorage(),
        widget = SelectionWidget(
            label = _(u"List style"),
            visible = {'edit': False, 'view': False},
        )
    ),

    StringField('first_list_position',
        schemata = "1st_list",
        required = False,
        searchable = False,
        default = "bottom",
        vocabulary = POSITIONLIST,
        storage = AnnotationStorage(),
        widget = SelectionWidget(
            label = _(u"List position"),
        )
    ),
    
    StringField("first_list_title",
        schemata = "1st_list",
        required = False,
        searchable = False,
        default = _(u"1st News List"),
        storage = AnnotationStorage(),
        widget = StringWidget(
            label = _(u"List title"),
        )
    ),

    StringField('first_list_order_by',
        schemata = "1st_list",
        required = False,
        searchable = False,
        vocabulary = ORDER_BY,
        default = 'effective',
        storage = AnnotationStorage(),
        widget = SelectionWidget(
            label = _(u"Order by"),
        )
    ),

    StringField('first_list_order',
        schemata = "1st_list",
        required = False,
        searchable = False,
        vocabulary = LISTORDER,
        default = 'reverse', # Newest first
        storage = AnnotationStorage(),
        widget = SelectionWidget(
            label = _(u"List order"),
        )
    ),

    LinesField('first_list_types',
        schemata = "1st_list",
        required = True,
        searchable = False,
        default = ('News Item',),
        vocabulary_factory = 'plone.app.vocabularies.UserFriendlyTypes', #getContentTypes',
        storage = AnnotationStorage(),
        widget = InAndOutWidget(
            label = _(u"List types"),
        )
    ),

    LinesField('first_list_state',
        schemata = "1st_list",
        default = ('published', ),
        required = False,
        vocabulary_factory = 'plone.app.vocabularies.WorkflowStates',
        storage = AnnotationStorage(),
        widget = InAndOutWidget(
            label = _(u"Select content states"),
        )
    ),
    
    LinesField('first_list_custom_view_fields',
        schemata = "1st_list",
        required = True,
        mode = "rw",
        default = ('Title',),
        vocabulary = 'listMetaDataFields',
        enforceVocabulary = True,
        storage = AnnotationStorage(),
        widget = InAndOutWidget(
            label = _(u"Table Columns"),
            description = _(u"Select which fields to display."),
        )
    ),

    LinesField('first_list_keywords',
        schemata = "1st_list",
        required = False,
        searchable = False,
        languageIndependent = True,
        vocabulary = 'getSubjects',
        storage = AnnotationStorage(),
        widget = MultiSelectionWidget(
            label = _(u"Select keywords"),
        )
    ),

    IntegerField('first_list_items',
        schemata = "1st_list",
        required = False,
        searchable = False,
        default = 4,
        languageIndependent = True,
        storage = AnnotationStorage(),
        widget = IntegerWidget(
            label = _(u"Amount of items to show"),
        )
    ),
    
    ReferenceField("first_list_path",
        schemata = "1st_list",
        required = False,
        relationship = "1_list_path",
        multiValued = True,
        languageIndependent = False,
        storage = AnnotationStorage(),
        widget = ReferenceBrowserWidget(
            allow_search = True,
            allow_browse = True,
            show_indexes = False,
            force_close_on_insert = False,
            label = _(u"Select path(s)"),
        )
    ),

    StringField('first_list_rss_title',
        schemata = "1st_list",
        required = False,
        searchable = False,
        storage = AnnotationStorage(),
        widget = StringWidget(
            label = _(u"RSS feed title"),
        )
    ),
    
    BooleanField('second_list_active',
        schemata = "2nd_list",
        required = False,
        searchable = False,
        default = False,
        storage = AnnotationStorage(),
        widget = BooleanWidget(
            label = _(u"Show list"),
        )
    ),

    StringField('second_list_style',
        schemata = "2nd_list",
        required = False,
        searchable = False,
        vocabulary = STYLELIST,
        storage = AnnotationStorage(),
        widget = SelectionWidget(
            label = _(u"List style"),
        )
    ),

    StringField('second_list_position',
        schemata = "2nd_list",
        required = False,
        searchable = False,
        default = "bottom",
        vocabulary = POSITIONLIST,
        storage = AnnotationStorage(),
        widget = SelectionWidget(
            label = _("List position")
        )
    ),

    StringField('second_list_title',
        schemata = "2nd_list",
        required = False,
        searchable = False,
        default = _(u"2nd News List"),
        storage = AnnotationStorage(),
        widget = StringWidget(
            label = _(u"List title"),
        )
    ),

    StringField('second_list_order_by',
        schemata = "2nd_list",
        required = False,
        searchable = False,
        vocabulary = ORDER_BY,
        default = 'effective',
        storage = AnnotationStorage(),
        widget = SelectionWidget(
            label = _(u"Order by"),
        )
    ),

    StringField('second_list_order',
        schemata = "2nd_list",
        required = False,
        searchable = False,
        vocabulary = LISTORDER,
        default = 'reverse', # Another option would be 'ascending'
        storage = AnnotationStorage(),
        widget = SelectionWidget(
            label = _(u"List order"),
        )
    ),

    LinesField('second_list_types',
        schemata = "2nd_list",
        required = True,
        searchable = False,
        vocabulary_factory = 'plone.app.vocabularies.UserFriendlyTypes',
        default = ('Event',),
        storage = AnnotationStorage(),
        widget = InAndOutWidget(
            label = _(u"List types"),
        )
    ),

    LinesField('second_list_state',
        schemata = "2nd_list",
        default = ('published', ),
        required = False,
        vocabulary_factory = 'plone.app.vocabularies.WorkflowStates',
        storage = AnnotationStorage(),
        widget = InAndOutWidget(
            label = _(u"Select content states"),
        )
    ),
    
    LinesField('second_list_custom_view_fields',
        schemata = "2nd_list",
        required = True,
        mode = "rw",
        default = ('Title',),
        vocabulary = 'listMetaDataFields',
        enforceVocabulary = True,
        storage = AnnotationStorage(),
        widget = InAndOutWidget(
            label = _(u"Table Columns"),
            description = _(u"Select which fields to display."),
        )
    ),
        
    LinesField('second_list_keywords',
        schemata = "2nd_list",
        required = False,
        searchable = False,
        languageIndependent = True,
        vocabulary = 'getSubjects',
        storage = AnnotationStorage(),
        widget = MultiSelectionWidget(
            label = _(u"Select keywords"),
        )
    ),

    IntegerField('second_list_items',
        schemata = "2nd_list",
        required = False,
        searchable = False,
        default = 4,
        languageIndependent = True,
        storage = AnnotationStorage(),
        widget = IntegerWidget(
            label = _(u"Amount of items to show"),
        )
    ),

    ReferenceField('second_list_path',
        schemata = "2nd_list",
        required = False,
        relationship = '2_list_path',
        multiValued = True,
        languageIndependent = False,
        storage = AnnotationStorage(),
        widget = ReferenceBrowserWidget(
            allow_search = True,
            allow_browse = True,
            show_indexes = False,
            force_close_on_insert = False,
            label = _(u"Select path(s)"),
            )
        ),

    StringField('second_list_rss_title',
        schemata = "2nd_list",
        required = False,
        searchable = False,
        storage = AnnotationStorage(),
        widget = StringWidget(
            label = _(u"RSS feed title"),
        )
    ),

    BooleanField('third_list_active',
        schemata = "3rd_list",
        required = False,
        searchable = False,
        default = False,
        storage = AnnotationStorage(),
        widget = BooleanWidget(
            label = _(u"Show list"),
        )
    ),

    StringField('third_list_style',
        schemata = "3rd_list",
        required = False,
        searchable = False,
        vocabulary = STYLELIST,
        storage = AnnotationStorage(),
        widget = SelectionWidget(
            label = _(u"List style"),
        )
    ),

    StringField('third_list_position',
        schemata = "3rd_list",
        required = False,
        searchable = False,
        default = "bottom",
        vocabulary = POSITIONLIST,
        storage = AnnotationStorage(),
        widget = SelectionWidget(
            label = _(u"List position"),
        )
    ),
    
    StringField('third_list_title',
        schemata = "3rd_list",
        required = False,
        searchable = False,
        default = _("3rd News List"),
        storage = AnnotationStorage(),
        widget = StringWidget(
            label = _(u"List title"),
        )
    ),

    StringField('third_list_order_by',
        schemata = "3rd_list",
        required = False,
        searchable = False,
        vocabulary = ORDER_BY,
        default = 'effective',
        storage = AnnotationStorage(),
        widget = SelectionWidget(
            label = _(u"Order by"),
        )
    ),

    StringField('third_list_order',
        schemata = "3rd_list",
        required = False,
        searchable = False,
        vocabulary = LISTORDER,
        default = 'reverse', # Another option would be 'ascending'
        storage = AnnotationStorage(),
        widget = SelectionWidget(
            label = _(u"List order"),
        )
    ),

    LinesField('third_list_types',
        schemata = "3rd_list",
        required = True,
        searchable = False,
        vocabulary_factory = 'plone.app.vocabularies.UserFriendlyTypes',
        default = ('News Item',),
        storage = AnnotationStorage(),
        widget = InAndOutWidget(
            label = _(u"List types"),
        )
    ),

    LinesField('third_list_state',
        schemata = "3rd_list",
        default = ('published', ),
        required = False,
        vocabulary_factory = 'plone.app.vocabularies.WorkflowStates',
        storage = AnnotationStorage(),
        widget = InAndOutWidget(
            label = _(u"Select content states"),
        )
    ),
    
    LinesField('third_list_custom_view_fields',
        schemata = "3rd_list",
        required = True,
        mode = "rw",
        default = ('Title',),
        vocabulary = 'listMetaDataFields',
        enforceVocabulary = True,
        storage = AnnotationStorage(),
        widget = InAndOutWidget(
            label = _(u"Table Columns"),
            description = _(u"Select which fields to display."),
        )
    ),

    LinesField('third_list_keywords',
        schemata = "3rd_list",
        required = False,
        searchable = False,
        languageIndependent = True,
        vocabulary = 'getSubjects',
        storage = AnnotationStorage(),
        widget = MultiSelectionWidget(
            label = _(u"Select keywords"),
        )
    ),

    IntegerField('third_list_items',
        schemata = "3rd_list",
        required = False,
        searchable = False,
        default = 4,
        languageIndependent = True,
        storage = AnnotationStorage(),
        widget = IntegerWidget(
            label = _(u"Amount of items to show"),
        )
    ),

    ReferenceField('third_list_path',
        schemata = "3rd_list",
        required = False,
        relationship = '3_list_path',
        multiValued = True,
        languageIndependent = False,
        storage = AnnotationStorage(),
        widget = ReferenceBrowserWidget(
            allow_search = True,
            allow_browse = True,
            show_indexes = False,
            force_close_on_insert = False,
            label = _(u"Select path(s)"),
            )
        ),

    StringField('third_list_rss_title',
        schemata = "3rd_list",
        required = False,
        searchable = False,
        storage = AnnotationStorage(),
        widget = StringWidget(
            label = _(u"RSS feed title"),
        )
    ),

    BooleanField('fourth_list_active',
        schemata = "4th_list",
        required = False,
        searchable = False,
        default = False,
        storage = AnnotationStorage(),
        widget = BooleanWidget(
            label = _(u"Show list"),
        )
    ),
        
    StringField('fourth_list_style',
        schemata = "4th_list",
        required = False,
        searchable = False,
        vocabulary = STYLELIST,
        storage = AnnotationStorage(),
        widget = SelectionWidget(
            label = _(u"List style"),
        )
    ),

    StringField('fourth_list_position',
        schemata = "4th_list",
        required = False,
        searchable = False,
        default = "bottom",
        vocabulary = POSITIONLIST,
        storage = AnnotationStorage(),
        widget = SelectionWidget(
            label = _(u"List position"),
        )
    ),
    
    StringField('fourth_list_title',
        schemata = "4th_list",
        required = False,
        searchable = False,
        default = _(u"4th News List"),
        storage = AnnotationStorage(),
        widget = StringWidget(
            label = _(u"List title"),
        )
    ),

    StringField('fourth_list_order_by',
        schemata = "4th_list",
        required = False,
        searchable = False,
        vocabulary = ORDER_BY,
        default = 'effective',
        storage = AnnotationStorage(),
        widget = SelectionWidget(
            label = _(u"Order by"),
        )
    ),

    StringField('fourth_list_order',
        schemata = "4th_list",
        required = False,
        searchable = False,
        vocabulary = LISTORDER,
        default = 'reverse', # Another option would be 'ascending'
        storage = AnnotationStorage(),
        widget = SelectionWidget(
            label = _(u"List order"),
        )
    ),

    LinesField('fourth_list_types',
        schemata = "4th_list",
        required = True,
        searchable = False,
        vocabulary_factory = 'plone.app.vocabularies.UserFriendlyTypes',
        default = ('News Item',),
        storage = AnnotationStorage(),
        widget = InAndOutWidget(
            label = _(u"List types"),
        )
    ),

    LinesField('fourth_list_state',
        schemata = "4th_list",
        default = ('published', ),
        required = False,
        vocabulary_factory = 'plone.app.vocabularies.WorkflowStates',
        storage = AnnotationStorage(),
        widget = InAndOutWidget(
            label = _(u"Select content states"),
        )
    ),
    
    LinesField('fourth_list_custom_view_fields',
        schemata = "4th_list",
        required = True,
        mode = "rw",
        default = ('Title',),
        vocabulary = 'listMetaDataFields',
        enforceVocabulary = True,
        storage = AnnotationStorage(),
        widget = InAndOutWidget(
            label = _(u"Table Columns"),
            description = _(u"Select which fields to display."),
        )
    ),

    LinesField('fourth_list_keywords',
        schemata = "4th_list",
        required = False,
        searchable = False,
        languageIndependent = True,
        vocabulary = 'getSubjects',
        storage = AnnotationStorage(),
        widget = MultiSelectionWidget(
            label = _(u"Select keywords"),
        )
    ),

    IntegerField('fourth_list_items',
        schemata = "4th_list",
        required = False,
        searchable = False,
        default = 4,
        languageIndependent = True,
        storage = AnnotationStorage(),
        widget = IntegerWidget(
            label = _(u"Amount of items to show"),
        )
    ),

    ReferenceField('fourth_list_path',
        schemata = "4th_list",
        required = False,
        relationship = '4_list_path',
        multiValued = True,
        languageIndependent = False,
        storage = AnnotationStorage(),
        widget = ReferenceBrowserWidget(
            allow_search = True,
            allow_browse = True,
            show_indexes = False,
            force_close_on_insert = False,
            label = _(u"Select path(s)"),
            )
        ),

    StringField('fourth_list_rss_title',
        schemata = "4th_list",
        required = False,
        searchable = False,
        storage = AnnotationStorage(),
        widget = StringWidget(
            label = _(u"RSS feed title"),
        )
    ),
))

# Next we'll clean the schema
DynaPageSchema['description'].schemata = "default"
