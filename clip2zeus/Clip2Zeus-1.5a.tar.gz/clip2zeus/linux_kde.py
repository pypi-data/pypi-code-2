#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gobject
gobject.threads_init()
from dbus import glib
glib.init_threads()
import dbus

from clip2zeus.common import Clip2ZeusApp

class Clip2ZeusKDE(Clip2ZeusApp):

    @property
    def clipboard(self):
        if not hasattr(self, '_clipboard'):
            bus = dbus.SessionBus()
            self._clipboard = bus.get_object('org.kde.klipper', '/klipper')

        return self._clipboard

    def check_clipboard(self):
        """Checks the system clipboard for data"""

        return str(self.clipboard.getClipboardContents())

    def update_clipboard(self, text):
        """Updates the system clipboard with the specified text"""

        self.clipboard.setClipboardContents(text)

if __name__ == '__main__':
    Clip2ZeusKDE().start()

