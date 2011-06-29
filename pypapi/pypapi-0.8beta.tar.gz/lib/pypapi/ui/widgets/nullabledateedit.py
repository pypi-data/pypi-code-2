# encoding: utf-8
# Copyright (c) 2011 AXIA Studio <info@pypapi.org>
# and Municipality of Riva del Garda TN (Italy).
#
# This file is part of PyPaPi Framework.
#
# This file may be used under the terms of the GNU General Public
# License versions 3.0 or later as published by the Free Software
# Foundation and appearing in the file LICENSE.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
#


import time
from PyQt4.QtGui import QLineEdit, QWidget, QHBoxLayout, QToolButton, QIcon,\
                        QCalendarWidget, QDialog
from PyQt4.QtCore import SIGNAL, Qt, pyqtProperty, QString, QDate, QPoint, QRect
from zope.interface import implements
from zope.component import provideHandler, adapter
from pypapi.ui.cute import interfaces, widget
import pypapi.ui.resources

class NullableDateEdit(QWidget):

    implements(interfaces.INullableDateEditWidget)

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.lineedit = QLineEdit()
        self.lineedit.setInputMask('99/99/9999')
        self.button_calendar = QToolButton(self)
        self.button_calendar.setIcon(QIcon(":/icons/calendar.png"))
        self.button_calendar.setObjectName("button_calendar")
        self.connect(self.button_calendar, SIGNAL('clicked()'), self.openCalendar)
        self.connect(self.lineedit, SIGNAL('editingFinished ()'), self.editingFinished)
        self.connect(self.lineedit, SIGNAL('textEdited ( const QString & )'), lambda s: self.setTextEdited(True))
        self.lineedit.installEventFilter(self)
        self._null = False
        layout = QHBoxLayout(self)
        layout.setMargin(0)
        layout.addWidget(self.lineedit, 1)
        layout.addWidget(self.button_calendar, 2)
        self.setFocusPolicy(Qt.TabFocus)
        self.setLayout(layout)

    def setDisplayFormat(self, format):
        self._displayFormat = format
        return QString('dd/MM/yyyy')
    def displayFormat(self):
        return self._displayFormat
    displayFormat = pyqtProperty('QString', displayFormat, setDisplayFormat)

    def setCalendarPopup(self, popup):
        self._calendarPopup = popup
        return QString('dd/MM/yyyy')
    def calendarPopup(self):
        return self._calendarPopup
    calendarPopup = pyqtProperty('bool', calendarPopup, setCalendarPopup)

    def text(self):
        t = self.lineedit.text()
        return self.lineedit.text()

    def setText(self, value):
        t = time.strptime(value, '%Y-%m-%dT%H:%M:%S')
        if t.tm_year > 1900:
            value = time.strftime('%d/%m/%Y', t)
        else:
            value = ''
        if not isinstance(value, QString):
            value = QString(value)
        self.lineedit.setText(value)
        self.lineedit.setCursorPosition(0)

    text = pyqtProperty('QString', text, setText)


    def textEdited(self):
        return self._text_edited
    def setTextEdited(self, value):
        self._text_edited = value
    text_edited = property(textEdited, setTextEdited)

    def editingFinished(self):
        t = self.lineedit.text()
        try:
            d = time.strptime(t, '%d/%m/%Y')
        except ValueError:
            self.lineedit.setText('')

    def openCalendar(self):
        rect = self.geometry()
        pos = self.mapToGlobal(QPoint(0, 0))
        h = 100
        d_y = rect.height()
        new_rect = QRect(pos.x(), pos.y() + d_y, rect.width(), h)
        popup = CalendarPopup(self)
        popup.setGeometry(new_rect)
        res = popup.exec_()


class CalendarPopup(QDialog):

    def __init__(self, parent=None):
        flags = Qt.FramelessWindowHint | Qt.Dialog
        QDialog.__init__(self, parent, flags)
        cal = QCalendarWidget()
        self.connect(cal, SIGNAL('clicked( const QDate & )'), self.clickDate)
        layout = QHBoxLayout(self)
        layout.addWidget(cal)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.current_date = None
        if parent is not None:
            t = parent.text
            try:
                d = time.strptime(t, '%d/%m/%Y')
                self.current_date = QDate(d.tm_year, d.tm_mon, d.tm_mday)
                cal.setSelectedDate(self.current_date)
            except ValueError:
                pass

    def clickDate(self, date):
        self.current_date = date
        if self.parent() is not None:
            self.parent().lineedit.setText(date.toString('dd/MM/yyyy'))
        self.accept()


@adapter(interfaces.INullableDateEditWidget, interfaces.IWidgetCreationEvent)
def nullableDateEditWidgetBinding(data_widget, event):

    dc = interfaces.IDataContext(data_widget)
    col_index = widget.resolveColumn(data_widget, dc)[0]
    dc.mapper.addMapping(data_widget, col_index, 'text')

provideHandler(nullableDateEditWidgetBinding)
