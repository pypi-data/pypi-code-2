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
This module handles the loading and saving of DjangoDE settings.
"""

from qt import QtCore, library as qt_library

from config_defaults import config_defaults, config_converter

CONFIG = None

def _load_config():
    """Load the config object."""
    global CONFIG # pylint: disable-msg=W0603

    CONFIG = QtCore.QSettings("Andrew Wilkinson", "DjangoDE")

def get_config_value(key, default=None):
    """Get the value from settings that was stored with key."""
    if CONFIG is None:
        _load_config()

    if not CONFIG.contains(key):
        return default if default is not None else config_defaults.get(key, None)

    value = CONFIG.value(key)

    converter = config_converter.get(key, lambda v: v)

    # PyQt4 returns a QVariant while PySide doesn't
    if hasattr(QtCore, "QVariant") and isinstance(value, QtCore.QVariant):
        if value.isNull():
            return None
        elif value.typeName() == "QString":
            return converter(unicode(value.toString()))
        elif value.typeName() == "QByteArray":
            return converter(value.toByteArray())
        elif value.typeName() == "QStringList":
            return converter(value.toStringList())
        else:
            raise ValueError, "Unknown QVariant type %s." % (value.typeName(), )
    else:
        return converter(value)

def set_config_value(key, value):
    """Save a value into the configuration."""
    if CONFIG is None:
        _load_config()

    if qt_library == "pyqt4" and isinstance(value, tuple):
        value = list(value)

    CONFIG.setValue(key, value)
