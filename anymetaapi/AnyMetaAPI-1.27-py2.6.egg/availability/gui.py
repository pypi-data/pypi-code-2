# Copyright (c) 2009 Mediamatic Lab
# See LICENSE for details.

"""
Graphical user interface for availability service.
"""


import gtk, base

class AvailabilityWidget (gtk.VBox):
    """
    A widget which represents the state of the L{AvailabilityService}
    it connects to.

    It consists of a series of rows, for each component a row with the
    component's caption and an icon representing its state.

    Below that is a text area which shows help texts for every
    component that is not in the"OK" state.
    """

    stock_map = { base.OK: "gtk-apply",
                  base.NOTICE: "gtk-about",
                  base.WARNING: "gtk-dialog-warning",
                  base.ERROR: "gtk-stop",
                  None: "gtk-about" }

    images = None


    def __init__(self, service):
        """
        Initialize the widget. In the constructor the
        L{AvailabilityService} is given as only argument.
        """
        gtk.VBox.__init__(self)
        self.service = service
        self.service.widgets.append(self)

        self.set_size_request(200, 160)
        
        self.images = {}
        self.rebuild()
        self.refresh()


    def rebuild(self):
        """
        Rebuild the widget. Call this when the number components in the L{AvailabilityService} have changed.
        """
        for c in self.get_children():
            self.remove(c)

        self.images = {}
        for c in self.service.components:            
            v = gtk.HBox()
            l = gtk.Label(c.caption)
            l.set_property("xalign", 0)
            v.pack_start(l, True, True, 10)

            im = gtk.Image()
            im.set_from_stock("gtk-missing-image", gtk.ICON_SIZE_MENU)
            v.pack_start(im, False, True, 10)

            self.pack_start(v, False, False, 10)

            self.images[c.name] = im

            self.pack_start(gtk.HSeparator(), False, True, 0)

        self.textbox = gtk.Label("fasd fasdljf asdklfj asdklfj lads")
        self.textbox.set_property("use_markup", True)
        self.textbox.set_property("xpad", 10)
        self.textbox.set_property("xalign", 0)
        self.textbox.set_property("yalign", 0)
        self.textbox.set_property("wrap", True)
        self.textbox.set_property("width_request", 160)
        
        self.pack_start(self.textbox, True, True, 10)


    def refresh(self):
        """
        Refresh the state of the widget. This is called automatically
        by the L{AvailabilityService} when a change in the
        availability has happened.
        """
        
        state = dict(self.service.getStateFull())
        for name in self.images:
            self.images[name].set_from_stock(self.stock_map[state[name]['state']], gtk.ICON_SIZE_MENU)

        txt = ""
        for name in state:
            if state[name]['state'] == base.OK:
                continue # do not add "OK" states to the explanation texts
            txt += "<b>" + state[name]['caption'] + "</b>\n"
            txt += state[name]['message'].strip()
            txt += "\n\n"
        self.textbox.set_label(txt)
