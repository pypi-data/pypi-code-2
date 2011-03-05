from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from collective.salesforce.query import queryMessageFactory as _

class ISalesforceQuery(Interface):
    """A page showing content from Salesforce"""
    
    # -*- schema definition goes here -*-
    datatype = schema.TextLine(
        title=_(u"Data Type"), 
        required=True,
        description=_(u"Select data type from Salesforce"),
    )

