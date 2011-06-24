# -*- coding: utf-8 -*-
##############################################################################
#       Copyright (C) 2010, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
##############################################################################
"""
This module contains convenience functions used elsewhere in the qtalchemy library.

qtalchemy using API2 of PyQt so we need to enable that before importing PyQt4.  We 
do this here as an example and to prepare for the doc-tests.  Note that it is not
illegal to call sip.setapi twice, but the second call must agree in api version with
the first.

    >>> import sip
    >>> sip.setapi('QString', 2)
    >>> sip.setapi('QVariant', 2)
"""

import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)
from PyQt4 import QtGui,QtCore
import datetime
import decimal

def fromQType(v, suggested=None):
    """
    This function takes a PyQt/PySide type and returns the most faithful representative of the item 
    in a native python type.
    
    (Basic) Examples:
    >>> type(fromQType(toQType(45)))
    <type 'int'>
    >>> fromQType(toQType(datetime.date.today()))==datetime.date.today()
    True
    """
    if hasattr(v, "toPyObject"):  # PyQt QVariant
        if v.isNull():
            return None
        v = v.toPyObject()
    elif hasattr(v, "toPyDateTime"):  # PyQt QDateTime
        if v.isNull():
            return None
        v = v.toPyDateTime()
    elif hasattr(v, "toPyDate"):  # PyQt QDate
        if v.isNull():
            return None
        v = v.toPyDate()
    elif hasattr(v, "toPyTime"):  # PyQt QTime
        if v.isNull():
            return None
        v = v.toPyTime()
    elif hasattr(v, "toPython"):  # PySide object
        if v.isNull():
            return None
        v = v.toPython()

    if suggested in (int, float, decimal.Decimal) and v=="":
        if suggested is decimal.Decimal:
            v = decimal.Decimal('0')
        else:
            v = suggested(0)
    elif suggested is datetime.date and isinstance(v,datetime.datetime):
        # TODO:  dangerous down-cast
        v = datetime.date(v.year,v.month,v.day)
    elif suggested is not None:
        try:
            is_ = isinstance(v,suggested)
        except TypeError as e:
            is_ = False

        if not is_:
            v = suggested(v)

    return v

def toQType(v,suggested=None):
    """
    This function takes a native python object and returns it in the most faithful way as a PyQt/PySide type.  
    For API 2, this means that basic types like str and int are returned unchanged.
    
    One notable caveat is that Qt does not have a decimal type so objects of type decimal.Decimal are returned 
    as strings.  The rationale for this is that maintaining decimal exactness of decimals is almost always the 
    right thing.
    
    Examples:
    >>> type(toQType(12))
    <type 'int'>
    >>> type(toQType("A string"))
    <type 'str'>
    >>> toQType(decimal.Decimal("12.34"))
    '12.34'
    >>> type(toQType(datetime.date(1979,1,9))) is QtCore.QDate
    True

    When the value `v` is None, we return a blank version of the suggested type.

    >>> toQType(None,suggested=str)
    ''
    >>> toQType(None,suggested=int)
    0
    """
    if isinstance(v, datetime.date):
        v = QtCore.QDate(v.year,v.month,v.day)
    elif isinstance(v, decimal.Decimal):
        v = str(v)

    if v is None and suggested is not None:
        if suggested == datetime.date:
            v = QtCore.QDate()
        else:
            # I'm baffled, suggested appears to be passed as a python type
            # but the whole point here is to return Qt type!
            v = suggested()

    return v

def ButtonBoxButton(bb,b,role=None):
    """
    :func:`.ButtonBoxButton` is a convenience function which enables button
    construction and assignment on one line of application code.
    """
    #TODO:  The return from this function can be a button or Role constant ... positively bizzarre
    if role is None:
        bb.addButton(b)
    else:
        bb.addButton(b,role)
    return b

def FormRow(form,label,widget):
    """
    :func:`.FormRow` is a convenience function which enables widget
    construction and assignment on one line of application code.
    """
    form.addRow(label,widget)
    return widget

def LayoutLayout(host,inner):
    """
    :func:`.LayoutLayout` is a convenience function which enable layout
    construction and assignment on one line of application code.
    
    See also :func:`.LayoutWidget` :func:`.FormRow` :func:`.ButtonBoxButton`

        >>> app = qtapp()
        >>> class Item(QtGui.QDialog):
        ...     def __init__(self,parent=None):
        ...         QtGui.QDialog.__init__(self,parent)
        ...         vbox = QtGui.QVBoxLayout(self)
        ... 
        ...         form = LayoutLayout(vbox,QtGui.QFormLayout())
        ...         self.book_edit = FormRow(form,"&Book Title",QtGui.QLineEdit())
        ...         self.author_edit = FormRow(form,"&Author",QtGui.QLineEdit())
        ... 
        ...         self.buttons = LayoutWidget(vbox,QtGui.QDialogButtonBox())
        ...         self.ok = ButtonBoxButton(self.buttons,QtGui.QDialogButtonBox.Save)
        ...         self.cancel = ButtonBoxButton(self.buttons,QtGui.QDialogButtonBox.Cancel)
        >>> d = Item()
        >>> d.exec_()  #doctest: +SKIP
        0
    """
    host.addLayout(inner)
    return inner

def LayoutWidget(layout,widget):
    """
    :func:`.LayoutWidget` is a convenience function which enable widget
    construction and assignment on one line of application code.
    """
    layout.addWidget(widget)
    return widget

def writeTableColumnGeo(table,name):
    settings = QtCore.QSettings()
    settings.beginGroup(name)
    for i in range(table.model().columnCount(None)):
        settings.setValue("Column%02i"%i,table.columnWidth(i))
    settings.endGroup()

def readTableColumnGeo(table,name):
    settings = QtCore.QSettings()
    settings.beginGroup(name)
    ei = table.property("ExtensionId")
    table.setProperty("ExtensionId", None)
    for i in range(table.model().columnCount(None)):
        if settings.value("Column%02i"%i,-1) != -1:
            table.setColumnWidth(i,int(settings.value("Column%02i"%i,-1)))
    table.setProperty("ExtensionId", ei)
    settings.endGroup()

def suffixExtId(parent, ext):
    id = parent.property("ExtensionId")
    if id is None:
        id = parent.objectName()
    if id is None:
        return ext
    else:
        return id+"/"+ext

class WindowGeometry(QtCore.QObject):
    """
    This class saves and restores the size and other geometry artifacts about 
    the passed QWidget.  It hooks the closeEvent by attaching itself as an 
    eventFilter to the passed QWidget.

    Table header geometry should be saved by passing an extensionId to 
    :func:`TableView.setModel` at this point.  This may change in the future.

    The geometry is persisted with QSettings under a name that is determined 
    by one of the following (with first items taking precedence).  This name 
    is determined in __init__ and saved for writing the settings later under 
    the same name.
    
    * name parameter
    * widget.property("ExtensionId")
    * widget.objectName()  (recommended)

    :param widget: the QWidget for which to save & restore state
    :param name: optional identifier to associate this in the persistent state
    :param size: save & restore window size (default True)
    :param position: save & restore window position (default True)
    :param splitters: splitters to save position
    """
    def __init__(self, widget, name=None, size=True, position=True, splitters=None):
        QtCore.QObject.__init__(self, widget)

        self.widget = widget
        self.size = size
        self.position = position
        self.name = name
        if self.name is None:
            self.name = widget.property("ExtensionId")
        if self.name is None:
            self.name = widget.objectName()
        self.splitters = splitters if splitters else []

        for s_index in range(len(self.splitters)):
            self.splitters[s_index].splitterMoved.connect(lambda pos,index,x=s_index: self.updateSplitter(x,pos,index))

        self.restoreState()

        if hasattr(self.widget, "finished"):
            self.widget.finished.connect(self.finished)
        else:
            self.widget.installEventFilter(self)

    def finished(self,i):
        self.saveState(splitters=False)

    def eventFilter(self, obj, event):
        if obj is self.widget and event.type() == QtCore.QEvent.Close:
            self.saveState(splitters=False)
        return QtCore.QObject.eventFilter(self, obj, event)

    def saveState(self, splitters=True):
        """
        This saves the state of all controlled elements.  Some elements are 
        saved immediately when modified (such as splitters).  Thus we suppress 
        the state saving on close for these elements.
        
        :param splitters:  pass False to suppress the saving of the splitter 
            state for splitters passed in __init__
        """
        settings = QtCore.QSettings()
        settings.beginGroup(self.name)
        if self.size and self.position:
            settings.setValue("geometry", self.widget.saveGeometry())
        elif self.size:
            settings.setValue("size", self.widget.size())
        elif self.position:
            settings.setValue("pos", self.widget.pos())
        
        if hasattr(self.widget, "saveState"):
            # I'm probably a QMainWindow
            settings.setValue("windowState", self.widget.saveState())

        if splitters:
            for splitter_index in range(len(self.splitters)):
                settings.setValue(self.splitter_persist_location(splitter_index),self.splitters[splitter_index].saveState())

        settings.endGroup()

    def restoreState(self):
        settings = QtCore.QSettings()
        settings.beginGroup(self.name)
        if self.size and self.position:
            if settings.value("geometry") is not None:
                self.widget.restoreGeometry(settings.value("geometry"))
        elif self.size:
            if settings.value("size") is not None:
                self.widget.resize(settings.value("size"))
        elif self.position:
            if settings.value("pos") is not None:
                self.widget.move(settings.value("pos"))
        
        if hasattr(self.widget, "saveState"):
            # I'm probably a QMainWindow
            if settings.value("windowState") is not None:
                self.widget.restoreState(settings.value("windowState"))
        
        for splitter_index in range(len(self.splitters)):
            state = settings.value(self.splitter_persist_location(splitter_index))
            if state is not None:
                self.splitters[splitter_index].restoreState(state)
        settings.endGroup()

    def splitter_persist_location(self, splitter_index):
        splitter_name = self.splitters[splitter_index].objectName()
        if splitter_name in [None, ""]:
            splitter_name = str(splitter_index)
        return "splitter/{0}".format(splitter_name)

    def updateSplitter(self,splitter_index,pos,index):
        settings = QtCore.QSettings()
        settings.beginGroup(self.name)
        settings.setValue(self.splitter_persist_location(splitter_index),self.splitters[splitter_index].saveState())
        settings.endGroup()

_test_app = None

def qtapp():
    """
    A QApplication creator for test cases.  QApplication is a single-ton and 
    this provides a safe construction wrapper.
    
    >>> app=qtapp()
    >>> # put test code here
    """
    global _test_app
    _test_app = QtGui.QApplication.instance()
    if _test_app is None:
        _test_app = QtGui.QApplication([])
    return _test_app
