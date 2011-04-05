# -*- coding: utf-8 -*-

# Helm
# widget.py

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


class Widget(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)
        self.views = list()

    def init(self, width, height=None):
        for view in self.views:
            view.init(width, height)

    def do_configure_event(self, *args, **kwds):
        for view in self.views:
            view.do_configure_event(*args, **kwds)
