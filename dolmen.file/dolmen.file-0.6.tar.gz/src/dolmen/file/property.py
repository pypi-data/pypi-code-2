# -*- coding: utf-8 -*-

from dolmen.file import NamedFile, INamedFile


_marker = object()


class FileProperty(object):
    """Stores the given file data in an INamedFile component.
    """

    def __init__(self, field, name=None, factory=NamedFile):
        if name is None:
            name = field.__name__

        if not INamedFile.implementedBy(factory):
            raise ValueError("Provided factory is not a valid INamedFile")

        self.__field = field
        self.__name = name
        self.__factory = factory

    def __set__(self, inst, value):
        name = self.__name
        field = self.__field.bind(inst)
        fields = inst.__dict__

        if field.readonly and self.__name in field:
            raise ValueError(self.__name, 'field is readonly')

        if value is not None:
            filename = getattr(value, 'filename', None)
            file = self.__factory(data=value, filename=filename)
        else:
            file = None

        fields[name] = file
        inst._p_changed = True

    def __get__(self, inst, klass):
        if inst is None:
            return self

        value = inst.__dict__.get(self.__name, _marker)
        if value is _marker:
            field = self.__field.bind(inst)
            value = getattr(field, 'default', _marker)
            if value is _marker:
                raise AttributeError(self.__name)
        return value

    def __getattr__(self, name):
        return getattr(self.__field, name)
