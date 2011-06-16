#!/usr/bin/python3

from sys import argv
from os.path import join

from PyQt4.QtCore import (QDir, SIGNAL, Qt, QAbstractItemModel, QModelIndex,
                          QVariant, QCoreApplication, QEvent, QSettings, QPoint,
                          QSize)
from PyQt4.QtGui import (QDialog, QHBoxLayout, QWidget, QLabel, QStackedWidget,
                         QRadioButton, QLineEdit, QTreeView, QGridLayout,
                         QVBoxLayout, QPushButton, QFileSystemModel, QIcon,
                         QApplication, QTreeView, QMainWindow, QAction,
                         QTabWidget, QMenu, QToolBar, QTableWidget, QLineEdit,
                         QTableWidgetItem, QGroupBox, QGridLayout, QCursor,
                         QMessageBox)

from fathom import (get_sqlite3_database, get_postgresql_database, 
                    get_mysql_database, get_oracle_database, TYPE_TO_FUNCTION)
from fathom.schema import Database, Trigger
from fathom import FathomError

from .model import FathomModel

_ = lambda string: QCoreApplication.translate('', string)

class QClickableTabWidget(QTabWidget):

    def __init__(self, allowEmpty=True, parent=None):
        QTabWidget.__init__(self, parent)
        self._allowEmpty = allowEmpty
        self.installEventFilter(self)
        
    def eventFilter(self, target, event):
        if event.type() != QEvent.MouseButtonPress:
            return QTabWidget.eventFilter(self, target, event)
        position = event.pos()
        tab = -1
        for index in range(self.tabBar().count()):
            if self.tabBar().tabRect(index).contains(position):
                tab = index
                break
        if tab == -1:
            return QTabWidget.eventFilter(self, target, event)
        if event.button() == Qt.RightButton:
            menu = QMenu()
            actions = ((self.tr('Close'), 'triggered()', self.close),
                       (self.tr('Close other'), 'triggered()', self.closeOther))
            for title, signal, slot in actions:
                action = QAction(title, self)
                self.connect(action, SIGNAL(signal), slot)
                menu.addAction(action)
            self.selection = index
            menu.exec(event.globalPos())
            self.selection = None
            return True

    def close(self):
        if not self._allowEmpty and self.tabBar().count() == 1:
            return
        self.removeTab(self.selection)
        
    def closeOther(self):
        for i in range(self.selection):
            self.removeTab(0)
        while self.tabBar().count() > 1:
            self.removeTab(1)


class QConnectionDialog(QDialog):
    
    '''
    General dialog for gathering information database connection.
    '''
    
    class PostgresWidget(QWidget):
        
        PARAMS = (("Host:", "host"), ("Port:", "port"),
                  ("Database name:", "databaseName"), 
                  ("User name:", "userName"), ("Password:", "password")) 
        
        def __init__(self, parent=None):
            QWidget.__init__(self, parent)
            
            grid = QGridLayout()            
            for index, (label, field) in enumerate(self.PARAMS):
                label = QLabel(self.tr(label))
                grid.addWidget(label, index, 0, Qt.AlignLeft | Qt.AlignTop)            
                setattr(self, field, QLineEdit())
                grid.addWidget(getattr(self, field), index, 1)

            self.setLayout(QVBoxLayout())
            self.layout().addLayout(grid)
            self.layout().addStretch()

        def validate(self):
            return bool(self.databaseName.text())
                
        def getDatabaseParams(self):
            result = []
            for label, field in (('dbname', self.databaseName),
                                 ('user', self.userName)):
                if field.text():
                    result.append('%s=%s' % (label, field.text()))
            return 'PostgreSQL', (' '.join(result),)


    class SqliteWidget(QWidget):
        
        def __init__(self, parent=None):
            QWidget.__init__(self, parent)
            
            self.model = QFileSystemModel()
            self.model.setRootPath('/')

            # preparing tree view displaying file system
            self.view = QTreeView(parent=self);
            self.view.setModel(self.model)
            for i in range(1, 4):
                self.view.header().hideSection(i)
            self.view.header().hide()
            self.connect(self.view, 
                         SIGNAL('doubleClicked(const QModelIndex &)'),
                         self.quickChoice)

            # expanding tree view to show current working directory
            path = QDir.currentPath().split('/')
            fullPath = ''
            for step in path:
                fullPath += step + '/'
                index = self.model.index(fullPath)
                if index.isValid():
                    self.view.setExpanded(index, True)
                else:
                    break
            
            self.setLayout(QVBoxLayout())
            self.layout().addWidget(self.view)
            
        def quickChoice(self):
            self.emit(SIGNAL('quickChoice'))
            
        def validate(self):
            index = self.view.currentIndex()
            return bool(index.isValid()) and not self.model.isDir(index)
            
        def getDatabaseParams(self):
            index = self.view.currentIndex()
            result = []
            while index.isValid():
                result.append(index.data())
                index = index.parent()
            result.reverse()
            return 'Sqlite3', (join(*result),)
            
    
    class MySqlWidget(QWidget):

        PARAMS = (("Host:", "host"), ("Port:", "port"),
                  ("Database name:", "db"), 
                  ("User name:", "user"), ("Password:", "passwd")) 
        
        def __init__(self, parent=None):
            QWidget.__init__(self, parent)
            
            grid = QGridLayout()            
            for index, (label, field) in enumerate(self.PARAMS):
                label = QLabel(self.tr(label))
                grid.addWidget(label, index, 0, Qt.AlignLeft | Qt.AlignTop)            
                setattr(self, field, QLineEdit())
                grid.addWidget(getattr(self, field), index, 1)

            self.setLayout(QVBoxLayout())
            self.layout().addLayout(grid)
            self.layout().addStretch()

        def validate(self):
            return bool(self.db.text())
                
        def getDatabaseParams(self):
            params = {}
            for _, field in self.PARAMS:
                if getattr(self, field).text():
                    params[field] = getattr(self, field).text()
            return 'MySQL', (), params

    
    class OracleWidget(QWidget):

        PARAMS = (("User:", "user", True), ("Password:", "password", True), 
                  ("DSN:", "dsn", False))
        
        def __init__(self, parent=None):
            QWidget.__init__(self, parent)
            
            grid = QGridLayout()
            for index, (label, field, _) in enumerate(self.PARAMS):
                label = QLabel(self.tr(label))
                grid.addWidget(label, index, 0, Qt.AlignLeft | Qt.AlignTop)            
                setattr(self, field, QLineEdit())
                grid.addWidget(getattr(self, field), index, 1)

            self.setLayout(QVBoxLayout())
            self.layout().addLayout(grid)
            self.layout().addStretch()

        def validate(self):
            return all([bool(getattr(self, field).text()) 
                        for _, field, required in self.PARAMS if required])
                        
        def getDatabaseParams(self):
            values = (field for _, field in self.PARAMS 
                            if getattr(self, field).text())
            values = (getattr(self, field).text() for field in values)
            return 'Oracle', tuple(values)

    def __init__(self, parent=None):
        QDialog.__init__(self)

        # preparing whole layout of dialog
        mainLayout = QVBoxLayout()
        widgetsLayout = QHBoxLayout()
        buttonsLayout = QHBoxLayout()
        radioLayout = QVBoxLayout()
        mainLayout.addLayout(widgetsLayout)
        mainLayout.addLayout(buttonsLayout)
        widgetsLayout.addLayout(radioLayout)
        
        # preparing radio buttons for choosing DBMS type
        radioLayout.addWidget(QLabel(self.tr("Database type:")))
        options = (('postgres', 'PostgreSQL', 'postgresChosen'), 
                   ('sqlite', 'sqlite3', 'sqliteChosen'),
                   ('oracle', 'Oracle', 'oracleChosen'),
                   ('mysql', 'MySQL', 'mysqlChosen'))
        for field, label, method in options:
            button = QRadioButton(self.tr(label), self)
            radioLayout.addWidget(button)
            self.connect(button, SIGNAL('pressed()'), getattr(self, method))
            setattr(self, field, button)
        radioLayout.addStretch()
        self.postgres.toggle()
        
        # preparing stack widgets for database connection details
        self.stackedWidget = QStackedWidget()
        self.stackedWidget.addWidget(self.PostgresWidget())
        sqliteWidget = self.SqliteWidget()
        self.stackedWidget.addWidget(sqliteWidget)
        self.stackedWidget.addWidget(self.OracleWidget())
        self.stackedWidget.addWidget(self.MySqlWidget())
        widgetsLayout.addWidget(self.stackedWidget)

        # preparing ok and cancel buttons at the bottom
        buttonsLayout.addStretch()
        for label, method in ('OK', self.accept), ('Cancel', self.reject):
            button = QPushButton(self.tr(label))
            self.connect(button, SIGNAL('pressed()'), method)
            buttonsLayout.addWidget(button)
        self.connect(sqliteWidget, SIGNAL('quickChoice'), self.accept)
        
        self.setLayout(mainLayout)
        self.resize(600, 400)
        
    def postgresChosen(self):
        self.stackedWidget.setCurrentIndex(0);
        
    def sqliteChosen(self):
        self.stackedWidget.setCurrentIndex(1);
    
    def oracleChosen(self):
        self.stackedWidget.setCurrentIndex(2);
        
    def mysqlChosen(self):
        self.stackedWidget.setCurrentIndex(3);
        
    def accept(self):
        if self.stackedWidget.currentWidget().validate():
            return QDialog.accept(self)
                        
    def getDatabaseParams(self):
        return self.stackedWidget.currentWidget().getDatabaseParams()


class MainWidget(QWidget):
    
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setLayout(QHBoxLayout())
        layout = QVBoxLayout()

        # attributes which hold connections between fathom objects and gui
        # elements
        self._params = {}
        self._tabs = {}
        self._databaseTabs = {}

        # creating button for adding connections
        button = QPushButton(self.tr('Add connection..'))
        button.setIcon(QIcon('icons/add_database.png'))
        
        # creating view for displaying connections
        view = QTreeView()
        view.setFixedWidth(400)
        view.header().hide()
        view.setExpandsOnDoubleClick(False)
        self.model = FathomModel()
        view.setModel(self.model)
        
        # creating widget for displaying inspected objects
        self.display = QClickableTabWidget()

        # merging it all together
        layout.addWidget(button)
        layout.addWidget(view)
        self.layout().addLayout(layout)
        self.layout().addWidget(self.display)
        
        # connecting to signals
        self.connect(button, SIGNAL('pressed()'), self.addConnection)
        self.connect(view, SIGNAL('doubleClicked(const QModelIndex &)'),
                     self.openElementFromTree)
        self.connect(view, SIGNAL('pressed(const QModelIndex &)'),
                     self.editElement)
        
        # filling connections view with stored connections
        self.loadConnections()
    
    def openElement(self, element, name, widget):
        self.connect(widget, SIGNAL('openElement'), self.openElement)
        try:
            tab = self._tabs[element]
        except KeyError:
            tab = self.display.addTab(widget, name)
            self._tabs[element] = tab
        self.display.setCurrentIndex(tab)
            
    def openElementFromTree(self, index=None):
        if index is None:
            index = self.sender().index
        pointer = index.internalPointer()
        if pointer.isOpenable():
            widget = pointer.createWidget()
            self.openElement(pointer.object(), pointer.tabName(), widget)
                            
    def editElement(self, index):
        if QApplication.mouseButtons() == Qt.RightButton:
            menu = QMenu()
            action = QAction('Open', self)
            action.index = index
            self.connect(action, SIGNAL('triggered()'), 
                         self.openElementFromTree)
            menu.addAction(action)
            if index.internalPointer().removable():
                action = QAction('Remove', self)
                action.index = index
                self.connect(action, SIGNAL('triggered()'), self.removeElement)
                menu.addAction(action)
            menu.exec(QCursor.pos())
            
    def removeElement(self):
        item = self.sender().index.internalPointer()
        self.model.removeDatabase(item)
        db = item.object()
        self.cleanTabs(db)
        settings = QSettings('gruszczy@gmail.com', 'qfathom')
        databases = settings.value('databases', [])
        index = databases.index(self._params[db])
        if index != -1:
            databases = databases[:index] + databases[index + 1:]
        settings.setValue('databases', databases)

    def loadConnections(self):
        settings = QSettings('gruszczy@gmail.com', 'qfathom')
        databases = settings.value('databases', [])
        for params in databases:
            try:
                db = self.connectDatabase(params)
                self.model.addDatabase(db)
            except FathomError:
                pass # warn at the end
        
    def addConnection(self):
        dialog = QConnectionDialog()
        if dialog.exec() == QDialog.Accepted:
            params = dialog.getDatabaseParams()
            try:
                db = self.connectDatabase(params)
                self.model.addDatabase(db)
            except FathomError as e:
                args = (self, 'Failed to connect to database',
                        'Failed to connect to database: %s' % str(e))
                QMessageBox.critical(*args)
            else:
                settings = QSettings('gruszczy@gmail.com', 'qfathom')
                databases = settings.value('databases', [])
                databases.append(params)
                settings.setValue('databases', databases)
            
    def connectDatabase(self, params):
        assert len(params) >= 2, 'Not enough params to connect to database!'
        function = TYPE_TO_FUNCTION[params[0]]
        dictionary = params[2] if len(params) > 2 else {}
        db = function(*params[1], **dictionary)
        self._params[db] = params
        return db
    
    def cleanTabs(self, db):
        indices = (self._tabs[obj] for obj in self._tabs
                                   if obj.database == db)
        indices = reversed(sorted(indices))
        for index in indices:
            self.display.removeTab(index)


class MainWindow(QMainWindow):
    
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent=parent)
        self.setWindowIcon(QIcon('icons/database.png'))
        self.setWindowTitle('QFathom')
        self.setCentralWidget(MainWidget())

        settings = QSettings('gruszczy@gmail.com', 'qfathom')
        geometry = settings.value('main-window/geometry', None)
        if geometry is not None:
            self.restoreGeometry(geometry)

    def closeEvent(self, event):
        settings = QSettings("gruszczy@gmail.com", "qfathom")
        settings.setValue("main-window/geometry", self.saveGeometry())
