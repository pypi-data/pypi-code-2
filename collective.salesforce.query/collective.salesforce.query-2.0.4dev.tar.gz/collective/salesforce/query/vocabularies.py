# -*- coding: utf-8 -*-
from zope.interface import implements
from zope.app import zapi
from os import path

from Products.CMFCore.utils import getToolByName

from zope.schema import vocabulary

from collective.salesforce.query import queryMessageFactory as _

class TitledVocabulary(vocabulary.SimpleVocabulary):
    def fromTitles(cls, items, *interfaces):
        """Construct a vocabulary from a list of (value,title) pairs.

        The order of the items is preserved as the order of the terms
        in the vocabulary.  Terms are created by calling the class
        method createTerm() with the pair (value, title).

        One or more interfaces may also be provided so that alternate
        widgets may be bound without subclassing.
        """

        terms = [cls.createTerm(value,value,title) for (value,title) in items]
        return cls(terms, *interfaces)
    fromTitles = classmethod(fromTitles)

def SalesforceDatatypes( context ):
    salesforce = getToolByName(context, 'portal_salesforcebaseconnector')
    types = salesforce.describeGlobal()['types']
    return TitledVocabulary.fromTitles([(i,i) for i in types])
