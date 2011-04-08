from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from collective.salesforce.query import queryMessageFactory as _

class ISalesforceGenericObject(Interface):
    """An object to be populated with fake attributes"""
