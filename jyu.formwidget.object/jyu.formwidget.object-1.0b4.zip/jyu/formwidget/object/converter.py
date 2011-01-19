# -*- coding: utf-8 -*-
"""DataConverter for ObjectWidget"""

from five import grok

from zope.interface import directlyProvides

from zope.schema import getFieldNames
from zope.schema.interfaces import IObject

from z3c.form.interfaces import \
    IObjectWidget, IDataConverter, NO_VALUE
from z3c.form.converter import BaseDataConverter


class TransientObject(object):
    """A dummy transient object, which is used to hold the target
    object's data while manipulating it within z3c.form framework"""

    def __init__(self, schema, data=None):
        directlyProvides(self, schema)
        if isinstance(data, dict):
            for name in getFieldNames(schema):
                setattr(self, name, data.get(name, NO_VALUE))
        elif isinstance(data, object):
            for name in getFieldNames(schema):
                setattr(self, name, getattr(data, name, NO_VALUE))
   

class ObjectConverter(BaseDataConverter, grok.MultiAdapter):
    """Data converter for IObjectWidget"""
    grok.provides(IDataConverter)
    grok.adapts(IObject, IObjectWidget)

    def toWidgetValue(self, value):
        """Convert object properties into dictionary values"""
        if value is self.field.missing_value:
            return NO_VALUE
        obj = dict()
        for name in getFieldNames(self.field.schema):
            if IObject.providedBy(self.field.schema[name]):
                obj_value = getattr(value, name, NO_VALUE)
                if obj_value == NO_VALUE:
                    obj[name] = NO_VALUE
                else:
                    obj[name] = TransientObject(\
                        self.field.schema[name].schema, obj_value)
            else:
                obj[name] = getattr(value, name, NO_VALUE)
        return obj

    def toFieldValue(self, value):
        """Convert dictionary value into TransitionObject with field.schema"""
        if value is NO_VALUE:
            return self.field.missing_value
        return TransientObject(self.field.schema, value)
