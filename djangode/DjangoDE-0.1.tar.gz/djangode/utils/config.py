# DjangoDE, a integrated development environment for Django
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

from PyQt4 import QtCore

CONFIG = None

def _load_config():
    """Load the config object."""
    global CONFIG # pylint: disable-msg=W0603

    CONFIG = QtCore.QSettings("Andrew Wilkinson", "DjangoDE")

def get_config_value(key, default=None):
    """Get the value from settings that was stored with key."""
    if CONFIG is None:
        _load_config()

    return CONFIG.value(key, default)

def set_config_value(key, value):
    """Save a value into the configuration."""
    if CONFIG is None:
        _load_config()

    CONFIG.setValue(key, value)

