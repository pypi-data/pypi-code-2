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

    def __init__(self, *args, **kwds):
        QtGui.QDialog.__init__(self, *args, **kwds)
        QtModule.Controller.__init__(self)

        return

    def populate(self):

        widget = self.widget()
        contextManager = self.contextManager()

        definition = self.definition()

        widget.textEditName.setText(definition.name() or '')
        widget.textEditComment.setText(definition.comment() or '')


        widget.checkBoxCritical.setChecked(definition.isCritical())

        QObject.connect(contextManager.mainWindow(),
                        SIGNAL("OnPomsetModified(PyQt_PyObject)"),
                        self.populateParameters)
        self.populateParameters()

        return


    def populateParameters(self):

        widget = self.widget()
        contextManager = self.contextManager()
        pomsetContext = self.pomsetContext()
        definition = self.definition()

        tableParameters = widget.tableParameters
        while tableParameters.rowCount():
            tableParameters.removeRow(0)

        tableParameters.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        tableParameters.setColumnWidth(0, 125)
        tableParameters.setColumnWidth(1, 75)
        tableParameters.setColumnWidth(2, 75)
        tableParameters.setColumnWidth(3, 175)

        filter = FilterModule.ObjectKeyMatchesFilter(
            filter=FilterModule.EquivalenceFilter(ParameterModule.PORT_TYPE_DATA),
            keyFunction = lambda x: x.portType()
            )
        parameters = definition.getParametersByFilter(filter)
        
        tableParameters.setRowCount(len(parameters))

        for rowIndex, parameter in enumerate(parameters):
            name = parameter.id() or ''
            item = QtGui.QTableWidgetItem('name')
            item.setData(Qt.UserRole, parameter)
            item.setData(Qt.DisplayRole, name)
            tableParameters.setItem(rowIndex, 0, item)

            stagingRequired = definition.parameterStagingRequired(name)
            item = QtGui.QTableWidgetItem('staging')
            item.setData(Qt.DisplayRole, stagingRequired)
            item.setData(Qt.UserRole, parameter)
            tableParameters.setItem(rowIndex, 1, item)

            isParameterSweep = definition.isParameterSweep(name)
            item = QtGui.QTableWidgetItem('sweep')
            item.setData(Qt.DisplayRole, isParameterSweep)
            item.setData(Qt.UserRole, parameter)
            tableParameters.setItem(rowIndex, 2, item)

            group = definition.getGroupForParameterSweep(name)
            item = QtGui.QTableWidgetItem('sweep group')
            item.setData(Qt.DisplayRole, str(group))
            item.setData(Qt.UserRole, parameter)
            tableParameters.setItem(rowIndex, 3, item)
            
            pass

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


    @pyqtSlot(QModelIndex)
    def on_tableParameters_doubleClicked(self, index):

        parameter = index.data(Qt.UserRole).toPyObject()
        self.editParameterBinding(parameter)

        return

    def editParameterBinding(self, parameter):
        contextManager = self.contextManager()

        # import the modules
        import pomsets_app.gui.qt.edit_parameter_binding.widget as WidgetModule
        import pomsets_app.gui.qt.edit_parameter_binding.controller as ControllerModule

        # initialize the widget
        controller = ControllerModule.Controller(self)
        controller.contextManager(contextManager)
        controller.pomsetContext(self.pomsetContext())
        controller.definition(self.definition())
        controller.parameter(parameter)

        ui = WidgetModule.Ui_Dialog()
        ui.setupUi(controller)

        controller.widget(ui)

        # populate the dialog
        controller.populate()

        controller.show()
        return controller


    @pyqtSlot()
    def on_buttonToggleStaging_clicked(self):

        widget = self.widget()
        tableParameters = widget.tableParameters

        selectedItems = tableParameters.selectedItems()
        if len(selectedItems) is 0:
            return

        # selectedItem = selectedItems[0]
        parameterIds = set([])
        for selectedItem in selectedItems:
            parameter = selectedItem.data(Qt.UserRole).toPyObject()
            parameterId = parameter.id()
            parameterIds.add(parameterId)

        for parameterId in parameterIds:
            stagingRequired = not self.definition().parameterStagingRequired(parameterId)
            self.definition().parameterStagingRequired(
                parameterId, stagingRequired)
            pass

        self.populateParameters()

        return


    @pyqtSlot()
    def on_buttonChangeGroup_clicked(self):

        widget = self.widget()
        tableParameters = widget.tableParameters

        selectedItems = tableParameters.selectedItems()
        if len(selectedItems) is 0:
            return

        selectedItem = selectedItems[0]
        parameter = selectedItem.data(Qt.UserRole).toPyObject()
        self.editParameterSweepGroup(parameter)

        return


    def editParameterSweepGroup(self, parameter):

        contextManager = self.contextManager()

        # import the modules
        import pomsets_app.gui.qt.edit_parameter_sweep_group.widget as WidgetModule
        import pomsets_app.gui.qt.edit_parameter_sweep_group.controller as ControllerModule

        # initialize the widget
        controller = ControllerModule.Controller(self)
        controller.contextManager(contextManager)
        controller.pomsetContext(self.pomsetContext())
        controller.definition(self.definition())
        controller.parameter(parameter)

        ui = WidgetModule.Ui_Dialog()
        ui.setupUi(controller)

        controller.widget(ui)

        # populate the dialog
        controller.populate()

        controller.show()
        return controller


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

        comment = str(widget.textEditComment.text())
        if not comment == definition.comment():
            definition.comment(comment)
            hasBeenModified = True

        isCritical = widget.checkBoxCritical.isChecked()
        if not definition.isCritical() == isCritical:
            definition.isCritical(isCritical)
            hasBeenModified = True

        if hasBeenModified:
            pomsetContext.isModified(True)
            contextManager.mainWindow().emit(
                SIGNAL("OnPomsetModified(PyQt_PyObject)"), pomsetContext)
            pass

        return


    # END class Controller
    pass
