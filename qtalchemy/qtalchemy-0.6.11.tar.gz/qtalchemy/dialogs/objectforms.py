# -*- coding: utf-8 -*-

from qtalchemy import MapperMixin, user_message, LayoutLayout, LayoutWidget, Message, CommandEvent
from PyQt4 import QtCore, QtGui
from sqlalchemy.orm import mapper, create_session, relation, object_session, Query
import traceback
import sys

def MessageButtonsToQt(flags):
    result = QtGui.QMessageBox.NoButton
    for x in "Ok Cancel Yes No".split(' '):
        if flags & getattr(Message, x):
            result |= getattr(QtGui.QMessageBox, x)
    return result

def QtToMessageButtons(flags):
    result = 0
    for x in "Ok Cancel Yes No".split(' '):
        if flags & getattr(QtGui.QMessageBox, x):
            result |= getattr(Message, x)
    return result

def appMessage(parent, flags, msg):
    """
    Display a Qt message box.
    """
    msgBox = QtGui.QMessageBox(parent)
    msgBox.setWindowTitle(QtGui.QApplication.applicationName())
    #if icon is not None:
    #    msgBox.setIcon( icon )
    msgBox.setText( msg )
    
    msgBox.setStandardButtons(MessageButtonsToQt(flags))
    return QtToMessageButtons(msgBox.exec_())

class SessionMessageBox(object):
    """
    This class is a callable to hook to a session message handler to display 
    messages for this session.
    """
    def __init__(self, parent=None):
        self.parent = parent

    def __call__(self, session, instance, flags, msg):
        # TODO:  pass icon
        # TODO:  pass exception info
        # TODO:  pass additional buttons
        # TODO:  allow data entry on instance (??) -- augment the message box with a bound data form
        msgBox = QtGui.QMessageBox(self.parent)
        msgBox.setWindowTitle(QtGui.QApplication.applicationName())
        #if icon is not None:
        #    msgBox.setIcon( icon )
        msgBox.setText( msg )
        
        msgBox.setStandardButtons(MessageButtonsToQt(flags))
        return QtToMessageButtons(msgBox.exec_())

def exception_message_box(e,text,parent=None,icon=None):
    """
    Extract exception information and display a message box with exception details in 
    a details extension of the message.
    """
    msg = QtGui.QMessageBox(parent)
    msg.setWindowTitle(QtGui.QApplication.applicationName())
    if icon is not None:
        msg.setIcon( icon )
    msg.setText( text )
    msg.setInformativeText( user_message(e) )
    exc_type, exc_value, exc_traceback = sys.exc_info()
    msg.setDetailedText( ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)) )
    msg.setStandardButtons( QtGui.QMessageBox.Ok )
    return msg.exec_()

def messaged_commit(session, parent):
    """
    This helper function displays a message to the user if the commit on the session fails.
    
    The message text is given by the user_message function.
    """
    try:
        session.commit()
    except Exception, e:
        exception_message_box(e,"There was an error saving the data.",parent=parent,icon=QtGui.QMessageBox.Warning)

class MapperDialog(QtGui.QDialog, MapperMixin):
    def __init__(self,parent):
        QtGui.QDialog.__init__(self,parent)

    def accept(self):
        self.submit()
        QtGui.QDialog.accept(self)

class BoundDialog(MapperDialog):
    def __init__(self,parent,session=None,flush=True):
        MapperDialog.__init__(self,parent)
        self.flush_on_close = flush
        self.session = session

    def init_simple_session(self,row,ssrc,row_id,table_type,key_col):
        # standard bit of init code to get a data session going
        if row is not None:
            self.main_row = row
            self.session=object_session(row)
        elif ssrc is not None:
            self.session=ssrc()
            if row_id is None:
                self.main_row = table_type()
                self.session.add(self.main_row)
            else:
                self.main_row = self.session.query(table_type).filter(key_col==row_id).one()
        else:
            assert False, "One of 'row' or 'ssrc' must be valid."

    def preCommandSave(self, event):
        try:
            MapperDialog.submit(self)
            if self.flush_on_close:
                self.flush()
                self.session.close()
        except Exception, e:
            self.session.rollback()
            exception_message_box(e,"There was an error saving data.",icon=QtGui.QMessageBox.Warning,parent=self)
            event.abort()

    def accept(self):
        event  = CommandEvent()
        self.preCommandSave(event)
        if not event.aborted:
            QtGui.QDialog.accept(self)

    def reject(self):
        MapperDialog.reject(self)
        if self.flush_on_close and self.session is not None:
            self.session.close()

    def flush(self):
        assert self.session is not None, "If flushing changes, we must have a session"
        self.session.commit()

def BoundDialogObject(parent,row):
    b = BoundDialog(parent)
    b.init_simple_session(row,None,None,None,None)
    b.setWindowTitle(row.DialogTitle)

    main = QtGui.QVBoxLayout()
    b.setLayout(main)
    grid = LayoutLayout(main,QtGui.QFormLayout())

    m = b.mapClass(type(row))
    for col in row.DialogVisualElements:
        m.addBoundField(grid,col)
    m.connect_instance(row)

    buttonbox = LayoutWidget(main,QtGui.QDialogButtonBox())
    buttonbox.addButton(QtGui.QDialogButtonBox.Ok)
    buttonbox.addButton(QtGui.QDialogButtonBox.Cancel)
    buttonbox.accepted.connect(b.accept)
    buttonbox.rejected.connect(b.reject)

    b.show()
    b.exec_()
