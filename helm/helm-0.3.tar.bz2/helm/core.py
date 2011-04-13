# -*- coding: utf-8 -*-

# Helm
# core.py

# Copyright (C) 2011 Anaël Verrier <elghinn@free.fr>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 only.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gtk
from gtk.gdk import CONTROL_MASK, keyval_name


def on_key_press(widget, event):
    if (event.state & CONTROL_MASK) == CONTROL_MASK:
        if keyval_name(event.keyval) == 'q':
            gtk.main_quit()


def run(width, *widgets):
    window = gtk.Window()
    window.set_decorated(False)
    window.set_has_frame(False)

    window.set_skip_taskbar_hint(True)
    window.set_skip_pager_hint(True)
    # window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DOCK)
    window.set_keep_below(True)

    window.set_title('Helm')
    window.connect('delete-event', gtk.main_quit)
    window.connect('key-press-event', on_key_press)

    vbox = gtk.VBox()
    for widget in widgets:
        if not widget.valid:
            continue
        vbox.pack_start(widget)
        widget.init(width)
        window.connect('configure-event', widget.do_configure_event)
    window.add(vbox)
    window.show_all()
    window.present()
    window.stick()
    window.set_resizable(False)
    gtk.main()
