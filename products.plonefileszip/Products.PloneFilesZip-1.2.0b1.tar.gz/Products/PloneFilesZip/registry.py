# -*- coding: iso-8859-15 -*-
# Copyright (c) 2003-2006 Ingeniweb SAS

# This software is subject to the provisions of the GNU General Public
# License, Version 2.0 (GPL).  A copy of the GPL should accompany this
# distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY,
# AGAINST INFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE

# More details in the ``LICENSE`` file included in this package.

"""
Registry utility for all file retrievers
$Id: registry.py 225402 2010-10-27 16:03:38Z glenfant $
"""

__author__  = 'Gilles Lenfant <gilles.lenfant@ingeniweb.com>'
__docformat__ = 'restructuredtext'

from interfaces import IFieldRetriever, ITypeRetriever

class GlobalRegistry:
    """Handles all FieldRetrievers"""

    def __init__(self):

        self._field_retrievers = {}
        self._type_retrievers = {}

    def register(self, retriever_klass):
        """Registers globally a retriever"""

        # Registering field retrievers
        if IFieldRetriever.isImplementedByInstancesOf(retriever_klass):
            if not self._field_retrievers.has_key(retriever_klass.field_type):
                self._field_retrievers[retriever_klass.field_type] = retriever_klass
            else:
                # FIXME: should log a hint to find conflicting retrievers
                raise ValueError, "Retriever for %s already registered" % retriever_klass.field_type

        # Registering type retrievers
        elif ITypeRetriever.isImplementedByInstancesOf(retriever_klass):
            if not self._type_retrievers.has_key(retriever_klass.meta_type):
                self._type_retrievers[retriever_klass.meta_type] = retriever_klass
            else:
                # FIXME: should log a hint to find conflicting retrievers
                raise ValueError, "Retriever for %s already registered" % retriever_klass.meta_type
        else:
            raise TypeError, "This object is not a field or type retriever"
        return


    def getRetriever(self, field_type):
        """Provides the retriever for a field_type"""

        return self._field_retrievers.get(field_type, None)

    def listFieldTypes(self):
        """Handled field_types"""

        return self._field_retrievers.keys()

    def listMetaTypes(self):
        """Handled meta types"""

        return self._type_retrievers.keys()

    def getRetrieversFor(self, content):
        """All retrievers for a content"""

        # Find if we got a type retriever for this content type
        if self._type_retrievers.has_key(content.meta_type):
            retriever_klass = self._type_retrievers[content.meta_type]
            retriever = retriever_klass(content)
            return retriever.getFieldRetrievers()

        # Okay, let's look in the fields retrievers
        fields = content.Schema().fields()
        retrievers = []
        for field in fields:
            retriever_klass = self.getRetriever(field.type)
            if retriever_klass is not None:
                retrievers.append(retriever_klass(field, content))
        return retrievers


GlobalRegistry = GlobalRegistry()

