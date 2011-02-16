# -*- coding: utf-8 -*-

import martian
from dolmen.content import directives


def get_content_type(component):
    return getattr(component, '__content_type__', None)


def get_schema(component):
    ifaces = directives.schema.bind().get(component)
    if ifaces is martian.UNKNOWN:
        return directives.schema.default
    return ifaces
