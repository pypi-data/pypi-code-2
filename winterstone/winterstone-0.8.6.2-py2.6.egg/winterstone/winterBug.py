# -*- coding: utf-8 -*-
from datetime import datetime
import re
import inspect
from PySide.QtGui import QLineEdit
from snowflake import *

from config import Config
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from extraQt import WinterEditor, WinterLine


class try_this(object):
    '''
        decorator for wrap method in try-except and post exception to API
    '''

    def __init__(self, api):
        self.api = api

    def __call__(self, func):
        def wrapped_f(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception, e:
                self.api.error(e)

        return wrapped_f


class WinterQtDebug(QDockWidget):
    '''
        Debug dockwidget class
    '''
    class WinterDebugLine(WinterLine):
        '''
            Editline for execution methods
        '''

        def __init__(self, parent):
            WinterLine.__init__(self)
            self.app = parent.app
            self.parent = parent

            complete_methods = []
            for i in dir(self.parent.app):
                if not i.startswith('_') and type(getattr(self.parent.app, i)).__name__ == 'instancemethod':
                    complete_methods.append(i)
            for i in dir(self.parent.app.core):
                if not i.startswith('_') and type(getattr(self.parent.app.core, i)).__name__ == 'instancemethod':
                    complete_methods.append('core.' + i)
            if self.parent.app.config.options.plugins:
                for plugin in self.parent.app.pm.plugins:
                    try:
                        if plugin.name in self.parent.app.p_config.plugins.active:
                            for i in dir(plugin):
                                if not i.startswith('_') and type(getattr(plugin, i)).__name__ == 'instancemethod':
                                    complete_methods.append('%s.%s' % (plugin.name, i))
                    except:
                        pass
            self.setComplete(complete_methods)
            if not self.parent.config.options.popup_completion:
                self.lineEditCompleter.setCompletionMode(QCompleter.InlineCompletion)
            else:
                self.lineEditCompleter.setCompletionMode(QCompleter.PopupCompletion)


        def checkLine(self):
            '''
                Check line for highlighting
                by getMethod from app
            '''
            line = re.findall('[^ ]*', str(self.text()))
            ln = line[0]
            module = re.findall('([^ ]*)\.', str(self.text()))
            if module:
                module = module[0]
                ln = ln.replace(module + '.', '')
            else:
                module = 'main'
            return self.app.getMethod(ln, module)


        def _command(self):
            '''
                Execute method
            '''
            if not self.dlock:
                line = re.findall('[^ ]*', str(self.text()))
                ln = line[0]
                module = re.findall('([^ ]*)\.', str(self.text()))
                if module:
                    module = module[0]
                    ln = ln.replace(module + '.', '')
                    print module, ln
                else:
                    module = 'main'
                args = line[1:]
                for arg in args:
                    if not arg:
                        args.remove(arg)
                try:
                    self.app.getMethod(ln, module=module)(*args)
                    self.hist_a.append(str(self.text()))
                    self.hist_a = list(set(self.hist_a))
                    self.clear()
                except Exception, e:
                    self.parent.error(str(e))

    class WinterErrorList(QListWidget):
        '''
            List of exceptions. Undone
        '''

        def __init__(self, parent):
            QListWidget.__init__(self)
            self.parent = parent

        def addItem(self, item, *args, **kwargs):
            '''
                Add exception item to list
            '''
            QListWidget.addItem(self, item)
            button = self.addItemButton(item, 'help', self.parent.inspectE)

        def addItemButton(self, item, icon, method):
            '''
                Add button to listitem
            '''
            widget = QWidget(self)
            button = QPushButton(QIcon(self.parent.api.icons[icon]), '')
            button.setBaseSize(QSize(14, 14))
            button.setIconSize(QSize(14, 14))
            button.method = method
            button.item = item
            button.clicked.connect(self.sig_map)
            horizbox = QHBoxLayout(widget)
            horizbox.addSpacerItem(QSpacerItem(self.width(), 0))
            widget.setLayout(horizbox)
            horizbox.insertWidget(1, button)
            return button

        def sig_map(self):
            '''
                I forgot, why its need
            '''
            try:
                self.sender().method(self.sender().item)
            except AttributeError:
                self.sender().method()

    def __init__(self, app):
        QDockWidget.__init__(self)
        self.setObjectName('debug')
        cfgfile = file('%sconfig/debug.cfg' % CWD)
        self.config = Config(cfgfile)
        self.exceptions = []
        self.app = app
        self.api = app.api
        widget = QTabWidget()
        log = QWidget()
        todo = WinterEditor(self.app, CWD + 'TODO', lexer='Plain')
        self.errorList = self.WinterErrorList(self)
        widget.addTab(log, 'Log')
        widget.addTab(self.errorList, 'Errors')
        widget.addTab(todo, 'ToDo')
        layout = QVBoxLayout(log)
        self.debugLine = self.WinterDebugLine(self)
        self.debugList = QListWidget()
        layout.addWidget(self.debugLine)
        layout.addWidget(self.debugList)
        log.setLayout(layout)
        self.setWidget(widget)

        self.app.addDockWidget(Qt.BottomDockWidgetArea, self)
        self.hide()

    def inspectE(self, *args, **kwargs):
        '''
            Exception inspection
        '''
        self.app.dialog('warning', 'Error', str(self.sender().item.e))


    def makeMessage(self, msg, color='', icon='', bold=True, fgcolor='', timestamp=False):
        '''
            Return listitem with nize attrs
        '''
        if timestamp:
            timestamp = datetime.now().strftime('%H:%M:%S')
            item = QListWidgetItem('[%s] %s' % (timestamp, msg))
        else:
            item = QListWidgetItem(msg)
        if color:
            item.setBackground(QColor(color))
        if 'item_font' in self.config.options:
            font = QFont(self.config.options['item_font'])
        else:
            font = QFont('Sans')
        font.setBold(bold)
        font.setPointSize(int(self.config.options['font_size']))
        item.setFont(font)
        item.setTextColor(QColor(fgcolor))
        if icon:
            item.setIcon(QIcon(self.api.icons[icon]))
        return item

    def info(self, msg):
        '''
            Add info message to list
        '''
        self.debugList.addItem(self.makeMessage(msg, self.config.options.info_bg_color, 'ok', timestamp=True,
                                                fgcolor=self.config.options.info_fg_color))

    def error(self, msg, obj=''):
        '''
            Add error message to list
        '''
        if not isinstance(msg, Exception):
            exc = Exception(msg)
        else:
            exc = msg
        self.exceptions.append(exc)
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        vmsg = '%s\nMethod: %s; locals: %s' % (exc, calframe[2][3], calframe[2][0].f_locals)
        if not obj:
            item = self.makeMessage(vmsg, self.config.options.error_bg_color, 'error', timestamp=True,
                                    fgcolor=self.config.options.error_fg_color)
            item2 = self.makeMessage(msg, self.config.options.error_bg_color, 'error', timestamp=True,
                                     fgcolor=self.config.options.error_fg_color) #in qt you cant copy widget=((
        else:
            item = self.makeMessage('%s::%s' % (obj, vmsg), self.config.options.erorr_bg_color, 'error', timestamp=True,
                                    fgcolor=self.config.options.error_fg_color)
            item2 = self.makeMessage('%s::%s' % (obj, msg), self.config.options.error_bg_color, 'error', timestamp=True,
                                     fgcolor=self.config.options.error_fg_color)
        item.e = exc
        self.errorList.addItem(item)
        self.debugList.addItem(item2)

    def debug(self, msg):
        '''
            Add debug message to list
        '''
        self.debugList.addItem(self.makeMessage(msg, self.config.options.debug_bg_color, 'warning', timestamp=True,
                                                fgcolor=self.config.options.debug_fg_color))
