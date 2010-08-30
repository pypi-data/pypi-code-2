import logging

from PyQt4.QtCore import *
from PyQt4 import QtGui

import pypatterns.filter as FilterModule

import pomsets.parameter as ParameterModule

import pomsets_app.gui.qt as QtModule

class Controller(QtModule.Controller, QtGui.QDialog):

    def definition(self, value=None):
        if value is not None:
            self._definition = value
        if not hasattr(self, '_definition'):
            self._definition = None
        return self._definition

    def parameter(self, value=None):
        if value is not None:
            self._parameter = value
        if not hasattr(self, '_parameter'):
            self._parameter = None
        return self._parameter


    def __init__(self, *args, **kwds):
        QtGui.QDialog.__init__(self, *args, **kwds)
        QtModule.Controller.__init__(self)
        return

    def populate(self):

        widget = self.widget()
        contextManager = self.contextManager()

        definition = self.definition()
        parameter = self.parameter()

        self.setWindowTitle('Edit bindings for parameter "%s"' % parameter.id())
        
        checkBoxSweep = widget.checkBoxSweep
        isSweep = definition.isParameterSweep(parameter.id())
        checkBoxSweep.setChecked(isSweep)

        # populate the values 
        (dataNode, parameterToEdit) = \
            self.pomsetContext().getParameterToEdit(definition, parameter.id())

        values = ''
        if dataNode.hasParameterBinding(parameterToEdit.id()):
            values = '\n'.join(dataNode.getParameterBinding(parameterToEdit.id()))
        textEditValues = widget.textEditValues
        textEditValues.setPlainText(values)

        return




    @pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBox_clicked(self, button):
        widget = self.widget()
        buttonRole = widget.buttonBox.buttonRole(button)
        if buttonRole == QtGui.QDialogButtonBox.ApplyRole:
            self.saveValues()
            pass
        if buttonRole == QtGui.QDialogButtonBox.AcceptRole:
            self.saveValues()
            self.accept()
            pass
        if buttonRole == QtGui.QDialogButtonBox.RejectRole:
            self.reject()
            pass
        return


    def saveValues(self):

        widget = self.widget()
        contextManager = self.contextManager()
        pomsetContext = self.pomsetContext()
        definition = self.definition()
        parameter = self.parameter()

        hasBeenModified = False

        checkBoxSweep = widget.checkBoxSweep
        isSweep = checkBoxSweep.isChecked()
        if not definition.isParameterSweep(parameter.id()) == isSweep:
            definition.isParameterSweep(parameter.id(), isSweep)
            hasBeenModified = True

        (dataNode, parameterToEdit) = \
            self.pomsetContext().getParameterToEdit(definition, parameter.id())


        textEditValues = widget.textEditValues
        values = str(textEditValues.toPlainText()).split('\n')
        if not dataNode.hasParameterBinding(parameterToEdit.id()) or \
                not values == dataNode.getParameterBinding(parameterToEdit.id()):
            dataNode.setParameterBinding(parameterToEdit.id(),
                                         values)
            hasBeenModified = True

        if hasBeenModified:
            pomsetContext.isModified(True)
            contextManager.mainWindow().emit(
                SIGNAL("OnPomsetModified(PyQt_PyObject)"), pomsetContext)
            pass

        return


    # END class Controller
    pass
