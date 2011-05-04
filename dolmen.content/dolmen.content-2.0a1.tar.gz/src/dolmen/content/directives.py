# -*- coding: utf-8 -*-

import martian
from dolmen.content.interfaces import IFactory
from zope.interface import classImplements
from zope.interface.interfaces import IInterface
from zope.interface.advice import addClassAdvisor
from zope.schema.fieldproperty import FieldProperty
from zope.schema import getFieldsInOrder
from zope.schema.interfaces import IField
from zope.interface.interface import InterfaceClass


class Fields(object):
    def __init__(self, *ifaces):
        fields = []
        for iface in ifaces:
            if isinstance(iface, InterfaceClass):
                for name, field in getFieldsInOrder(iface):
                    fields.append((name, field))
            elif IField.providedBy(iface):
                name = iface.__name__
                if not name:
                    raise ValueError(
                        "Field has no name")
                fields.append((name, iface))

        seq = []
        byname = {}
        for name, field in fields:
            name = field.__name__
            if name in byname:
                raise ValueError("Duplicate name", name)
            seq.append(field)
            byname[name] = field

        self.__Fields_seq__ = seq
        self.__Fields_byname__ = byname

    def __len__(self):
        return len(self.__Fields_seq__)

    def __iter__(self):
        return iter(self.__Fields_seq__)

    def __getitem__(self, name):
        return self.__Fields_byname__[name]

    def get(self, name, default=None):
        return self.__Fields_byname__.get(name, default)


def validateSchema(directive, *ifaces):
    for iface in ifaces:
        if not IInterface.providedBy(iface):
            raise martian.error.GrokImportError(
                "%s directive can only use interface classes. "
                "%s is not an interface class. " % (directive.name, iface))


def verifyFactory(directive, factory):
    if factory and not IFactory.implementedBy(factory):
        raise martian.error.GrokImportError(
            "%s directive can only use classes that implement IFactory. "
            "%s is not a valid factory. " % (directive.name, factory))


class schema(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    validate = validateSchema

    def factory(self, *schemas):
        addClassAdvisor(_schema_advice, depth=3)
        return list(schemas)


def _schema_advice(cls):
    interfaces = schema.bind().get(cls)

    formfields = Fields(*interfaces)
    for field in formfields:
        fname = field.__name__
        if not hasattr(cls, fname):
            setattr(cls, fname, FieldProperty(field))

    classImplements(cls, *interfaces)
    return cls


class factory(martian.Directive):
    scope = martian.CLASS_OR_MODULE
    store = martian.ONCE
    validate = verifyFactory


class nofactory(martian.MarkerDirective):
    scope = martian.CLASS
    store = martian.ONCE_NOBASE


__all__ = ['factory', 'nofactory', 'schema', 'Fields']
