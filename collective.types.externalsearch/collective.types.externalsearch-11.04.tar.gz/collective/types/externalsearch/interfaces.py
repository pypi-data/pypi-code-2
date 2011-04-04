from zope.interface import Interface
from zope import schema

#from Products.CMFPlone import PloneMessageFactory as _
from collective.types.externalsearch import ExternalSearchMessageFactory as _

class IExternalSearch(Interface):
    """A widget to query an external resource
    """
    title = schema.TextLine(
        title=_(u'Title'),
        required=True)

    description = schema.Text(
        title=_(u'Description'),
        required=True)

    actionURL = schema.TextLine(
        title=_(u'Form tag action'),
        required=True,
    )
    
    formMethod = schema.TextLine(
        title=_(u'Form Method'),
        required=True,
    )
    
    searchBoxName = schema.TextLine(
        title=_(u'Search Box Name'),
        required=True,
    )
    
    searchBoxText = schema.TextLine(
        title=_(u'Search Box Default Text'),
        required=False,
    )
    
    hiddenFields = schema.List(
        title=_('Hidden Fields'),
        value_type=schema.Dict(),
    )
    
    submitName = schema.TextLine(
        title=_(u'Submit Button Name'),
        required=False,
    )
    
    submitValue = schema.TextLine(
        title=_(u'Submit Button Value'),
        required=False,
    )
    
    titleLink = schema.TextLine(
        title=_(u'Optional Title Link'),
        required=False,
    )

    image = schema.TextLine(
        title=_(u"A small icon representing the site to be searched"),
        required=False)
        # todo: value_type=schema.Object(title=_(u'Image')))