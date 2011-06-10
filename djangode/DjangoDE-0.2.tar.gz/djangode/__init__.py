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
DjangoDE is a Django Development Environment.

Created by Andrew Wilkinson <andrewjwilkinson@gmail.com>

Released under the GNU GPL v2.

See http://code.google.com/p/djangode
"""

VERSION = (0, 2, 0)

COPYRIGHT = "Copyright &copy; 2010-2011 Andrew Wilkinson &lt;<a href='mailto:andrewjwilkinson@gmail.com'>andrewjwilkinson@gmail.com</a>&gt;"

def get_version():
    return "%s.%s" % VERSION[:2] + (".%s" % (VERSION[2], ) if VERSION[2] > 0 else "")

from djangode.main import main
