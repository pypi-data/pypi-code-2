#!/usr/bin/python3

from PyQt4.QtCore import (QAbstractItemModel, QModelIndex, Qt,
                          QCoreApplication, SIGNAL)
from PyQt4.QtGui import (QIcon, QVBoxLayout, QWidget, QLabel, QGroupBox,
                         QGridLayout, QPushButton, QHBoxLayout)

from fathom.schema import Trigger

_ = lambda string: QCoreApplication.translate('', string)


class DetailsWidget(QWidget):
    
    def addTitle(self, name):
        label = QLabel('<h2>' + name + '</h2>')
        self.layout().addWidget(label)
        

class TableDetailsWidget(DetailsWidget):
    
    def __init__(self, table, parent=None):
        QWidget.__init__(self, parent)
        self._table = table
        
        self.setLayout(QVBoxLayout())
        self.addTitle(table.name)
        self.addColumns()
        self.addForeignKeys()
        self.layout().addStretch()

    def addColumns(self):
        box = QGroupBox(self.tr('Columns'))
        layout = QGridLayout()
        layout.addWidget(QLabel(self.tr('<b>Name</b>')), 0, 0)
        layout.addWidget(QLabel(self.tr('<b>Type</b>')), 0, 1)
        layout.addWidget(QLabel(self.tr('<b>Not null</b>')), 0, 2)
        layout.addWidget(QLabel(self.tr('<b>Default</b>')), 0, 3)
        for index, column in enumerate(self._table.columns.values()):
            layout.addWidget(QLabel(column.name), index + 1, 0)
            layout.addWidget(QLabel(column.type), index + 1, 1)
            layout.addWidget(QLabel(str(column.not_null)), index + 1, 2)
            layout.addWidget(QLabel(column.default), index + 1, 3)
        box.setLayout(layout)
        self.layout().addWidget(box)
        
    def addForeignKeys(self):
        if self._table.foreign_keys:
            box = QGroupBox(self.tr('Foreign keys'))
            layout = QGridLayout()
            layout.addWidget(QLabel(self.tr('<b>Columns</b>')), 0, 0)
            layout.addWidget(QLabel(self.tr('<b>Referenced table</b>')), 0, 1)
            layout.addWidget(QLabel(self.tr('<b>Referenced columns</b>')), 0, 2)
            for index, fk in enumerate(self._table.foreign_keys):
                layout.addWidget(QLabel(', '.join(fk.columns)), index + 1, 0)
                layout.addWidget(QLabel(fk.referenced_table), index + 1, 1)
                layout.addWidget(QLabel(', '.join(fk.referenced_columns)), 
                                        index + 1, 2)
                button = QPushButton('Open table')
                button.table = fk.referenced_table
                self.connect(button, SIGNAL('pressed()'), self.openTable)
                layout.addWidget(button, index + 1, 3)
            box.setLayout(layout)
            self.layout().addWidget(box)
        else:
            self.layout().addWidget(QLabel('No foreign keys defined.'))
    
    def openTable(self):
        try:
            table = self._table.database.tables[self.sender().table]
        except KeyError:
            args = (self, 'Table not found',
                    "Table was not found in the database nad can't be opened.")
            QMessageBox.critical(*args)
        self.emit(SIGNAL('openElement'), table, table.name, 
                  TableDetailsWidget(table))


class ViewDetailsWidget(DetailsWidget):
    
    def __init__(self, view, parent=None):
        QWidget.__init__(self, parent)
        self._view = view
        
        self.setLayout(QVBoxLayout())
        self.addTitle(view.name)
        self.addColumns()
        self.layout().addStretch()

    def addColumns(self):
        box = QGroupBox(self.tr('Columns'))
        layout = QGridLayout()
        layout.addWidget(QLabel(self.tr('<b>Name</b>')), 0, 0)
        layout.addWidget(QLabel(self.tr('<b>Type</b>')), 0, 1)
        layout.addWidget(QLabel(self.tr('<b>Not null</b>')), 0, 2)
        layout.addWidget(QLabel(self.tr('<b>Default</b>')), 0, 3)
        for index, column in enumerate(self._view.columns.values()):
            layout.addWidget(QLabel(column.name), index + 1, 0)
            layout.addWidget(QLabel(column.type), index + 1, 1)
            layout.addWidget(QLabel(str(column.not_null)), index + 1, 2)
            layout.addWidget(QLabel(column.default), index + 1, 3)
        box.setLayout(layout)
        self.layout().addWidget(box)
        

class TriggerDetailsWidget(DetailsWidget):
    
    WHEN_NAMES = {Trigger.BEFORE: 'BEFORE', Trigger.AFTER: 'AFTER', 
                  Trigger.INSTEAD: 'INSTEAD'}
    EVENT_NAMES = {Trigger.UPDATE: 'UPDATE', Trigger.BEFORE: 'BEFORE',
                   Trigger.DELETE: 'DELETE'}
    
    def __init__(self, trigger, parent=None):
        QWidget.__init__(self, parent)
        self._trigger = trigger
        
        self.setLayout(QVBoxLayout())
        self.addTitle(trigger.name)
        self.addInformation()
        self.layout().addStretch()
        
    def addInformation(self):
        layout = QGridLayout()
        layout.addWidget(QLabel(self.tr('<b>Table:</b>')), 0, 0)
        layout.addWidget(QLabel(self._trigger.table), 0, 1)
        layout.addWidget(QLabel(self.tr('<b>When:</b>'),), 1, 0)
        layout.addWidget(QLabel(self.WHEN_NAMES[self._trigger.when] + ' ' +
                                self.EVENT_NAMES[self._trigger.event]), 1, 1)
        self.layout().addLayout(layout)
        

class ProcedureDetailsWidget(DetailsWidget):
    
    def __init__(self, procedure, parent=None):
        QWidget.__init__(self, parent)
        self._procedure = procedure
        
        self.setLayout(QVBoxLayout())
        self.addTitle(procedure.name)
        self.addReturns()
        self.addArguments()
        self.layout().addStretch()
    
    def addReturns(self):
        returns = self._procedure.returns or 'void'
        label = QLabel(self.tr('<b>Returns:</b> ') + returns)
        self.layout().addWidget(label)
        
    def addArguments(self):
        if self._procedure.arguments:
            box = QGroupBox(self.tr('Arguments:'))
            layout = QGridLayout()
            layout.addWidget(QLabel(self.tr('<b>Name</b>')), 0, 0)
            layout.addWidget(QLabel(self.tr('<b>Type</b>')), 0, 1)
            arguments = self._procedure.arguments.values()
            for index, argument in enumerate(arguments):
                layout.addWidget(QLabel(argument.name), index + 1, 0)
                layout.addWidget(QLabel(argument.type), index + 1, 1)
            box.setLayout(layout)
            self.layout().addWidget(box)
        else:
            label = QLabel(self.tr("Arguments: none."))
            self.layout().addWidget(label)


class IndexDetailsWidget(DetailsWidget):
    
    def __init__(self, index, parent=None):
        QWidget.__init__(self, parent)
        self._index = index
        
        self.setLayout(QVBoxLayout())
        self.addTitle(index.name)
        self.addTable()
        self.addColumns()
        self.addUniqueness()
        self.layout().addStretch()
        
    def addTable(self):
        layout = QHBoxLayout()
        label = QLabel('<b>Indexed table:</b> ' + self._index.table)
        button = QPushButton('Open table')
        button.table = self._index.table
        self.connect(button, SIGNAL('pressed()'), self.openTable)
        layout.addWidget(label)
        layout.addWidget(button)
        self.layout().addLayout(layout)

    def addColumns(self):
        label = QLabel('<b>Columns:</b> ' + ', '.join(self._index.columns))
        self.layout().addWidget(label)
        
    def addUniqueness(self):
        label = QLabel('<b>Unique:</b> ' + ('Yes' if self._index.is_unique 
                                                 else 'No'))
        self.layout().addWidget(label)

    def openTable(self):
        try:
            table = self._index.database.tables[self.sender().table]
        except KeyError:
            args = (self, 'Table not found',
                    "Table was not found in the database nad can't be opened.")
            QMessageBox.critical(*args)
        self.emit(SIGNAL('openElement'), table, table.name, 
                  TableDetailsWidget(table))


class Item:
    
    def __init__(self, obj, parent, row):
        self._parent = parent
        self._row = row
        self._obj = obj
        
    def object(self):
        return self._obj

    def childrenCount(self):
        return 0
        
    def row(self):
        return self._row
        
    def parent(self):
        return self._parent
    
    def removable(self):
        return False
        
    def isOpenable(self):
        return True
        
    def name(self):
        return self.object().name
        
    def tabName(self):
        return self.name()
        
    def createWidget(self):
        return self.DetailsWidget(self._obj)
        

class TableItem(Item):
    DetailsWidget = TableDetailsWidget
        

class ViewItem(Item):
    DetailsWidget = ViewDetailsWidget
    
            
class TriggerItem(Item):
    DetailsWidget = TriggerDetailsWidget
        

class IndexItem(Item):
    DetailsWidget = IndexDetailsWidget


class ProcedureItem(Item):
    DetailsWidget = ProcedureDetailsWidget


class ListItem(Item):
    
    def __init__(self, obj, parent, row):
        Item.__init__(self, obj, parent, row)
        self._children = [self.ChildItem(child, self, row)
                          for row, child in enumerate(obj)]
    
    def child(self, index):
        return self._children[index]
    
    def childrenCount(self):
        return len(self._obj)
        
    def isOpenable(self):
        return False
        
    def name(self):
        return self._name
    
    def tabName(self):
        assert False, 'tabName should not be called on list items!'


class DatabaseItem(Item):
    
    def __init__(self, db, row):
        Item.__init__(self, db, None, row)
        self.children = [TableListItem(list(db.tables.values()), self, 0), 
                         ViewListItem(list(db.views.values()), self, 1),
                         TriggerListItem(list(db.triggers.values()), self, 2),
                         IndexListItem(list(db.indices.values()), self, 3)]
        if db.supports_stored_procedures():
            item = ProceduresListItem(list(db.procedures.values()), self, 3)
            self.children.append(item)

    def childrenCount(self):
        return len(self.children)
        
    def child(self, row):
        return self.children[row]
                         
    def removable(self):
        return True


class TableListItem(ListItem):
    ChildItem = TableItem
    _name = _('Tables')
            
    def name(self):
        return _('Tables')
        

class ViewListItem(ListItem):
    ChildItem = ViewItem
    _name = _('Views')
                        
    def name(self):
        return _('Views')
        

class IndexListItem(ListItem):
    ChildItem = IndexItem
    _name = _('Indices')
        
            
class TriggerListItem(ListItem):
    ChildItem = TriggerItem
    _name = _('Triggers')
    
        
class ProceduresListItem(ListItem):
    ChildItem = ProcedureItem
    _name = _('Procedures')
    

class FathomModel(QAbstractItemModel):
    
    def __init__(self, parent=None):
        QAbstractItemModel.__init__(self, parent)
        self._databases = []
        
    def addDatabase(self, database):
        count = len(self._databases)
        self.beginInsertRows(QModelIndex(), count, count + 1)
        self._databases.append(DatabaseItem(database, count))
        self.endInsertRows()
        
    def removeDatabase(self, database):
        index = self._databases.index(database)
        assert index > -1, 'Database to be removed not found!'
        self.beginRemoveRows(QModelIndex(), index, index + 1)
        self._databases.pop(index)
        self.endRemoveRows()
        
    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        if parent.isValid():
            parent = parent.internalPointer()
            if parent.childrenCount() > row:
                return self.createIndex(row, column, parent.child(row))
            else:
                return QModelIndex()
        if len(self._databases) > row:
            return self.createIndex(row, column, self._databases[row])
        else:
            return QModelIndex()
            
    def parent(self, index):
        if not index.isValid() or index.internalPointer().parent() is None:
            return QModelIndex()
        parent = index.internalPointer().parent()
        return self.createIndex(parent.row(), 0, parent)
            
    def rowCount(self, parent):
        if not parent.isValid():
            return len(self._databases)
        else:
            return parent.internalPointer().childrenCount()
            
    def columnCount(self, parent):
        return 1
            
    def data(self, index, role):
        if index.isValid() and role in (Qt.DisplayRole, Qt.DecorationRole):
            if role == Qt.DisplayRole:
                return index.internalPointer().name()
            if role == Qt.DecorationRole:
                return QIcon('icons/database.png')
        return None
