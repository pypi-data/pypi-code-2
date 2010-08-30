from PyQt4.QtCore import *
from PyQt4 import QtGui

import pomsets.parameter as ParameterModule

import pomsets_app.gui.qt as QtModule

class Controller(QtModule.Controller, QtGui.QDialog):

    def __init__(self, *args, **kwds):
        QtGui.QDialog.__init__(self, *args, **kwds)
        QtModule.Controller.__init__(self)
        return


    def parameter(self, value=None):
        if value is not None:
            self._parameter = value
        if not hasattr(self, '_parameter'):
            self._parameter = None
        return self._parameter

    def definition(self, value=None):
        if value is not None:
            self._definition = value
        if not hasattr(self, '_definition'):
            self._definition = None
        return self._definition



    def shouldAllowEdit(self, value=None):
        if value is not None:
            self._shouldAllowEdit = value
        if not hasattr(self, '_shouldAllowEdit'):
            self._shouldAllowEdit = None
        return self._shouldAllowEdit


    def populate(self):

        widget = self.widget()
        contextManager = self.contextManager()

        parameter = self.parameter()

        windowTitle = 'View parameter'
        if self.shouldAllowEdit():
            windowTitle = 'Edit parameter'
        self.setWindowTitle(windowTitle)

        textEditName = widget.textEditName
        textEditName.setText(parameter.id() or '')
        textEditDescription=widget.textEditDescription
        textEditDescription.setText(parameter.description() or '')

        comboBoxDirection = widget.comboBoxDirection
        comboBoxDirection.addItems([
                ParameterModule.PORT_DIRECTION_INPUT,
                ParameterModule.PORT_DIRECTION_OUTPUT])
        direction = parameter.portDirection()
        if parameter.getAttribute(ParameterModule.PORT_ATTRIBUTE_ISSIDEEFFECT):
            direction = ParameterModule.PORT_DIRECTION_OUTPUT
        index = comboBoxDirection.findText(direction)
        if index >= 0:
            comboBoxDirection.setCurrentIndex(index)

        checkBoxCommandline = widget.checkBoxCommandline
        isCommandline = parameter.getAttribute(
            ParameterModule.PORT_ATTRIBUTE_COMMANDLINE)
        checkBoxCommandline.setChecked(isCommandline)

        textEditFlag = widget.textEditFlag
        if isCommandline:

            commandlineOptions = parameter.getAttribute(
                ParameterModule.PORT_ATTRIBUTE_COMMANDLINE_OPTIONS,
                defaultValue = {}
            )

            prefixFlag = commandlineOptions.get(
                ParameterModule.COMMANDLINE_PREFIX_FLAG, []
            )
            textEditFlag.setText(' '.join(prefixFlag))
            pass

        
        checkBoxOptional = widget.checkBoxOptional
        isOptional = parameter.optional()
        checkBoxOptional.setChecked(isOptional)

        checkBoxFile = widget.checkBoxFile
        isFile =  parameter.getAttribute(
            ParameterModule.PORT_ATTRIBUTE_ISINPUTFILE) or \
            parameter.getAttribute(
            ParameterModule.PORT_ATTRIBUTE_ISSIDEEFFECT)
        checkBoxFile.setChecked(isFile)

        checkBoxList = widget.checkBoxList
        argumentValueIsList = parameter.getAttribute(
            ParameterModule.PORT_ATTRIBUTE_ISLIST)
        checkBoxList.setChecked(argumentValueIsList)

        if isCommandline and argumentValueIsList:
            checkBoxDistributeFlag = widget.checkBoxDistributeFlag
            shouldDistributePrefixFlag = commandlineOptions.get(
                ParameterModule.COMMANDLINE_PREFIX_FLAG_DISTRIBUTE, False)
            checkBoxDistributeFlag.setChecked(shouldDistributePrefixFlag)
            pass

        self.setVisibilityOfWidgetItems()

        if not self.shouldAllowEdit():
            textEditName.setReadOnly(True)
            textEditDescription.setReadOnly(True)
            comboBoxDirection.setEditable(False)
            comboBoxDirection.setEnabled(False)
            checkBoxCommandline.setEnabled(False)
            textEditFlag.setReadOnly(True)
            checkBoxOptional.setEnabled(False)
            checkBoxFile.setEnabled(False)
            checkBoxList.setEnabled(False)
            widget.checkBoxDistributeFlag.setEnabled(False)

        textEditName.setFocus()

        return


    def setVisibilityOfWidgetItems(self):
        widget = self.widget()

        checkBoxList = widget.checkBoxList
        checkboxCommandline = widget.checkBoxCommandline

        isList = checkBoxList.isChecked()
        isCommandline = checkboxCommandline.isChecked()

        shouldShowFlag = True
        shouldShowDistributeFlag = True
        # enable the flag items only if commandline is checked
        if isCommandline:
            shouldShowFlag = True
            # enable the distribute flag items only if 
            # both commandline and list are checked
            if isList:
                shouldShowDistributeFlag = True
            else:
                shouldShowDistributeFlag = False
            pass
        else:
            shouldShowFlag = False
            shouldShowDistributeFlag = False
            pass

        for childWidget, visibilitySetting in [
            (widget.labelFlag, shouldShowFlag),
            (widget.textEditFlag, shouldShowFlag),
            (widget.checkBoxDistributeFlag, shouldShowDistributeFlag)]:
            childWidget.setVisible(visibilitySetting)

        return


    @pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBox_clicked(self, button):
        widget = self.widget()
        buttonRole = widget.buttonBox.buttonRole(button)
        if buttonRole == QtGui.QDialogButtonBox.ApplyRole:
            if self.shouldAllowEdit():
                self.saveValues()
            pass
        if buttonRole == QtGui.QDialogButtonBox.AcceptRole:
            if self.shouldAllowEdit():
                self.saveValues()
            self.accept()
            pass
        if buttonRole == QtGui.QDialogButtonBox.RejectRole:
            self.reject()
            pass
        return


    @pyqtSlot(int)
    def on_checkBoxList_stateChanged(self, newState):
        self.setVisibilityOfWidgetItems()
        return

    @pyqtSlot(int)
    def on_checkBoxCommandline_stateChanged(self, newState):
        self.setVisibilityOfWidgetItems()
        return


    def saveValues(self):

        widget = self.widget()
        contextManager = self.contextManager()
        pomsetContext = self.pomsetContext()
        parameter = self.parameter()
        
        hasBeenModified = False
        
        name = str(widget.textEditName.text())
        if not name == parameter.id():
            self.definition().renameParameter(parameter.id(), name)
            hasBeenModified = True

        description = str(widget.textEditDescription.text())
        if not description == parameter.description():
            parameter.description(description)
            hasBeenModified = True

        direction = str(widget.comboBoxDirection.currentText())
        isFile = widget.checkBoxFile.isChecked()
        isInputFile = False
        isSideEffect = False
        if isFile:
            if direction == ParameterModule.PORT_DIRECTION_OUTPUT:
                direction = ParameterModule.PORT_DIRECTION_INPUT
                isSideEffect = True
            else:
                isInputFile = True
        
        if not parameter.portDirection() == direction:
            parameter.portDirection(direction)
            hasBeenModified = True
        if not parameter.getAttribute(ParameterModule.PORT_ATTRIBUTE_ISSIDEEFFECT) == isSideEffect:
            parameter.setAttribute(
                ParameterModule.PORT_ATTRIBUTE_ISSIDEEFFECT, isSideEffect)
            hasBeenModified = True
        if not parameter.getAttribute(ParameterModule.PORT_ATTRIBUTE_ISINPUTFILE) == isInputFile:
            parameter.setAttribute(
                ParameterModule.PORT_ATTRIBUTE_ISINPUTFILE, isInputFile)
            hasBeenModified = True

        checkBoxCommandline = widget.checkBoxCommandline
        isCommandline = checkBoxCommandline.isChecked()
        if not parameter.getAttribute(ParameterModule.PORT_ATTRIBUTE_COMMANDLINE) == isCommandline:
            parameter.setAttribute(
                ParameterModule.PORT_ATTRIBUTE_COMMANDLINE, isCommandline)
            hasBeenModified = True

        commandlineOptions = {}
        if isCommandline:

            # flag
            textEditFlag = widget.textEditFlag
            prefixFlag = str(textEditFlag.text()).split(' ')
            commandlineOptions[ParameterModule.COMMANDLINE_PREFIX_FLAG] = prefixFlag

            # distribute flag
            checkBoxDistributeFlag = widget.checkBoxDistributeFlag
            shouldDistributeFlag = checkBoxDistributeFlag.isChecked()
            commandlineOptions[ParameterModule.COMMANDLINE_PREFIX_FLAG_DISTRIBUTE] = shouldDistributeFlag
            pass

        currentCommandlineOptions = parameter.getAttribute(
            ParameterModule.PORT_ATTRIBUTE_COMMANDLINE_OPTIONS,
            defaultValue = {}
            )
        if not currentCommandlineOptions == commandlineOptions:
            parameter.setAttribute(
                ParameterModule.PORT_ATTRIBUTE_COMMANDLINE_OPTIONS,
                commandlineOptions
            )
            hasBeenModified = True


        # handle whether the parameter is optional
        checkBoxOptional = widget.checkBoxOptional
        isOptional = checkBoxOptional.isChecked()
        if not parameter.optional() == isOptional:
            parameter.optional(isOptional)
            hasBeenModified = True


        if hasBeenModified:

            pomsetContext.isModified(True)
            
            contextManager.mainWindow().emit(
                SIGNAL("OnPomsetModified(PyQt_PyObject)"), pomsetContext)
        return


    # END class Controller
    pass
