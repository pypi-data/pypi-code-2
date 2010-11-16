# -*- coding: utf-8 -*-
from zope.app.form.browser import SequenceDisplayWidget, SequenceWidget
from zope.app.form.interfaces import IInputWidget
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.i18n import translate
import zope.component


try:
    from zc import resourcelibrary
    haveResourceLibrary = True
except ImportError:
    haveResourceLibrary = False


def _getSubWidget(sequenceWidget, prefix="%s."):
    field = sequenceWidget.context.value_type
    if sequenceWidget.subwidget is not None:
        widget = sequenceWidget.subwidget(field, sequenceWidget.request)
    else:
        widget = zope.component.getMultiAdapter((field, sequenceWidget.request),
                                                IInputWidget)
    widget.setPrefix(prefix % (sequenceWidget.name))
    return widget

class SequenceDisplayTableWidget(SequenceDisplayWidget):
    template = ViewPageTemplateFile('sequencedisplaytablewidget.pt')

    def __call__(self):
        return self.template()

    def mainWidget(self):
        return _getSubWidget(self)

    def haveMessage(self):
        if self._renderedValueSet():
            data = self._data
        else:
            data = self.context.get(self.context.context)

        # deal with special cases:
        if data == self.context.missing_value:
            return translate(self._missingValueMessage, self.request)
        data = list(data)
        if not data:
            return translate(self._emptySequenceMessage, self.request)
        return None

    def widgets(self):
        # get the data to display:
        if self._renderedValueSet():
            data = self._data
        else:
            data = self.context.get(self.context.context)

        # deal with special cases:
        if data == self.context.missing_value:
            return translate(self._missingValueMessage, self.request)
        data = list(data)
        if not data:
            return translate(self._emptySequenceMessage, self.request)

        widgets = []
        for i, item in enumerate(data):
            #widget = self._getSubWidget(i)
            widget = self._getWidget(i)
            widget.setRenderedValue(item)
            widgets.append(widget)
        return widgets

class SequenceTableWidget(SequenceWidget):
    template = ViewPageTemplateFile('sequencetablewidget.pt')

    def mainWidget(self):
        return _getSubWidget(self)

class TupleSequenceTableWidget(SequenceTableWidget):
    _type = tuple


class ListSequenceTableWidget(SequenceTableWidget):
    _type = list


class SequenceTableJSWidget(SequenceWidget):
    template = ViewPageTemplateFile('sequencetablejswidget.pt')
    haveResourceLibrary = haveResourceLibrary

    def mainWidget(self):
        return _getSubWidget(self)

    def emptyWidget(self):
        widget = _getSubWidget(self, prefix="%s._default_rowid_")
        widget.setRenderedValue(None)
        return widget

    def _getPresenceMarker(self, count=0):
        maxval = self.context.max_length
        if maxval:
            maxval=str(maxval)
        else:
            maxval=''
        minval = self.context.min_length
        if minval:
            minval=str(minval)
        else:
            minval=''
        rv = ('<input type="hidden" name="%s.count" id="%s.count" value="%d" />'
                % (self.name, self.name, count))
        rv = rv+('<input type="hidden" name="%s.max_length" id="%s.max_length" value="%s" />'
                % (self.name, self.name, maxval))
        rv = rv+('<input type="hidden" name="%s.min_length" id="%s.min_length" value="%s" />'
                % (self.name, self.name, minval))
        return rv

    def __call__(self, *args, **kw):
        if haveResourceLibrary:
            resourcelibrary.need('sequencetable')
        return super(SequenceTableJSWidget, self).__call__(*args, **kw)

class TupleSequenceTableJSWidget(SequenceTableJSWidget):
    _type = tuple


class ListSequenceTableJSWidget(SequenceTableJSWidget):
    _type = list
