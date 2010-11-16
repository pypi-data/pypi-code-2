##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Optional Dropdown Widget

$Id: widget.py 71676 2006-12-29 16:23:00Z srichter $
"""
__docformat__ = "reStructuredText"
import zope.component
import zope.schema.interfaces
from zope.app import form
from zope.app.form import browser
from zope.app.form.browser.itemswidgets import ItemDisplayWidget
from zope.app.form.interfaces import MissingInputError

class OptionalDisplayWidget(ItemDisplayWidget):

    def __call__(self):
        """See IBrowserWidget."""
        value = self._getFormValue()
        if not value:
            return self.translate(self._messageNoValue)
        elif value not in self.vocabulary:
            return value
        else:
            term = self.vocabulary.getTerm(value)
            return self.textForValue(term)


class OptionalDropdownWidget(object):
    """Optional Dropdown Widget"""
    zope.interface.implements(browser.interfaces.IBrowserWidget,
                              form.interfaces.IInputWidget)

    connector = u'<br />\n'

    _prefix = 'field.'

    # See zope.app.form.interfaces.IWidget
    name = None
    label = property(lambda self: self.context.title)
    hint = property(lambda self: self.context.description)
    visible = True

    # See zope.app.form.interfaces.IInputWidget
    required = property(lambda self: self.context.required)

    def __init__(self, field, request):
        self.context = field
        self.request = request
        # Clone field again, because we change the ``require`` options
        clone = field.bind(field.context)
        clone.required = False
        clone.value_type.required = False
        # Setup the custom value widget
        clone.value_type.__name__ = 'custom'
        self.customWidget = zope.component.getMultiAdapter(
            (clone.value_type, request), form.interfaces.IInputWidget)
        # Setup the dropdown widget
        self.dropdownWidget = form.browser.DropdownWidget(
            clone, clone.vocabulary, request)
        # Setting the prefix again, sets everything up correctly
        self.setPrefix(self._prefix)

    def setRenderedValue(self, value):
        """See zope.app.form.interfaces.IWidget"""
        if value in self.context.vocabulary:
            self.dropdownWidget.setRenderedValue(value)
            self.customWidget.setRenderedValue(
                self.context.value_type.missing_value)
        else:
            self.customWidget.setRenderedValue(value)
            self.dropdownWidget.setRenderedValue(
                self.context.missing_value)

    def setPrefix(self, prefix):
        """See zope.app.form.interfaces.IWidget"""
        # Set the prefix locally
        if not prefix.endswith("."):
            prefix += '.'
        self._prefix = prefix
        self.name = prefix + self.context.__name__
        self.customWidget.setPrefix(self.name+'.')
        self.dropdownWidget.setPrefix(self.name+'.')

    def getInputValue(self):
        """See zope.app.form.interfaces.IInputWidget"""
        customMissing = self.context.value_type.missing_value
        if (self.customWidget.hasInput() and
            self.customWidget.getInputValue() != customMissing):
            return self.customWidget.getInputValue()

        dropdownMissing = self.context.value_type.missing_value
        if (self.dropdownWidget.hasInput() and
            self.dropdownWidget.getInputValue() != dropdownMissing):
            return self.dropdownWidget.getInputValue()

        raise MissingInputError(self.name, self.label,
                                zope.schema.interfaces.RequiredMissing())


    def applyChanges(self, content):
        """See zope.app.form.interfaces.IInputWidget"""
        field = self.context
        new_value = self.getInputValue()
        old_value = field.query(content, self)
        # The selection of an existing scoresystem has not changed
        if new_value == old_value:
            return False
        field.set(content, new_value)
        return True

    def hasInput(self):
        """See zope.app.form.interfaces.IInputWidget"""
        return self.dropdownWidget.hasInput() or self.customWidget.hasInput()

    def hasValidInput(self):
        """See zope.app.form.interfaces.IInputWidget"""
        customValid = self.customWidget.hasValidInput()
        customMissing = self.context.value_type.missing_value
        dropdownValid = self.dropdownWidget.hasValidInput()
        dropdownMissing = self.context.missing_value
        # If the field is required and both values are missing, then the input
        # is invalid
        if self.context.required:
            return (
                (customValid and
                 self.customWidget.getInputValue() != customMissing)
                or
                (dropdownValid and
                 self.dropdownWidget.getInputValue() != dropdownMissing)
                )
        # If the field is not required, we just need either input to be valid,
        # since both generated widgets have non-required fields.
        return customValid or dropdownValid

    def hidden(self):
        """See zope.app.form.browser.interfaces.IBrowserWidget"""
        return '\n'.join((self.dropdownWidget.hidden(),
                          self.customWidget.hidden()))


    def error(self):
        """See zope.app.form.browser.interfaces.IBrowserWidget"""
        dropdownError = self.dropdownWidget.error()
        if dropdownError:
            return dropdownError
        return self.customWidget.error()


    def __call__(self):
        """See zope.app.form.browser.interfaces.IBrowserWidget"""
        return self.connector.join((self.dropdownWidget(), self.customWidget()))
