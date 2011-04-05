# -*- coding: utf-8 -*-

# Helm
# view.py

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

import array
import time

import cairo
import gobject
import gtk
from PIL import Image
from Xlib import display, Xatom
from Xlib.X import ZPixmap
from Xlib.xobject.drawable import Pixmap

AllPlanes = 2 ** 32 - 1 # from /usr/include/X11/Xlib.h


class View(gtk.DrawingArea):
    __gsignals__ = {'expose-event': 'override'}

    def __init__(self):
        gtk.DrawingArea.__init__(self)

        self.display = display.Display()
        self.screen = self.display.screen()
        self.root = self.screen.root
        self._XROOTPMAP_ID = self.display.intern_atom("_XROOTPMAP_ID")
        self.ESETROOT_PMAP_ID = self.display.intern_atom("ESETROOT_PMAP_ID")

        self.background = None
        self.width = 0

        gobject.timeout_add(1000, self.redraw_cb, True)
        gobject.timeout_add(1000, self.update_cb, True)

    def init(self, width, height=None):
        self.width = width
        if height is None:
            height = width
        self.height = height
        self.set_size_request(width, height)

    def init_background(self):
        # get XID
        pmap = self.root.get_full_property(self._XROOTPMAP_ID, Xatom.PIXMAP)
        if not pmap:
            pmap = self.root.get_full_property(self.ESETROOT_PMAP_ID,
                                               Xatom.PIXMAP)

        # get x-pixmap
        pix = Pixmap(self.display.display, pmap.value[0])

        # get some informations
        geom = pix.get_geometry()
        x, y = self.window.get_origin()
        width, height = self.window.get_size()

        # x-pixmap -> array
        data = pix.get_image(x, y, width, height, ZPixmap, AllPlanes).data
        image = Image.fromstring('RGB', (width, height),
                                 data, 'raw', 'BGRX')
        image_string = image.tostring()
        image_array = array.array('c', chr(0) * (len(image_string) * 4 / 3))
        for i, c in enumerate(image_string):
            image_array[(2 - (i % 3)) + 4 * (i / 3)] = c

        # array -> cairo.ImageSurface
        img_surf = cairo.ImageSurface.create_for_data(image_array,
                                                      cairo.FORMAT_RGB24,
                                                      width, height)
        self.background = img_surf

    def redraw_cb(self, redo=False, *args, **kwds):
        gobject.idle_add(self.redraw_after)
        return redo

    def redraw_after(self):
        self.emit('expose-event', None)

    def update_cb(self, *args, **kwds):
        gobject.idle_add(self.update_after)
        return True

    def update_after(self):
        self.update()

    def do_configure_event(self, *args, **kwds):
        self.background = None
        self.redraw_cb()

    def do_expose_event(self, *args, **kwds):
        width, height = self.window.get_size()
        pixmap = gtk.gdk.Pixmap(self.window, width, height)
        cr = pixmap.cairo_create()
        self.draw_background(cr)
        self.draw(cr, width, height)

        gc = self.window.new_gc()
        self.window.draw_drawable(gc, pixmap, 0, 0, 0, 0, width, height)

    def draw_background(self, cr):
        if self.background is None:
            self.init_background()
        width, height = self.window.get_size()
        cr.set_source_surface(self.background)
        cr.rectangle(0, 0, width, height)
        cr.fill()

    def draw(self, cr, width, height):
        cr.set_source_rgb(0.5, 0.5, 0.5)
        cr.rectangle(0, 0, width, height)
        cr.fill()
