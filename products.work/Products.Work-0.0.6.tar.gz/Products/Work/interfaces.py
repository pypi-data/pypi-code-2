from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from Products.Work import WorkMessageFactory as _

# -*- extra stuff goes here -*-

from plone.theme.interfaces import IDefaultPloneLayer

class IWork(Interface):
    """Marker interface
    """

class IWorkSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 skin layer 
       for this product.
    """
