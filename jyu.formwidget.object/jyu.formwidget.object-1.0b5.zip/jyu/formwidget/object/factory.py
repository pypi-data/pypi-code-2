# -*- coding: utf-8 -*-
"""Simple object factory base to use with schema.Object and z3c.form.

Example of Use::

  from five import grok
  from zope.interface import Interface
  from z3c.form.interfaces import IObjectFactory
  from jyu.formwidget.object.factory import AbstractBaseFactory

  class MySchemaObjectFactory(AbstractBaseFactory, grok.MultiAdapter):
     grok.provides(IObjectFactory)
     grok.name("my.package.interfaces.IMySchema")
     grok.adapts(Interface, Interface, Interface, Interface)
"""

from OFS.SimpleItem import SimpleItem


class AbstractBaseFactory(object):
    """Abstract schema.Object factory."""

    def __init__(self, context, request, form, widget):
        pass

    def __call__(self, value):
        """Create SimpleItem and let DataManger to both
        mark it with proper interface and populate it."""
        return SimpleItem()
