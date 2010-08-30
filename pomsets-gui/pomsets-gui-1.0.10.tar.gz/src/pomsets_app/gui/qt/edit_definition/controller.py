import functools
import logging
import os
import uuid

from PyQt4.QtCore import *
from PyQt4 import QtGui

import pypatterns.filter as FilterModule
import pypatterns.relational as RelationalModule

import pomsets.parameter as ParameterModule

import pomsets_app.gui.qt as QtModule


DROP_ABOVE = 'above'
DROP_BELOW = 'below'

def reorderParameters(parameterToMove, newParameterPosition, 
                      controller=None):

    if controller is None:
        raise ValueError('controller cannot be None')

    
    definition = controller.definition()
    contextManager = controller.contextManager()
    builder = contextManager.pomsetBuilder()
    
    # get the current parameter positions
    parameters = controller.getParametersToDisplay()
    newParameters = []

    # insert the parameter in the correct position
    parameterToDrop, dropPosition = newParameterPosition
    for parameter in parameters:
        if parameter.id() == parameterToMove.id():
            continue
        if parameter.id() == parameterToDrop.id():
            if dropPosition == DROP_ABOVE:
                newParameters.append(parameterToMove)
            newParameters.append(parameter)
            if dropPosition == DROP_BELOW:
                newParameters.append(parameterToMove)
            continue
        newParameters.append(parameter)
        pass

    # clear and rebuild the parameter orderings
    definition.parameterOrderingTable().clear()
    for sourceParameter, targetParameter in zip(newParameters[:-1], newParameters[1:]):
        builder.addParameterOrdering(
            definition, sourceParameter.id(), targetParameter.id())
        pass
    
    controller.populateParameters()
    return


def dropEvent(event, function=None, table=None):

    if function is None:
        raise ValueError('function cannot be None')
    if table is None:
        raise ValueError('table cannot be None')

    pos = event.pos()

    item = table.itemAt(pos)    
    if item is None:
        # bad drop, ignore
        return

    parameter = item.data(Qt.UserRole).toPyObject()
    dropIndicatorPosition = table.dropIndicatorPosition()
    dip = "onto"
    if dropIndicatorPosition in [QtGui.QAbstractItemView.OnItem,
                                 QtGui.QAbstractItemView.AboveItem]:
        dip = DROP_ABOVE
    elif dropIndicatorPosition == QtGui.QAbstractItemView.BelowItem:
        dip = DROP_BELOW

    draggedParameter = table.currentItem().data(Qt.UserRole).toPyObject()

    function(draggedParameter, (parameter, dip))
    return


class Controller(QtModule.Controller, QtGui.QDialog):

    def __init__(self, *args, **kwds):
        QtGui.QDialog.__init__(self, *args, **kwds)
        QtModule.Controller.__init__(self)
        return

    def shouldAllowEdit(self, value=None):
        if value is not None:
            self._shouldAllowEdit = value
        if not hasattr(self, '_shouldAllowEdit'):
            self._shouldAllowEdit = False
        return self._shouldAllowEdit

    def shouldReconstructParameterOrdering(self, value=None):
        if value is not None:
            self._shouldReconstructParameterOrdering = value
        if not hasattr(self, '_shouldReconstructParameterOrdering'):
            self._shouldReconstructParameterOrdering = False
        return self._shouldReconstructParameterOrdering

    def definition(self, value=None):
        if value is not None:
            self._definition = value
        if not hasattr(self, '_definition'):
            self._definition = False
        return self._definition

    def populate(self):

        widget = self.widget()
        contextManager = self.contextManager()

        if self.shouldAllowEdit():
            self.setWindowTitle('Edit definition')
        else:
            self.setWindowTitle('View definition')

        comboBoxExecutableType = widget.comboBoxExecutableType 
        executableTypes = contextManager.getExecutableTypes()
        comboBoxExecutableType.addItems(executableTypes)

        # update all gui items with the values from the definition
        pomsetContext = self.pomsetContext()
        definition = self.definition()

        textEditName = widget.textEditName
        textEditName.setText(definition.name() or '')
        textEditDescription =widget.textEditDescription
        textEditDescription.setText(definition.description() or '')
        
        executable = definition.executable()
        executableType = contextManager.getTypeForExecutable(executable)
        index = comboBoxExecutableType.findText(executableType)
        if index >= 0:
            comboBoxExecutableType.setCurrentIndex(index)

        self.updateGuiForEditingExecutableType(executableType)

        self.populateParameters()

        if not self.shouldAllowEdit():
            comboBoxExecutableType.setEditable(False)
            comboBoxExecutableType.setEnabled(False)
            textEditName.setReadOnly(True)
            textEditDescription.setReadOnly(True)
        return


    def updateGuiForEditingExecutableType(self, executableType):

        widget = self.widget()
        contextManager = self.contextManager()
        pomsetContext = self.pomsetContext()
        definition = self.definition()


        executable = definition.executable()
        if executable is None or \
           not contextManager.getTypeForExecutable(executable) == executableType:
            executableClass = contextManager.getClassForExecutableType(executableType)
            executable = executableClass()


        visibilityValues = []
        labelValues = {
            widget.labelExecutablePath:"Executable path"
            }
        if executableType == 'Shell':
            # turn off unnecessary widgets and
            # turn on necessary widgets
            visibilityValues = [True, True,
                                True,
                                False, False,
                                False, False,
                                True, True]

            widget.textEditExecutablePath.setText(os.path.sep.join(executable.path()))
            widget.checkBoxStageable.setChecked(executable.stageable())
            widget.textEditStaticArgs.setText(' '.join(executable.staticArgs()))
            pass
        elif executableType == 'Hadoop Jar':
            # turn off unnecessary widgets
            # turn on necessary widgets
            visibilityValues = [False, False,
                                False,
                                True, True,
                                True, True,
                                False, False]
            widget.textEditJarFile.setText(' '.join(executable.jarFile()))
            widget.textEditJarClass.setText(' '.join(executable.jarClass()))
            widget.textEditStaticArgs.setText(' '.join(executable.staticArgs()))
            pass
        elif executableType == 'Hadoop Streaming':
            # turn off unnecessary widgets
            # turn on necessary widgets
            visibilityValues = [False, False,
                                False,
                                False, False,
                                False, False,
                                False, False]
            pass
        elif executableType == 'Hadoop Pipes':
            # turn off unnecessary widgets
            # turn on necessary widgets

            visibilityValues = [True, True,
                                False,
                                False, False,
                                False, False,
                                False, False]
            widget.textEditExecutablePath.setText(os.path.sep.join(executable.pipesFile()))
            pass
        elif executableType == 'Python Eval':
            visibilityValues = [True, True,
                                False,
                                False, False,
                                False, False,
                                False, False]
            delimiter = '.'
            if not all([len(x) for x in executable.path()]):
                delimiter = ''
            labelValues[widget.labelExecutablePath] = "Module/Function path"
            widget.textEditExecutablePath.setText(delimiter.join(executable.path()))
            pass

        childWidgets = [widget.labelExecutablePath,
                        widget.textEditExecutablePath,
                        widget.checkBoxStageable,
                        widget.labelJarFile,
                        widget.textEditJarFile,
                        widget.labelJarClass,
                        widget.textEditJarClass,
                        widget.labelStaticArgs,
                        widget.textEditStaticArgs]
        for visibilityValue, childWidget in zip(visibilityValues,
                                                childWidgets):
            childWidget.setVisible(visibilityValue)
            pass

        for childWidget, labelText in labelValues.iteritems():
            childWidget.setText(labelText)

        if not self.shouldAllowEdit():
            widget.textEditExecutablePath.setReadOnly(True)
            widget.checkBoxStageable.setEnabled(False)
            widget.textEditJarFile.setReadOnly(True)
            widget.textEditJarClass.setReadOnly(True)
            widget.textEditStaticArgs.setReadOnly(True)

        return


    def getParametersToDisplay(self):
        definition = self.definition()
        parametersTable = definition.parametersTable()
        filter = RelationalModule.ColumnValueFilter(
            'parameter',
            FilterModule.ObjectKeyMatchesFilter(
                filter = FilterModule.EquivalenceFilter(ParameterModule.PORT_TYPE_DATA),
                keyFunction=lambda x: x.portType()
            )
        )
        parameters = RelationalModule.Table.reduceRetrieve(
            parametersTable,
            filter,
            ['parameter'],
            []
        )

        # sort the parameters according to ordering
        parameters = ParameterModule.sortParameters(
            parameters, definition.parameterOrderingTable())
        return parameters


    def populateParameters(self):

        widget = self.widget()
        contextManager = self.contextManager()
        pomsetContext = self.pomsetContext()
        definition = self.definition()

        tableParameters = widget.tableParameters
        while tableParameters.rowCount():
            tableParameters.removeRow(0)

        tableParameters.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        tableParameters.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        tableParameters.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)

        tableParameters.setDragDropOverwriteMode(False)
        if self.shouldAllowEdit():
            tableParameters.setDragDropMode(QtGui.QAbstractItemView.DragDrop)
        tableParameters.setColumnWidth(0, 200)
        tableParameters.setColumnWidth(1, 120)


        parameters = self.getParametersToDisplay()


        tableParameters.setRowCount(len(parameters))
        for rowIndex, parameter in enumerate(parameters):
            name = parameter.id() or ''
            item = QtGui.QTableWidgetItem('name')
            item.setData(Qt.UserRole, parameter)
            item.setData(Qt.DisplayRole, name)
            tableParameters.setItem(rowIndex, 0, item)

            direction = parameter.portDirection()
            if parameter.getAttribute(ParameterModule.PORT_ATTRIBUTE_ISSIDEEFFECT):
                direction = 'output'
            item = QtGui.QTableWidgetItem('direction')
            item.setData(Qt.UserRole, parameter)
            item.setData(Qt.DisplayRole, direction)
            tableParameters.setItem(rowIndex, 1, item)
            pass


        if self.shouldAllowEdit():
            builder = contextManager.pomsetBuilder()
            reorderParametersFunction = functools.partial(
                reorderParameters,
                controller=self)

            tableParameters.dropEvent = functools.partial(
                dropEvent,
                function=reorderParametersFunction,
                table=tableParameters)

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

    @pyqtSlot(QModelIndex)
    def on_tableParameters_doubleClicked(self, index):

        parameter = index.data(Qt.UserRole).toPyObject()
        self.displayParameter(parameter)

        return


    @pyqtSlot(str)
    def on_comboBoxExecutableType_currentIndexChanged(self, value):
        try:
            self.updateGuiForEditingExecutableType(value)
        except TypeError, e:
            logging.debug('error on updating gui >> %s' % e)
        return

    @pyqtSlot()
    def on_buttonAdd_clicked(self):

        if not self.shouldAllowEdit():
            return

        contextManager = self.contextManager()
        pomsetContext = self.pomsetContext()
        definition = self.definition()
        widget = self.widget()

        name = '_'.join(['parameter', uuid.uuid4().hex[:3]])

        builder = contextManager.pomsetBuilder()

        attributes = {
            'direction':ParameterModule.PORT_DIRECTION_INPUT
            }

        builder.addPomsetParameter(definition, name, attributes)

        # TODO:
        # find the last parameter in the list
        # add parameter ordering
        tableParameters = widget.tableParameters
        index = tableParameters.rowCount() - 1
        if index >= 0:
            sourceParameter = \
                tableParameters.item(index, 0).data(Qt.UserRole).toPyObject()

            builder.addParameterOrdering(definition, sourceParameter.id(), name)
            pass

        self.populateParameters()

        return


    @pyqtSlot()
    def on_buttonEdit_clicked(self):
        contextManager = self.contextManager()

        tableParameters = self.widget().tableParameters
        parameters = list(set([x.data(Qt.UserRole).toPyObject() 
                               for x in tableParameters.selectedItems()]))

        if len(parameters) is 0:
            return
        # no need to verify that only one was selected
        # because we've already specified that 
        # as a property of the table

        parameterToEdit = parameters[0]

        self.displayParameter(parameterToEdit)

        return


    def displayParameter(self, parameter):

        contextManager = self.contextManager()


        controller = None
        ui = None

        executableType = str(self.widget().comboBoxExecutableType.currentText())
        if executableType == 'Python Eval':
            # import the modules
            import pomsets_app.gui.qt.edit_python_parameter.widget as WidgetModule
            import pomsets_app.gui.qt.edit_python_parameter.controller as ControllerModule

            # initialize the widget and controller
            controller = ControllerModule.Controller(self)
            ui = WidgetModule.Ui_Dialog()
            pass
        else:

            # import the modules
            import pomsets_app.gui.qt.edit_parameter.widget as WidgetModule
            import pomsets_app.gui.qt.edit_parameter.controller as ControllerModule

            # initialize the widget and controller
            controller = ControllerModule.Controller(self)
            ui = WidgetModule.Ui_Dialog()
            pass
        
        controller.shouldAllowEdit(self.shouldAllowEdit())
        controller.contextManager(contextManager)
        controller.pomsetContext(self.pomsetContext())
        controller.parameter(parameter)
        controller.definition(self.definition())

        ui.setupUi(controller)

        controller.widget(ui)

        # populate the dialog
        controller.populate()

        QObject.connect(contextManager.mainWindow(), 
                        SIGNAL("OnPomsetModified(PyQt_PyObject)"),
                        self.populateParameters)

        controller.show()

        return

    @pyqtSlot()
    def on_buttonRemove_clicked(self):

        if not self.shouldAllowEdit():
            return

        contextManager = self.contextManager()
        builder = contextManager.pomsetBuilder()
        pomsetContext = self.pomsetContext()
        pomset = self.definition()

        tableParameters = self.widget().tableParameters
        parametersToRemove = list(
            set([x.data(Qt.UserRole).toPyObject() 
                 for x in tableParameters.selectedItems()]))

        if len(parametersToRemove):

            # clear the parameter orderings
            pomset.parameterOrderingTable().clear()

            # remove the parameter
            for parameter in parametersToRemove:
                builder.removePomsetParameter(pomset, parameter.id())
                pass

            # now recreate the parameter orderings
            # use the existing ordering in the table
            parameters = self.getDisplayedParameters()

            # because the table still contains references
            # to the parameters that we've removed
            # we need to remove them
            # so that we do not re-add removed parameter orderings
            idsOfParametersToRemove = [x.id() for x in parametersToRemove]
            parameters = [x for x in parameters 
                          if not x.id() in idsOfParametersToRemove]

            self.constructTotalOrder(pomset, parameters)

            self.populateParameters()
            contextManager.mainWindow().emit(
                SIGNAL("OnPomsetModified(PyQt_PyObject)"), pomsetContext)

            pass

        return


    def saveValues(self):

        widget = self.widget()
        contextManager = self.contextManager()
        pomsetContext = self.pomsetContext()
        definition = self.definition()
        
        hasBeenModified = False
        
        name = str(widget.textEditName.text())
        if not name == definition.name():
            definition.name(name)
            hasBeenModified = True

        description = str(widget.textEditDescription.text())
        if not description == definition.description():
            definition.description(description)
            hasBeenModified = True


        executableType = str(widget.comboBoxExecutableType.currentText())
        executable = definition.executable()
        currentExecutableType = contextManager.getTypeForExecutable(executable)
        if not executableType == currentExecutableType:
            executableClass = contextManager.getClassForExecutableType(executableType)
            executable = executableClass()
            definition.executable(executable)
            hasBeenModified = True
            
        if executableType == 'Shell':
            executablePath = str(widget.textEditExecutablePath.text()).split(os.path.sep)
            if not executablePath == executable.path():
                executable.path(executablePath)
                hasBeenModified = True

            isStageable = widget.checkBoxStageable.isChecked()
            if not executable.stageable() == isStageable:
                executable.stageable(isStageable)
                hasBeenModified = True

            staticArgs = str(widget.textEditStaticArgs.text()).split(' ')
            if not executable.staticArgs() == staticArgs:
                executable.staticArgs(staticArgs)
                hasBeenModified = True

        elif executableType == 'Hadoop Jar':

            jarFile = str(widget.textEditJarFile.text()).split(' ')
            if not executable.jarFile() == jarFile:
                executable.jarFile(jarFile)
                hasBeenModified = True

            jarClass = str(widget.textEditJarClass.text()).split(' ')
            if not executable.jarClass() == jarClass:
                executable.jarClass(jarClass)
                hasBeenModified = True
            pass

        elif executableType == 'Hadoop Streaming':
            executable.jarFile([contextManager.getHadoopStreamingJar()])
            executable.jarClass([])
            pass

        elif executableType == 'Hadoop Pipes':

            pipesFile = str(widget.textEditExecutablePath.text()).split(os.path.sep)
            if not executable.pipesFile() == pipesFile:
                executable.pipesFile(pipesFile)
                hasBeenModified = True
            pass
        elif executableType == 'Python Eval':
            executablePath = str(widget.textEditExecutablePath.text())
            if len(executablePath) > 0:
                executablePath = executablePath.rsplit('.', 1)
                if len(executablePath) == 1:
                    executablePath.insert(0, '')
            else:
                executablePath = ['', '']
            if not executablePath == executable.path():
                executable.path(executablePath)
                hasBeenModified = True

        if self.shouldReconstructParameterOrdering():
            hasBeenModified = True
            parameters = self.getDisplayedParameters()
            self.constructTotalOrder(definition, parameters)
            pass

        if hasBeenModified:

            pomsetContext.isModified(True)
            
            contextManager.mainWindow().emit(
                SIGNAL("OnPomsetModified(PyQt_PyObject)"), pomsetContext)
        return

    def getDisplayedParameters(self):
        tableParameters = self.widget().tableParameters
        parameters = [tableParameters.item(x, 0).data(Qt.UserRole).toPyObject()
                      for x in range(tableParameters.rowCount())]
        return parameters


    def constructTotalOrder(self, pomset, parameters):

        contextManager = self.contextManager()
        builder = contextManager.pomsetBuilder()

        for sourceParameter, targetParameter in zip(
            parameters[:-1], parameters[1:]):

            builder.addParameterOrdering(
                pomset, sourceParameter.id(), targetParameter.id())
            pass
        return


    # END class Controller
    pass
