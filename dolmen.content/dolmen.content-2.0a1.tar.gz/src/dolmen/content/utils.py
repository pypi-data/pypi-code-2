# -*- coding: utf-8 -*-

import martian
from dolmen.content.directives import schema, Fields


def bootstrap_object(object, *ifaces, **values):
    if values and ifaces:
        ifields = Fields(*ifaces)
        for key, value in values.items():
            ifield = ifields.get(key)
            if ifield is None:
                continue
            field = ifield.bind(object)
            field.validate(value)
            field.set(object, value)


def get_content_type(component):
    return getattr(component, '__content_type__', None)


def get_schema(component):
    ifaces = schema.bind().get(component)
    if ifaces is martian.UNKNOWN:
        return schema.default
    return ifaces


__all__ = ['bootstrap_object', 'get_content_type', 'get_schema']
