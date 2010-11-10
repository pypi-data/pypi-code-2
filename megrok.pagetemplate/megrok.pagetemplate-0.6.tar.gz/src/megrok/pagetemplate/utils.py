# -*- coding: utf-8 -*-

from zope.component import queryMultiAdapter
from megrok.pagetemplate import IPageTemplate


def getPageTemplate(context, request, name=u""):
    """A convenient function to query a PageTemplate component
    """
    return queryMultiAdapter((context, request), IPageTemplate, name=name)
