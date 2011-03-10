# -*- coding: utf-8 -*-
# Copyright (C) 2010, 2011  Michał Masłowski  <mtjm@mtjm.eu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""
Module importing PyQt4 or PySide modules used by WatchVideo.
"""


import sys
import os

# Use more Pythonic and PySide-like API of PyQt4.
try:
    import sip
    sip.setapi("QString", 2)
    sip.setapi("QVariant", 2)
except ImportError:
    assert True  # PyQt4 is not available, error later


try:
    #: List of packages to try.
    _PACKAGES = os.environ["WATCHVIDEO_QT"].split()
except KeyError:
    _PACKAGES = ("PyQt4", "PySide")


#: Package providing Qt bidings.
_PACKAGE = None

for _PACKAGE in _PACKAGES:
    try:
        _MODULE = __import__(_PACKAGE, globals(), locals(),
                             ("QtCore", "QtGui"), 0)
        QtCore = _MODULE.QtCore
        QtGui = _MODULE.QtGui
    except (ImportError, AttributeError):
        _PACKAGE = None
    else:
        break

if _PACKAGE is None:
    print """\nError!
-------------
Dependency Problem - The required PyQt4 libraries couldn't be found.
If you are on Debian or one of its derivated systems (like Ubuntu)
type \"sudo aptitude -y install python-qt4\" in order to install them.
If you are on another distribution, search for \"pyqt4\" if it has a
package manager, or download and install it from
<http://www.riverbankcomputing.co.uk/pyqt/download.php>.
"""
    sys.exit(1)


__all__ = ("QtCore", "QtGui")


# Aliases for PySide compatibility.
if _PACKAGE == "PyQt4":
    QtCore.Signal = QtCore.pyqtSignal
    QtCore.Slot = QtCore.pyqtSlot

# Allow "from watchvideo.qt.QtCore import ..." and similar.
sys.modules["watchvideo.qt.QtCore"] = QtCore
sys.modules["watchvideo.qt.QtGui"] = QtGui
