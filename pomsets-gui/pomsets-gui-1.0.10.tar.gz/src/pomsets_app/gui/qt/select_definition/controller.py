from PyQt4.QtCore import *
from PyQt4 import QtGui

import pypatterns.filter as FilterModule
import pypatterns.relational as RelationalModule

import pomsets.library as LibraryModule

import pomsets_app.gui.qt as QtModule

class Controller(QtModule.Controller, QtGui.QDialog):

    def __init__(self, *args, **kwds):
        QtGui.QDialog.__init__(self, *args, **kwds)
        QtModule.Controller.__init__(self)
        return

    def canvasPosition(self, value=None):
        if value is not None:
            self._canvasPosition = value
        if not hasattr(self, '_canvasPosition'):
            self._canvasPosition = None
        return self._canvasPosition

    def populate(self):

        widget = self.widget()
        contextManager = self.contextManager()

        persistentLibrary = contextManager.persistentLibrary()
        transientLibrary = contextManager.transientLibrary()

        treeWidgetDefinitions = widget.treeWidgetDefinitions
        treeWidgetDefinitions.setHeaderHidden(True)


        notBootstrapFilter = FilterModule.constructNotFilter()
        notBootstrapFilter.addFilter(
            LibraryModule.getBootstrapLoaderPomsetsFilter())

        for library, filter, header in [(persistentLibrary, notBootstrapFilter, 'Library definitions'),
                                        (transientLibrary, FilterModule.TRUE_FILTER, 'Loaded definitions')]:
            rootItem = QtGui.QTreeWidgetItem([header])
            rootItem.setData(0, Qt.UserRole, None)
            treeWidgetDefinitions.addTopLevelItem(rootItem)
            definitions = RelationalModule.Table.reduceRetrieve(
                library.definitionTable(), 
                filter, ['definition'], [])
            for definition in definitions:
                item = QtGui.QTreeWidgetItem([definition.name() or 'anonymous'])
                item.setData(0, Qt.UserRole, definition)
                rootItem.addChild(item)
                pass
            pass
        return


    @pyqtSlot(QtGui.QAbstractButton)
    def on_buttonBox_clicked(self, button):
        widget = self.widget()
        buttonRole = widget.buttonBox.buttonRole(button)
        if buttonRole == QtGui.QDialogButtonBox.AcceptRole:
            try:
                self.createNode()
            except ValueError, e:
                # this happens if a root item is selected

                # TODO:
                # should display an error dialog

                return
            self.accept()
            pass
        if buttonRole == QtGui.QDialogButtonBox.RejectRole:
            self.reject()
            pass
        return

    def createNode(self):

        widget = self.widget()
        treeWidgetDefinitions = widget.treeWidgetDefinitions
        
        selectedItems = treeWidgetDefinitions.selectedItems()
        data = [y for y in 
                [x.data(0, Qt.UserRole).toPyObject() for x in selectedItems]
                 if y is not None]
        if len(data) is 0:
            raise ValueError('need to select a definition to reference')
        
        name = str(widget.textEditName.text())
        if not name or not len(name):
            raise ValueError('need to specify name for new node')

        self.contextManager().mainWindow().OnCreateNode(
            self.pomsetContext(), self.pomsetReference(),
            data[0], self.canvasPosition(),
            name=name)
        
        return


    # END class Controller
    pass
