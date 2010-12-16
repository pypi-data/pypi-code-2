from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from Products.Organization import OrganizationMessageFactory as _

# -*- extra stuff goes here -*-

from plone.theme.interfaces import IDefaultPloneLayer

class IOrganization(Interface):
    """Marker interface
    """

class IOrganizationSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 skin layer 
       for this product.
    """
