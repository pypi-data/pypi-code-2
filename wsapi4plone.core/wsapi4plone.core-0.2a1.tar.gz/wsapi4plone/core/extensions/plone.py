# -*- coding: utf-8 -*-
# FIXME Move this to a better location in the package.
from zope.component import getUtility
from zope.interface import implements, Interface

from wsapi4plone.core.interfaces import (
    ICallbackExtension, IFormatQueryResults, IReadExtension)
from wsapi4plone.core.extension import BaseExtension


class IPloneContents(IReadExtension, ICallbackExtension):
    """An extension to get at Plone Folder items."""


class PloneContents(BaseExtension):
    implements(IPloneContents)

    @property
    def contents_query(self):
        if getattr(self, '_content_query', None) is None:
            self._contents_query = IContentsQuery(self.context)
        return self._contents_query

    def get_callback(self):
        query_args = self.contents_query.arguments()
        contents = {'function': 'query',
                    'args': query_args}

    def get(self):
        formatter = getUtility(IFormatQueryResults)
        return formatter(self.contents_query.results())


class IContentsQuery(Interface):
    """Adapter to provide the query results for a given object."""

    def arguments(self):
        """Returns the arguments (in dictionary format) that are used to
        make the query for the contents."""

    def results(self):
        """A method to obtain the results from ZCatalog search."""


class BaseContentQuery(object):

    def __init__(self, context):
        self.context = context

    def results(self):
        return self.context.portal_catalog(*self.arguments())

class PloneFolderContents(BaseContentQuery):

    def arguments(self):
        arg = {'path': {
            'query': '/'.join(self.context.getPhysicalPath()), 'depth': 1}
            }
        return (arg,)
