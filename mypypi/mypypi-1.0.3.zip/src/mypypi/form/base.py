##############################################################################
#
# Copyright (c) 2009 Projekt01 GmbH and Contributors.
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

__docformat__ = "reStructuredText"

import zope.interface
import zope.component
import zope.schema.interfaces
from zope.schema.fieldproperty import FieldProperty

from z3c.form import interfaces, widget

from mypypi.form.interfaces import IMultiWidget


class MultiWidget(widget.Widget):
    """None Term based sequence widget base.

    The multi widget is used for ITuple or IList if no other widget is defined.

    Some IList or ITuple are using another specialized widget if they can
    choose from a collection. e.g. a IList of IChoice. The base class of such
    widget is the ISequenceWidget.

    This widget can handle none collection based sequences and offers add or
    remove values to or from the sequence. Each sequence value get rendered by
    it's own relevant widget. e.g. IList of ITextLine or ITuple of IInt

    Each widget get rendered within a sequence value. This means each internal
    widget will repressent one value from the mutli widget value. Based on the
    nature of this (sub) widget setup the internal widget do not have a real
    context and can't get binded to it. This makes it impossible to use a
    sequence of collection where the collection needs a context. But that
    should not be a problem since sequence of collection will use the
    SequenceWidget as base.
    """

    zope.interface.implements(IMultiWidget)

    allowAdding = True
    allowRemoving = True

    widgets = None
    _value = None

    _mode = FieldProperty(interfaces.IWidget['mode'])

    def __init__(self, request):
        super(MultiWidget, self).__init__(request)
        self.widgets = []
        self._value = []

    @property
    def counterName(self):
        return '%s.count' % self.name

    @property
    def counterMarker(self):
        # this get called in render from the template and contains always the
        # right amount of widgets we use.
        return '<input type="hidden" name="%s" value="%d" />' % (
            self.counterName, len(self.widgets))

    @apply
    def mode():
        """This invokes updateWidgets on any value change e.g. update/extract."""
        def get(self):
            return self._mode
        def set(self, mode):
            self._mode = mode
            # ensure that we apply the new mode to the widgets
            for w in self.widgets:
                w.mode = mode
        return property(get, set)

    def getWidget(self, idx):
        """Setup widget based on index id with or without value."""
        valueType = self.field.value_type
        widget = zope.component.getMultiAdapter((valueType, self.request),
            interfaces.IFieldWidget)
        self.setName(widget, idx)
        widget.mode = self.mode
        #set widget.form (objectwidget needs this)
        if interfaces.IFormAware.providedBy(self):
            widget.form = self.form
            zope.interface.alsoProvides(
                widget, interfaces.IFormAware)
        widget.update()
        return widget

    def setName(self, widget, idx):
        widget.name = '%s.%i' % (self.name, idx)
        widget.id = '%s-%i' % (self.id, idx)

    def appendAddingWidget(self):
        """Simply append a new empty widget with correct (counter) name."""
        # since we start with idx 0 (zero) we can use the len as next idx
        idx = len(self.widgets)
        widget = self.getWidget(idx)
        self.widgets.append(widget)

    def applyValue(self, widget, value=interfaces.NOVALUE):
        """Validate and apply value to given widget.

        This method gets called on any multi widget value change and is
        responsible for validating the given value and setup an error message.

        This is internal apply value and validation process is needed because
        nothing outside this multi widget does know something about our
        internal sub widgets.
        """
        if value is not interfaces.NOVALUE:
            try:
                # convert widget value to field value
                converter = interfaces.IDataConverter(widget)
                fvalue = converter.toFieldValue(value)
                # validate field value
                zope.component.getMultiAdapter(
                    (self.context,
                     self.request,
                     self.form,
                     getattr(widget, 'field', None),
                     widget),
                    interfaces.IValidator).validate(fvalue)
                # convert field value to widget value
                widget.value = converter.toWidgetValue(fvalue)
            except (zope.schema.ValidationError, ValueError), error:
                # on exception, setup the widget error message
                view = zope.component.getMultiAdapter(
                    (error, self.request, widget, widget.field,
                     self.form, self.context), interfaces.IErrorViewSnippet)
                view.update()
                widget.error = view
                # set the wrong value as value
                widget.value = value

    def updateWidgets(self):
        """Setup internal widgets based on the value_type for each value item.
        """
        oldLen = len(self.widgets)
        self.widgets = []
        idx = 0
        if self.value:
            for v in self.value:
                widget = self.getWidget(idx)
                self.applyValue(widget, v)
                self.widgets.append(widget)
                idx += 1
        missing = oldLen - len(self.widgets)
        if missing > 0:
            # add previous existing new added widgtes
            for i in xrange(missing):
                widget = self.getWidget(idx)
                self.widgets.append(widget)
                idx += 1

    def updateAllowAddRemove(self):
        """Update the allowAdding/allowRemoving attributes
        basing on field constraints and current number of widgets
        """
        if not zope.schema.interfaces.IMinMaxLen.providedBy(self.field):
            return
        max_length = self.field.max_length
        min_length = self.field.min_length
        num_items = len(self.widgets)
        self.allowAdding = bool((not max_length) or (num_items < max_length))
        self.allowRemoving = bool(num_items and (num_items > min_length))

    @apply
    def value():
        """This invokes updateWidgets on any value change e.g. update/extract."""
        def get(self):
            return self._value
        def set(self, value):
            self._value = value
            # ensure that we apply our new values to the widgets
            self.updateWidgets()
        return property(get, set)

    def extract(self, default=interfaces.NOVALUE):
        # This method is responsible to get the widgets value based on the
        # request and nothing else.
        # We have to setup the widgets for extract their values, because we
        # don't know how to do this for every field without the right widgets.
        # Later we will setup the widgets based on this values. This is needed
        # because we probably set a new value in the form for our multi widget
        # which whould generate a different set of widgets.
        if self.request.get(self.counterName) is None:
            # counter marker not found
            return interfaces.NOVALUE
        counter = int(self.request.get(self.counterName, 0))
        values = []
        append = values.append
        # extract value for existing widgets
        for idx in range(counter):
            widget = self.getWidget(idx)
            append(widget.value)
        if len(values) == 0:
            # no multi value found
            return interfaces.NOVALUE
        return values
