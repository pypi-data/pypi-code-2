# -*- coding: utf-8 -*-
from Acquisition import aq_inner

from zope.interface import alsoProvides, noLongerProvides
from plone.z3cform.interfaces import IDeferSecurityCheck


def traverse(self, name, ignored):

    form = self._prepareForm()

    # Since we cannot check security during traversal,
    # we delegate the check to the widget view.
    alsoProvides(self.request, IDeferSecurityCheck)
    form.update()
    noLongerProvides(self.request, IDeferSecurityCheck)

    # Resolve all widgets from form and its subforms
    widgets = {}

    def resolve(form, widgets, prefix=u""):
        for key in form.widgets:
            obj = form.widgets.get(key)
            widgets[prefix + key] = obj
            if hasattr(obj, "subform"):
                resolve(getattr(obj, "subform"), widgets,
                          prefix + key + u".widgets.")
    resolve(form, widgets)

    # Find the widget - it may be in a form or in a group
    if name in widgets:
        widget = widgets.get(name)
    elif form.groups is not None:
        for group in form.groups:
            if name in group.widgets:
                widget = group.widgets.get(name)

    # Make the parent of the widget the traversal parent.
    # This is required for security to work in Zope 2.12
    if widget is not None:
        widget.__parent__ = aq_inner(self.context)
        return widget

    return None
