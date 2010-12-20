# -*- coding: utf-8 -*-
"""Simple object factory base to use with schema.Object and z3c.form.

Example of Use::

  from five import grok
  from zope.interface import Interface
  from z3c.form.interfaces import IObjectFactory
  from jyu.formwidget.object.factory import AbstractBaseFactory

  from my.package.interfaces import IMySchema

  class PeriodFactory(AbstractBaseFactory, grok.MultiAdapter):
     grok.provides(IObjectFactory)
     grok.name("my.package.interfaces.IMySchema")
     grok.adapts(Interface, Interface, Interface, Interface)
     interface = IMySchema
"""

from zope import schema

from zope.interface import alsoProvides

from OFS.SimpleItem import SimpleItem


class AbstractBaseFactory(object):
    """Abstract schema.Object factory."""
    interface = None

    def __init__(self, context, request, form, widget):
        pass

    def __call__(self, value):
        """Creates a simple traversable zodb-object (OFS.SimpleItem),
        marks it with the interface of the specified schema (to make it
        work with z3c.form), initializes it with given values and returns
        the result, which will be saved as a value of an object field."""

        new_object = SimpleItem()
        alsoProvides(new_object, self.interface)
        for name, field in schema.getFieldsInOrder(self.interface):
            if name in value:
                setattr(new_object, name, value.get(name, None))
        return new_object
