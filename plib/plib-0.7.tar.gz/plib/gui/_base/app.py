#!/usr/bin/env python
"""
Module APP -- GUI Application Classes
Sub-Package GUI.BASE of Package PLIB -- Python GUI Framework
Copyright (C) 2008-2011 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Defines the classes that form the basic GUI application framework.
"""

from plib.gui.defs import *


class PAboutDialogBase(object):
    """Base class for about dialogs.
    
    Implements mapping of standard fields in about data to methods
    of about dialog that will process the data, by hacking
    ``__getattribute__`` to substitute attribute names on the fly.
    """
    
    attrmap = {}
    
    def __init__(self, parent):
        self.mainwidget = parent
    
    def __getattribute__(self, name):
        # Monkeypatch attribute name if necessary
        attrmap = super(PAboutDialogBase, self).__getattribute__('attrmap')
        if name in attrmap:
            name = attrmap[name]
        return super(PAboutDialogBase, self).__getattribute__(name)


class PTopWindowBase(object):
    """Base class for 'top window' widgets.
    
    A top window is a 'plain' main application window; it has no
    frills like menus, toolbars, status bars, etc. built in (if
    you want those frills, use PMainWindow instead). It does have
    some basic functionality, however, using the following class
    fields:
    
    aboutdialogclass -- gives class to be used to display the 'about' dialog
    box. This class is normally set internally to PLIB and should not need
    to be overridden by the user.
    
    clientwidgetclass -- gives the class of the client widget (actually can
    be any callable with the right signature that returns a widget); if None,
    no client widget is created automatically (widgets can still be created
    manually in user code). The callable must take one argument, which will
    be the PTopWindow instance creating it.
    
    Note that all the rest of the options below can be read from a client
    widget class, so the need to set them by subclassing PTopWindow directly
    should be rare:
    
    aboutdata -- gives data for display in the 'about' dialog.
    
    prefsdata -- gives parameters for constructing the 'preferences' dialog.
    
    defaultcaption -- gives the caption if no editor object is found
    
    placement -- how the window should be sized (normal, maximized, wrapped to
    the client widget, or offset from the screen edge) and positioned on the
    screen (centered, or left to the system's default positioning)
    
    sizeoffset -- how many pixels from the edge of the screen this window
    should be sized (only used if placement indicates sizing to offset from
    screen edge)
    """
    
    clientwidgetclass = None
    aboutdialogclass = None
    abouttoolkitfunc = None
    
    aboutdata = {}
    prefsdata = None
    defaultcaption = "Top Window"
    placement = (SIZE_NONE, MOVE_NONE)
    sizeoffset = 160
    
    _clientattrs = ('aboutdata', 'prefsdata',
        'defaultcaption', 'placement', 'sizeoffset')
    
    def __init__(self, parent, cls=None):
        self.shown = False
        
        # Figure out if parent is another window or the application
        if hasattr(parent, 'app'):
            self.app = parent.app
            self._parent = parent
        elif isinstance(parent, PApplicationBase):
            self.app = parent
            self._parent = None
        else:
            # This shouldn't happen, but just in case...
            self.app = None
            self._parent = None
        
        self._set_client_class(cls)
        
        if 'icon' in self.aboutdata:
            self.set_iconfile(self.aboutdata['icon'])
        self.set_caption(self.defaultcaption)
        
        self.clientwidget = self.createclient()
        self.prefsdialog = self.createprefsdialog()
    
    def _set_client_class(self, cls):
        if cls is not None:
            self.clientwidgetclass = cls
        if self.clientwidgetclass is not None:
            cls = self.clientwidgetclass
            for attrname in self._clientattrs:
                if hasattr(cls, attrname):
                    setattr(self, attrname, getattr(cls, attrname))
                elif not hasattr(self, attrname):
                    setattr(self, attrname, None)
    
    def set_iconfile(self, iconfile):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def set_caption(self, caption):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError
    
    def createclient(self):
        """Create the client widget if its class is given."""
        
        if self.clientwidgetclass is not None:
            return self.clientwidgetclass(self)
        return None
    
    def createprefsdialog(self):
        """Create the preferences dialog if data is given."""
        
        if (self.prefsdata is not None):
            # This avoids circular imports when this module is first loaded
            from plib.gui import main as gui
            return gui.PPrefsDialog(self, *self.prefsdata)
        return None
    
    def sizetoscreen(self, maximized=False):
        """Size the window to the screen.
        
        Size the window to be sizeoffset pixels from each screen edge,
        or maximized if the parameter is True."""
        raise NotImplementedError
    
    def sizetoclient(self, clientwidth, clientheight):
        """Size the window to a client widget.
        
        Size the window to fit the given client width and height.
        """
        raise NotImplementedError
    
    def center(self):
        """Center the window in the primary screen.
        """
        raise NotImplementedError
    
    def get_clientsize(self):
        """Return tuple of (width, height) needed to wrap client.
        """
        c = self.clientwidget
        return (c.preferred_width(), c.preferred_height())
    
    def show_init(self):
        """Should always call from derived classes to ensure proper setup.
        """
        if not self.shown:
            # Do placement just before showing for first time
            size, pos = self.placement
            if size == SIZE_CLIENTWRAP:
                self.sizetoclient(*self.get_clientsize())
            elif size in (SIZE_MAXIMIZED, SIZE_OFFSET):
                self.sizetoscreen(size == SIZE_MAXIMIZED)
            if (pos == MOVE_CENTER) and (size != SIZE_MAXIMIZED):
                self.center()
            self.shown = True
    
    def about(self):
        if (self.aboutdata is not None) and \
                (self.aboutdialogclass is not None):
            
            dialog = self.aboutdialogclass(self)
            for key, item in self.aboutdata.iteritems():
                getattr(dialog, key)(item)
            dialog.display()
    
    def about_toolkit(self):
        if self.abouttoolkitfunc is not None:
            self.abouttoolkitfunc()
    
    def acceptclose(self):
        """Return False if window should not close based on current state.
        """
        return True
    
    def exit(self):
        """Placeholder for derived classes to implement.
        """
        raise NotImplementedError


class PApplicationBase(object):
    """Base class for GUI application.
    
    Automatically sizes the main widget and centers it in
    the primary screen if the widget's class flags are set
    appropriately (see PTopWindow).
    
    Descendant app classes should set the class variable
    ``mainwidgetclass`` to the appropriate class object. If this
    is the only customization you want to do, however, you do
    not need to subclass this class--just pass your main window
    class derived from ``PTopWindow`` to the ``runapp`` function;
    see that function's docstring. In fact, you can even pass a
    client widget class to ``runapp``, and it will automatically
    be wrapped in a ``PTopWindow``--or, if you set the keyword
    argument ``use_mainwindow`` to ``True``, a ``PMainWindow``.
    See the ``pyidserver-gui`` and ``scrips-edit`` example
    programs for typical usage.
    
    The only time you should need to subclass this class is to
    override ``createMainWidget`` (to alter the parameters passed
    to the main widget, or do other processing after it's created
    but before the rest of ``__init__``) or to provide other
    functionality that has to be at the application level rather
    than in the main widget (but this should be extremely rare).
    """
    
    mainwidgetclass = None
    
    def __init__(self, arglist=[], cls=None, use_mainwindow=False):
        self.arglist = arglist
        self.mainwin = None
        
        # Set up main widget class
        if self.mainwidgetclass is None:
            # Import here to avoid circular imports; note that we
            # should normally get here only if the ``cls`` parameter
            # is not None (so we have a real client class)
            from plib.gui import main as gui
            if use_mainwindow:
                self.mainwidgetclass = gui.PMainWindow
            else:
                self.mainwidgetclass = gui.PTopWindow
        
        # Set up main application class
        if cls is not None:
            # The ``cls`` parameter should be either a valid main widget
            # class (which will create its own client widget), or a valid
            # client widget class (which will be wrapped in the default
            # main widget)
            self.mainwinclass = cls
        else:
            self.mainwinclass = self.mainwidgetclass
    
    def createMainWidget(self):
        """Create the main widget and return it.
        """
        if issubclass(self.mainwinclass, PTopWindowBase):
            return self.mainwinclass(self)
        return self.mainwidgetclass(self, self.mainwinclass)
    
    def _eventloop(self):
        """Placeholder for derived classes for main event loop.
        """
        raise NotImplementedError
    
    def run(self):
        """Show the main widget and run the main event loop.
        """
        
        self.mainwin.show_init()
        self._eventloop()
    
    def process_events(self):
        """Placeholder for derived classes to pump events outside main loop.
        """
        raise NotImplementedError
    
    def before_quit(self):
        """Placeholder for derived classes to do destructor-type processing.
        """
        pass
