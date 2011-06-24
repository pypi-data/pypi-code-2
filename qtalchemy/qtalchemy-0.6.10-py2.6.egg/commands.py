# -*- coding: utf-8 -*-
##############################################################################
#       Copyright (C) 2010, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
##############################################################################
"""
Attach command descriptions and short-cut keys to python functions.  These 
command sets can be converted into QMenu and QToolbar objects.  Additionally, 
one can fill QDialogButtonBox classes.  Facilities are included for classifying 
and sorting the commands for global application consistency.
"""

import weakref
from PyQtHelpers import *
from PyQt4 import QtCore, QtGui

if QtCore.__name__.startswith("PySide"):
    Signal = QtCore.Signal
else:
    Signal = QtCore.pyqtSignal

class Command(object):
    """
    This is a decorator for entity methods to mark them as methods that should be included 
    in the GUI command set in places with this entity.  This enables automatic generation of 
    button boxes and tool-bars.

    See :class:`BoundCommandMenu` for more details.
    """
    def __init__(self, descr, default=False, requireSelection=True, needs_reload=True, key=None, statusTip=None, iconFile=None, type="action", sort=500):
        """
        :param descr: Text description of command for menu items
        :param default: Default command for item activation.
        :param requireSelection: Set to false if the command function makes sense with-out a current object
        :param needs_reload: Set to false if the command does not modify the database in a way that would require refreshing the screen.
        :param key: shortcut key as given by QtCore.Qt.Key enumeration
        :param type: classifies the command for menu structure - new/view/action/delete are common options with special meanings to the sort algorithm
        """
        self.descr = descr
        self.requireSelection = requireSelection
        self.default = default
        self.needs_reload = needs_reload
        self.iconFile = iconFile
        self.key = key
        self.statusTip = statusTip
        self.command_type = type
        self.sort = sort
        self.func = None

    def __call__(self, func):
        func._command_me = self
        func.descr = self.descr
        self.func = func
        return func

    def action(self, parent):
        action = QtGui.QAction(self.descr, parent)
        if self.key is not None:
            action.setShortcut(self.key)
        if self.statusTip is not None:
            action.setStatusTip(parent.tr(self.statusTip))
        if self.iconFile is not None:
            action.setIcon(QtGui.QIcon(self.iconFile))
        return action

    def sort_key(self):
        assert 0<=self.sort<1000, "We expect you to sort between 0 and 999 inclusive"
        action_map = {"new": 2, "view": 4, "action": 6, "delete": 8}
        try:
            actInt = action_map[self.command_type]
        except KeyError, e:
            actInt = 5
        return "{0:01f}{1:03f}".format(actInt, self.sort)

class CommandMenu(object):
    """
    The CommandMenu class defines a list of menu commands which can be incorporated 
    into menus or toolbars associated with some UI object.  Multiple CommandMenu 
    objects can be associated with a single class.  This enables modularity in 
    the menu structure.
    
    The principle interaction with CommandMenu is a method decorator 
    :func:`command` to add a command to the menu.  Additional decorators 
    are :func:`itemNew`, :func:`itemAction` and :func:`itemDelete` which 
    are useful with the :func:`BoundCommandMenu.withView`.
    """
    def __init__(self, name):
        self.commands = []
        self.name = name

    def command(self, descr, key=None, statusTip=None, type="action", iconFile=None, sort=500, default=False, requireSelection=False, needs_reload=True):
        """
        :param descr:  string that appears in the menu (or other UI element)
        :param key: short-cut key to apply to this command
        :param type:  a string value typically chosen from "new", "action", "delete"; 
            This is used to sort the menu.
        :param sort:  integer from 0 to 1000 used to fine-tune the sort after the 'type'

        A function decorated with itemNew must have one parameter:
        
        #.  command object (probably self)
        """
        def decorator(f):
            x = Command(descr, 
                key=key, 
                type=type, 
                statusTip=statusTip, 
                iconFile=iconFile, 
                sort=sort, 
                default=default, 
                requireSelection=requireSelection, 
                needs_reload=needs_reload)
            x.func = f
            self.commands.append(x)
            self.commands.sort(key=lambda x:x.sort_key())
            return f
        return decorator

    def itemNew(self, **kwargs):
        """
        A function decorator similar to :func:`command` but with parameters 
        defaulted appropriate for adding an item to an adjacent view.
        
        A function decorated with itemNew must have two parameters:
        
        #.  command object (probably self)
        #.  identifier or object acted on.  This should have a default of 
            None if requireSelection is not specified in itemNew.
        """
        if not kwargs.has_key("descr"):
            kwargs["descr"] = "&New..."
        if not kwargs.has_key("iconFile"):
            kwargs["iconFile"] = ":/qtalchemy/default-new.ico"
        if not kwargs.has_key("requireSelection"):
            kwargs["requireSelection"] = False
        kwargs["type"] = "new"
        return self.command(**kwargs)

    def itemDelete(self, **kwargs):
        """
        A function decorator similar to :func:`command` but with parameters 
        defaulted appropriate for deleting an item in an adjacent view.
        
        A function decorated with itemNew must have two parameters:
        
        #.  command object (probably self)
        #.  identifier or object acted on.  This should have a default of 
            None if requireSelection is not specified in itemNew.
        """
        if not kwargs.has_key("descr"):
            kwargs["descr"] = "&Delete..."
        if not kwargs.has_key("requireSelection"):
            kwargs["requireSelection"] = True
        if not kwargs.has_key("iconFile"):
            kwargs["iconFile"] = ":/qtalchemy/default-delete.ico"
        kwargs["type"] = "delete"
        return self.command(**kwargs)

    def itemAction(self, descr, **kwargs):
        """
        A function decorator similar to :func:`command` but with parameters 
        defaulted appropriate for deleting an item in an adjacent view.
        
        A function decorated with itemNew must have two parameters:
        
        #.  command object (probably self)
        #.  identifier or object acted on.  This should have a default of 
            None if requireSelection is not specified in itemNew.
        """
        if not kwargs.has_key("requireSelection"):
            kwargs["requireSelection"] = True
        kwargs["type"] = "action"
        return self.command(descr, **kwargs)

    def __get__(self, instance, owner):
        try:
            return getattr(instance, self.name)
        except AttributeError as e:
            setattr(instance, self.name, BoundCommandMenu(instance, self))
            return getattr(instance, self.name)

class DomainEntity(CommandMenu):
    """
    DomainEntity is deprecated, but still used by the ForeignKey lookup stuff

    The DomainEntity object defines how an object appears and can be manipulated by the user.  This has 
    several components::
    
    * Defining database queries to provide user view of lists of these domain entities.
    * Key field information to map back to individual tables.
    * Commands acting on a record in the principle table (identified by primary key).
    
    QtAlchemy takes the view that rows of database queries do not map well to typical object oriented 
    design methods.  The DomainEntity provides a more abstract view of commands associated to an entity which 
    can be bound to arbitrary database queries with-in the code.  Thus a joined query can actually offer user 
    commands associated with any of the tables in the query.
    """

    def __init__(self, info={}):
        """
        The following assignments are a common proto-type associating this DomainEntity with a 
        explicit table.  We do not yet define the sql joins clearly.
        """
        CommandMenu.__init__(self,"base_menu")
        self.key_column = None
        self.list_display_columns = None
        self.list_search_columns = None
        self.info = info

    def list_query_converter(self):
        from sqlalchemy.orm import Query
        queryCols = tuple([self.key_column.label("_hidden_id")] + self.list_display_columns)
        return (Query(queryCols).order_by(self.list_display_columns[0], self.key_column), lambda x: x._hidden_id)

class BoundCommandMenuItem(object):
    """
    The class :class:`BoundCommandMenu` is responsible for creating and managing instances of this class.
    
    This class binds comamnds from an entity to a PyQt/PySide view where each row represents an 
    entity to the entity class.  The proxy slots 'activatedProxy' and 'triggeredProxy' redirect 
    to the specified function of the entity instance.
    """
    def __init__(self, cmd, action, objectConverter, binding):
        """
        :param cmd:  a :class:`Command` object
        :param action:  A QAction or QPushButton
        :param objectConverter:  A callable taking row objects (QModelIndex.internalPointer()) to id's for the entity functions.
            If objectConverter is None, then use the default model objectConverter.
        """
        self.cmd = cmd
        self.action = action
        self.objectConverter = objectConverter
        self.binding = binding

        if binding.view is not None:
            self.model = binding.view.model()
            self.item_sel = binding.view.selectionModel()

            # hook to QItemSelectionModel::selectionChanged signal for enabling/disabling
            # hook to QAbstractItemModel::modelReset signal for enabling/disabling
            self.item_sel.selectionChanged.connect(self.enable_buttons)
            self.model.modelReset.connect(self.enable_buttons)

        if isinstance(self.action, QtGui.QPushButton):
            self.action.clicked.connect(self.triggeredProxy)
        elif isinstance(self.action, QtGui.QAction):
            self.action.triggered.connect(self.triggeredProxy)

    def enable_buttons(self, sel=None, desel=None):
        # setEnabled is sufficient for both QPushButton and QAction
        if self.cmd.requireSelection:
            indexes = self.binding.view.selectedIndexes()
            self.action.setEnabled(len(indexes)>0)

    def activatedProxy(self, index):
        if self.cmd.requireSelection and index is None:
            print "none selected"
        else:
            if index is None:
                self.cmd.func(self.binding.target)
            else:
                objectConverter = self.model.objectConverter if self.objectConverter is None else self.objectConverter
                self.cmd.func(self.binding.target, objectConverter(index.internalPointer()))
            if self.cmd.needs_reload:
                self.binding.refresh.emit()
                if self.binding.view:
                    self.model.reset_content_from_session()

    def triggeredProxy(self, checked=False):
        index = None
        if self.binding.view is not None:
            indexes = self.binding.view.selectedIndexes()
            index = None if len(indexes)==0 else indexes[0]
        self.activatedProxy(index)


class BoundCommandMenu(QtCore.QObject):
    """
    This class holds the :class:`BoundCommandMenuItem` objects binding an entity to a view.  This is 
    the main class for tying :class:`CommandMenu` instances to PyQt/PySide views.
    
    Primarily the work of this class is carried out in the :class:`BoundCommandMenuItem` objects which holds 
    slots connected to signals from the view.  This class also attaches the actions to the view.
    
    Note that if the view is a :class:`qtalchemy.widgets.TableView`, the 
    default context menu policy of :class:`qtalchemy.widgets.TableView` is 
    QtCore.Qt.ActionsContextMenu.
    """
    preCommand = Signal(name='preCommand')
    refresh = Signal(name='refresh')

    def __init__(self, target, menu, view=None, buttonBox=None, bindDefault=False, objectConverter=None):
        QtCore.QObject.__init__(self)
        self.target = target
        self.menu = menu
        self.view = view
        self.buttonBox = buttonBox
        self.bindDefault = bindDefault
        self.objectConverter = objectConverter
        
        if self.view:
            # we need to hook up to the context menu immediately
            self.resetActions()

    def withView(self, view, buttonBox=None, bindDefault=False, objectConverter=None):
        """
        Return a duplicate of this BoundMenuCommand augmented with a view.  The 
        QAction objects will enable and disable as appropriate for the connected view.
        
        :param view: a QAbstractItemView attached to a QAbstractItemModel
        """
        return BoundCommandMenu(self.target, self.menu, view, buttonBox=buttonBox, bindDefault=bindDefault, objectConverter=objectConverter)

    def resetActions(self):
        """
        Regenerate QAction objects from self.target
        """
        self.action_bindings = [] # this is annoying -- I need to hold a reference explicitly
        self.button_bindings = []
        self.default_binding = None
        for cmd in self.menu.commands:
            action = cmd.action(self.view if self.view is not None else self.target)
            current = BoundCommandMenuItem(cmd, action, objectConverter = self.objectConverter, binding = weakref.proxy(self))
            self.action_bindings.append(current)
            if cmd.default:
                self.default_binding = current

            if self.buttonBox is not None:
                #TODO:  map Command.type to QtGui.QDialogButtonBox.*Role items
                button = self.buttonBox.addButton(cmd.descr, QtGui.QDialogButtonBox.ActionRole)
                self.button_bindings.append(BoundCommandMenuItem(cmd, button, objectConverter = self.objectConverter, binding = weakref.proxy(self)))

        if self.default_binding and self.bindDefault:
            self.view.activated.connect(self.default_binding.activatedProxy)

        if self.view is not None:
            for cb in self.action_bindings:
                self.view.addAction(cb.action)

    def fillMenu(self, menu):
        """
        Take the actions in the list and attach them to a menu.
        """
        if not hasattr(self, "action_bindings"):
            self.resetActions()
        for command in self.action_bindings:
            menu.addAction(command.action)

    def fillToolbar(self, toolbar):
        """
        Take the actions in the list and attach them to a toolbar.
        """
        if not hasattr(self, "action_bindings"):
            self.resetActions()
        for command in self.action_bindings:
            toolbar.addAction(command.action)

    def __len__(self):
        return len(self.menu.commands)

    def __getitem__(self, index):
        return self.menu.commands[index]
