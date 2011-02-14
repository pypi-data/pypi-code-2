# -*- coding: utf-8 -*-

import os.path
import martian

from sys import modules
from dolmen import content
from martian.directive import StoreOnce


def get_absolute_path(filename, pyfile=__file__):
    if os.path.isfile(filename):
        return filename
    path = os.path.join(os.path.dirname(pyfile), filename)
    if not os.path.isfile(path):
        return None
    return path


class FileValueStoreOnce(StoreOnce):
    """Stores the abs. path of the file given as a value.
    """
    def set(self, locals_, directive, value):
        pyfile = modules[locals_['__module__']].__file__
        path = get_absolute_path(value, pyfile)
        if path is None:
            raise martian.error.GrokImportError(
                "Directive %r cannot resolve the file %r." %
                (directive.name, value))
        StoreOnce.set(self, locals_, directive, path)


FILE_PATH_ONCE = FileValueStoreOnce()


class icon(martian.Directive):
    scope = martian.CLASS
    store = FILE_PATH_ONCE
    validate = martian.validateText


icon.set(content.Content, get_absolute_path('content.png'))
icon.set(content.Container, get_absolute_path('container.png'))
icon.set(content.OrderedContainer, get_absolute_path('container.png'))
