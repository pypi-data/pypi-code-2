from zope.annotation.interfaces import IAttributeAnnotatable
from zope.interface import implements

from Products.PythonScripts.standard import url_quote

from Products.ATContentTypes.content import base
from Products.ATContentTypes.content.schemata import ATContentTypeSchema, finalizeATCTSchema

from Products.Archetypes import atapi
from Products.Archetypes.utils import DisplayList

from Products.DataGridField import DataGridField, DataGridWidget
from Products.DataGridField.Column import Column
from Products.DataGridField.SelectColumn import SelectColumn


from collective.types.externalsearch import ExternalSearchMessageFactory as _
from collective.types.externalsearch.interfaces import IExternalSearch


ExternalSearchSchema = ATContentTypeSchema.copy() + atapi.Schema((


    atapi.StringField('titleLink',
        widget=atapi.StringWidget(
            label=_(u'Title Link'),
            description=_(u'Optional link for the title of the search box'),
            label_msgid='label_titleLink',
        ),
        required=False,
        storage=atapi.AnnotationStorage(),
        searchable=False,
    ),


    #Action URL
    #
    #This is the url set for the form tag
    #<form tal:attributes="action context/actionURL">
    atapi.StringField('actionURL',
        # todo: validators=('isURL',),
        widget=atapi.StringWidget(
            label=_(u'Form tag action'),
            description=_(u"The url to set the form tag's action"),
            label_msgid='label_actionURL',
        ),
        required=True,
        storage=atapi.AnnotationStorage(),
        searchable=False,
    ),
    
    atapi.StringField('formMethod',
        default='get',
        widget=atapi.SelectionWidget(
            format='select',
            label=_(u'Form Method'),
            description=_(u''),
            label_msgid='label_formMethod',
            ),
        required=True,
        storage=atapi.AnnotationStorage(),
        searchable=False,
        vocabulary="getFormMethods",
    ),
    
    atapi.StringField('searchBoxName',
        required=True,
        searchable=False,
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u'Search Box Name'),
            description=_(u'HTML name attribute for form seach box'),
            label_msgid='label_searchBoxName',
        ),
    ),

    atapi.StringField('searchBoxText',
        required=False,
        searchable=True,
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u'Search Box Default Text'),
            description=_(u"Text shown inside the search box until the user clicks. This works the same way as Plone's site search."),
            label_msgid='label_searchBoxText',
        ),
    
    ),
    
    DataGridField('hiddenFields',
        searchable = False,
        columns=("fieldName",
                 "fieldValue"
                 ),
        widget = DataGridWidget(
            label=_(u'Hidden Fields'),
            columns={
                'fieldName'  : Column(_(u"Name")),
                'fieldValue' : Column(_(u"Value")),
            },
        ),
        storage=atapi.AnnotationStorage(),
    ),
    
    atapi.StringField('submitName',
        widget=atapi.StringWidget(
            label=_(u'Submit Button Name'),
            description=_(u"Name parameter in &lt;input /&gt; tag."),
            label_msgid='label_submitName',
        ),
        required=False,
        storage=atapi.AnnotationStorage(),
        searchable=False,
    ),
    
    atapi.StringField('submitValue',
        widget=atapi.StringWidget(
            label=_(u'Submit Button Value'),
            description=_(u"Value parameter of submit button. Will be shown in place of \"Submit\" text"),
            label_msgid='label_submitValue',
        ),
        required=False,
        storage=atapi.AnnotationStorage(),
        searchable=False,
    ),


    #Image
    #An image to associate with the search.  No resizing is
    #done, make sure it's small.  Not required.
    atapi.ReferenceField('image',
        relationship='isImage',
        multiValued=False,
        storage=atapi.AnnotationStorage(),
        default_output_type="image/jpeg",
        allowed_types=('Image',),
        widget=atapi.ReferenceWidget(
            addable=True,
            label='Icon',
            label_msgid='label_icon',
            description="A small icon representing the site to be searched",
        )
    ),
    
    atapi.BooleanField('newWindow',
        widget=atapi.BooleanWidget(
            label=_(u"Search Opens in New Window"),
            description=_(u"Checking this box will force this search to open in a new window.")
        ),
        default=False,
        storage=atapi.AnnotationStorage(),
    ),

    ))


#Dublin core stuff
ExternalSearchSchema['title'].storage = atapi.AnnotationStorage()
ExternalSearchSchema['title'].widget.label = _(u"Title")
ExternalSearchSchema['title'].widget.description = _(u"")
ExternalSearchSchema['description'].storage = atapi.AnnotationStorage()
ExternalSearchSchema['description'].widget.label = _(u"Description")
ExternalSearchSchema['description'].widget.description = _("")


class ExternalSearch(base.ATCTContent):
    """This holds information on searching an external
    website for information

    Make sure ExternalSearch implements IExternalSearch
     >>> from collective.types.externalsearch.interfaces import IExternalSearch
     >>> from collective.types.externalsearch import ExternalSearch
     >>> from zope.interface.verify import verifyObject
     >>> extrnsrch = ExternalSearch('extrnsrch', )
     >>> verifyObject(IExternalSearch, extrnsrch)
     True     

    """
    implements(IExternalSearch, IAttributeAnnotatable)
    schema = ExternalSearchSchema
    portal_type = meta_type = 'collective.types.ExternalSearch'
    _at_rename_after_creation = True

    description = atapi.ATFieldProperty('description')
    actionURL = atapi.ATFieldProperty('actionURL')
    formMethod = atapi.ATFieldProperty('formMethod')
    searchBoxName = atapi.ATFieldProperty('searchBoxName')
    searchBoxText = atapi.ATFieldProperty('searchBoxText')
    hiddenFields = atapi.ATFieldProperty('hiddenFields')
    
    submitName = atapi.ATFieldProperty('submitName')
    submitValue = atapi.ATFieldProperty('submitValue')
    image = atapi.ATReferenceFieldProperty('image')
    newWindow = atapi.ATFieldProperty('newWindow')

    
    def getFormMethods(self):
        """ Get list of possible form types"""
        return DisplayList((
            ("get", "GET",),
            ("post", "POST",),
            ))
    
    def urlSafe(self, textIn):
        """Make a string URL safe"""
        return url_quote(textIn)
    
    def id_string(self):
        """Build the string for the id of the search box.
        This is to be used with the for attribute in the
        label, as well.

        Returns a string"""
        return '_'.join(('external_search', self.id))

base.registerATCT(ExternalSearch, 'collective.types.externalsearch')
