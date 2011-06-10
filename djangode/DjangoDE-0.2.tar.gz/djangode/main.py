# DjangoDE, an integrated development environment for Django
# Copyright (C) 2010-2011 Andrew Wilkinson
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

"""
This module contains the function which starts DjangoDE running.
"""

import gc
import logging
import os
import sys

import djangode
from djangode import global_objects
from djangode.gui import MainWindow
from djangode.utils import set_proxy
from djangode.utils.qt import QtGui

def main():
    """
    This function creates the MainWindow object and starts the application running.
    """
    logging.getLogger('').setLevel(logging.DEBUG)
    logging.info("Welcome to DjangoDE " + djangode.get_version())
    logging.info("Licensed under the GNU GPL 2")
    logging.info("Copyright Andrew Wilkinson <andrewjwilkinson@gmail.com>")

    app = QtGui.QApplication(sys.argv)
    app.lastWindowClosed.connect(app_quit)

    set_proxy()

    global_objects.icon = QtGui.QPixmap(os.path.dirname(djangode.__file__) + os.sep + "gfx" + os.sep + "logo_square.png")
    global_objects.main_window = MainWindow()
    global_objects.main_window.show()

    sys.exit(app.exec_())

def app_quit():
    # In order to prevent a deadlock involving QFileSystemWatcher when QApplication has already been deleted
    # we ensure the main window has been fully collected.
    global_objects.window = None
    gc.collect()
