from zope.interface import Interface
from zope.schema import *
from zope.schema import vocabulary as schemavocab
from Products.CMFCore.utils import getToolByName 

from Products.CMFPlone import PloneMessageFactory as _

from collective.validator.base.interfaces.interfaces import IWebValidator

class IW3cStrict(IWebValidator):
    """Marker interface for the XHTML-Strict adapter"""
