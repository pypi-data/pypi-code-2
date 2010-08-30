import logging

from PyQt4.QtCore import *
from PyQt4 import QtGui

import pypatterns.filter as FilterModule
import pypatterns.relational as RelationalModule

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

        self.setWindowTitle('Specify parameter sweep group for "%s"' % parameter.id())

        buttonToSelect = widget.buttonUseOwnGroup
        if not definition.parameterIsInOwnParameterSweepGroup(parameter.id()):
            buttonToSelect = widget.buttonUseOtherGroup

        buttonToSelect.setChecked(True)


        listWidget = widget.listWidget

        # first get all the parameter sweep groups
        parameterSweepGroups = list(set(
                RelationalModule.Table.reduceRetrieve(
                    definition.parameterSweepGroups(),
                    FilterModule.TRUE_FILTER, ['group'], [])))
        psgMap = {}
        for psg in parameterSweepGroups:
            for parameterId in psg:
                psgMap[parameterId] = psg

        # now get the parameters that are in their own parameter sweep groups
        parameterFilter = FilterModule.constructAndFilter()
        parameterFilter.addFilter(
            FilterModule.ObjectKeyMatchesFilter(
                filter=FilterModule.EquivalenceFilter(ParameterModule.PORT_TYPE_DATA),
                keyFunction = lambda x: x.portType()
                )
            )
        notThisParameterFilter = FilterModule.constructNotFilter()
        notThisParameterFilter.addFilter(
            FilterModule.IdentityFilter(parameter))
        parameterFilter.addFilter(notThisParameterFilter)

        allParameters = definition.getParametersByFilter(parameterFilter)
        for allParameter in allParameters:
            parameterId = allParameter.id()
            if not parameterId in psgMap:
                group = tuple([parameterId])
                psgMap[parameterId] = group
                parameterSweepGroups.append(group)

        for psg in parameterSweepGroups:
            item = QtGui.QListWidgetItem('group')
            item.setData(Qt.UserRole, psg)
            item.setData(Qt.DisplayRole, str(psg))
            listWidget.addItem(item)
            pass

        return




    @pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBox_clicked(self, button):
        widget = self.widget()
        buttonRole = widget.buttonBox.buttonRole(button)

        if buttonRole == QtGui.QDialogButtonBox.ApplyRole:
            try:
                self.saveValues()
            except Exception, e:
                self.notifyUserOfError(e)
                return
            pass
        if buttonRole == QtGui.QDialogButtonBox.AcceptRole:
            try:
                self.saveValues()
                self.accept()
            except Exception, e:
                self.notifyUserOfError(e)
                return
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
        parameterId = parameter.id()

        buttonUseOwnGroup = widget.buttonUseOwnGroup

        needToRemoveFromGroup = False
        if not definition.parameterIsInOwnParameterSweepGroup(parameterId):
            if buttonUseOwnGroup.isChecked():
                needToRemoveFromGroup = True
            else:
                if not parameterId in selectedGroup:
                    needToRemoveFromGroup = True
                pass
            pass

        buttonUseOtherGroup = widget.buttonUseOtherGroup
        needToAddToGroup = False
        if buttonUseOtherGroup.isChecked():
            listWidget = widget.listWidget
            selectedItems = list(listWidget.selectedItems())
            if len(selectedItems) == 0:
                return
            selectedItem = selectedItems[0]
            selectedGroup = tuple(
                [str(x) 
                 for x in selectedItem.data(Qt.UserRole).toPyObject()])

            if definition.parameterIsInOwnParameterSweepGroup(parameterId):
                needToAddToGroup = True
            else:
                if not parameterId in selectedGroup:
                    needToAddToGroup = True
            pass
                    

        if needToRemoveFromGroup:
            group = definition.getGroupForParameterSweep(parameterId)
            definition.removeParameterSweepGroup(group)
            newGroup = [x for x in list(group) if not x==parameterId]
            definition.addParameterSweepGroup(newGroup)

        if needToAddToGroup:
            definition.removeParameterSweepGroup(selectedGroup)
            newGroup = list(selectedGroup) + [parameterId]
            definition.addParameterSweepGroup(newGroup)
            

        if needToRemoveFromGroup or needToAddToGroup:
            pomsetContext.isModified(True)
            contextManager.mainWindow().emit(
                SIGNAL("OnPomsetModified(PyQt_PyObject)"), pomsetContext)
            pass

        return


    # END class Controller
    pass
