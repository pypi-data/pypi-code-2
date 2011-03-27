#!/usr/bin/python

from . import daemon
from . import copy_to_clipboard, generate_password
import pygtk
pygtk.require('2.0')
import gtk
import gobject
import signal

class GtkGui(object):
    def __init__(self, daemon):
        self.daemon = daemon

        self.window=gtk.Window(gtk.WINDOW_TOPLEVEL)

        self.window.set_title("PetaPass")
        self.window.set_border_width(20)
        self.window.set_resizable(False)
        self.window.set_position(gtk.WIN_POS_CENTER)
        # XXX can't get focus grabbing to work correctly, sigh
        #self.window.set_property('skip-taskbar-hint', True)
        self.window.set_property('skip-pager-hint', True)
        self.window.set_property('focus-on-map', True)
        # XXX if undecorated, present() works inconsistently.
        #self.window.set_property('decorated', False)

        accel_group = gtk.AccelGroup()
        self.window.add_accel_group(accel_group)
        self.window.connect('key_press_event', self.key_press_event)

        signal.signal(signal.SIGUSR1, self.sig_usr1)
        signal.signal(signal.SIGUSR2, self.sig_usr2)
        signal.signal(signal.SIGTERM, self.sig_term)

        table = gtk.Table(3, 5, False)
        self.window.add(table)
        table.show()

        ## Password ##
        label = gtk.Label('Master')
        label.set_alignment(1, 0)
        label.show()
        table.attach(label, 0, 1, 0, 1, gtk.EXPAND, gtk.EXPAND, 3, 3)

        self.master = gtk.Entry()
        self.master.set_visibility(False)
        self.master.set_width_chars(40)
        self.master.show()
        table.attach(self.master, 1, 5, 0, 1, gtk.EXPAND, gtk.EXPAND, 3, 3)

        ### Token ##
        label = gtk.Label('Token')
        label.set_alignment(1, 0)
        label.show()
        table.attach(label, 0, 1, 1, 2, gtk.EXPAND, gtk.EXPAND, 3, 3)

        self.token = gtk.Entry()
        self.token.set_width_chars(40)
        self.token.set_activates_default(True)
        self.token.show()
        table.attach(self.token, 1, 5, 1, 2, gtk.EXPAND, gtk.EXPAND, 3, 3)

        # hitting enter on the master focuses token
        self.master.connect_object('activate', gtk.Widget.grab_focus, self.token)

        ### Buttons ##
        ok = gtk.Button(stock=gtk.STOCK_OK)
        ok.set_flags(gtk.CAN_DEFAULT)
        ok.connect("clicked", self.ok_clicked, None)
        ok.show()
        table.attach(ok, 1, 2, 2, 3, gtk.EXPAND, gtk.EXPAND, 3, 3)
        ok.grab_default()

        cancel = gtk.Button(stock=gtk.STOCK_CANCEL)
        cancel.connect("clicked", self.cancel_clicked, None)
        cancel.show()
        table.attach(cancel, 2, 3, 2, 3, gtk.EXPAND, gtk.EXPAND, 3, 3)
        # escape key closes window
        cancel.add_accelerator("clicked", accel_group, gtk.keysyms.Escape, 0, gtk.ACCEL_LOCKED)

        forget = gtk.Button("_Forget")
        forget.connect("clicked", self.forget_clicked, None)
        forget.show()
        table.attach(forget, 3, 4, 2, 3, gtk.EXPAND, gtk.EXPAND, 3, 3)

        self.show_master = gtk.CheckButton("_Show Master")
        self.show_master.connect("toggled", self.show_master_toggled, None)
        self.show_master.show()
        table.attach(self.show_master, 4, 5, 2, 3, gtk.EXPAND, gtk.EXPAND, 3, 3)

    def key_press_event(self, widget, event):
        # quit on ctrl-q
        keyname = gtk.gdk.keyval_name(event.keyval)
        if event.state & gtk.gdk.CONTROL_MASK and keyname == 'q':
            gtk.main_quit()

    def show_master_toggled(self, widget, data=None):
        if widget.get_active():
            self.master.set_visibility(True)
        else:
            self.master.set_visibility(False)

    def cancel_clicked(self, widget, data=None):
        self.master.set_text("")
        self.window.hide()

    def ok_clicked(self, widget, data=None):
        master = self.master.get_text()
        token = self.token.get_text()
        self.master.set_text("")
        self.token.set_text("")
        self.window.hide()

        self.daemon.set(master)
        copy_to_clipboard(generate_password(master, token))

    def forget_clicked(self, widget, data=None):
        self.master.set_text("")
        self.daemon.forget()
        self.master.grab_focus()

    def sig_usr1(self, sig, frame):
        # get master & raise window
        master = self.daemon.get()
        if master is not None:
            self.master.set_text(master)
            self.token.grab_focus()
        else:
            self.master.grab_focus()

        self.window.present()

    def sig_usr2(self, sig, frame):
        self.daemon.forget()

    def sig_term(self, sig, frame):
        gtk.main_quit()

    def main(self):
        gobject.threads_init()
        gtk.main()