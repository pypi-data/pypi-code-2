# -*- coding: utf-8 -*-

import grok
from grok import index
from dolmen.content import IContent
from dolmen.app.site import IDolmen
from dolmen.app.content import IDescriptiveSchema
from zope.index.text.interfaces import ISearchableText


class ContentIndexes(grok.Indexes):
    """Indexes the content type of a ``dolmen.content`` `IContent`.
    """
    grok.site(IDolmen)
    grok.context(IContent)
    content_type = index.Field(attribute='__content_type__')


class DescriptiveIndexes(grok.Indexes):
    """Indexes the attributes of an `IDescriptiveSchema` content.
    """
    grok.site(IDolmen)
    grok.context(IDescriptiveSchema)

    title = index.Text()
    description = index.Text()


class SearchableIndex(grok.Indexes):
    """Indexes the searchable text of an `ISearchableText` content.
    """
    grok.site(IDolmen)
    grok.context(ISearchableText)

    searchabletext = index.Text(attribute="getSearchableText")


class SearchableDescription(grok.Adapter):
    """Provides the needed `ISearchableText` methods for
    `IDescriptiveSchema`.
    """
    grok.implements(ISearchableText)
    grok.context(IDescriptiveSchema)

    def getSearchableText(self):
        return (self.context.title, self.context.description)


__all__ = ['ContentIndexes', 'DescriptiveIndexes',
           'SearchableIndex', 'SearchableDescription']
