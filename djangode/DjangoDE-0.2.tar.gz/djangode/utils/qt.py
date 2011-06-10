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

import logging
import sys

try:
    if "--force-pyqt4" in sys.argv:
        raise ImportError

    from PySide import QtCore, QtGui, QtNetwork, QtWebKit
except ImportError:
    logging.info("Using PyQt4")
    from PyQt4 import Qt, QtCore, QtGui, QtNetwork, QtWebKit

    Signal = QtCore.pyqtSignal
    Slot = QtCore.pyqtSlot
    library = "pyqt4"
else:
    logging.info("Using PySide")

    Qt = QtCore.Qt
    Signal = QtCore.Signal
    Slot = QtCore.Slot
    library = "pyside"

