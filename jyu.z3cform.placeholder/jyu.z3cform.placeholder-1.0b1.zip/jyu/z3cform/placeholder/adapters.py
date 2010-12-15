# -*- coding: utf-8 -*-
""" Grok adapter for rendering field placeholder as widget title """

from five import grok

from zope.interface import Interface
from zope.schema.interfaces import IField

from z3c.form.interfaces import IForm, IFormLayer, IWidget, IValue

from jyu.z3cform.placeholder.config import PLACEHOLDERS_KEY


class SchemaAnnotationAsHint(grok.MultiAdapter):
    """Schema field annotation as widget ``title`` IValue adapter."""
    grok.provides(IValue)
    grok.name("title")
    grok.adapts(Interface, IFormLayer, IForm, IField, IWidget)

    def __init__(self, context, request, form, field, widget):
        super(SchemaAnnotationAsHint, self).__init__()
        self.context = context
        self.request = request
        self.form = form
        self.field = field
        self.widget = widget

    def get(self):
        interface = getattr(self.field, "interface", None)
        if interface:
            placeholders = interface.queryTaggedValue(PLACEHOLDERS_KEY, {})
            if self.field.__name__ in placeholders:
                return placeholders[self.field.__name__]
        return None
