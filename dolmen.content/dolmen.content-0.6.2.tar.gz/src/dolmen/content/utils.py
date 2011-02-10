# -*- coding: utf-8 -*-


def get_content_type(component):
    return getattr(component, '__content_type__', None)
