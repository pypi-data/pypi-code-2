# DjangoDE, an integrated development environment for Django
# Copyright (C) 2010 Andrew Wilkinson
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

import pickle

def module_contents(module_name):
    try:
        module = __import__(module_name, fromlist=[__doc__])
    except ImportError:
        return None
    else:
        return pickle.dumps([m for m in dir(module) if m[0] != "_"], 0)

def module_file(module_name):
    try:
        module = __import__(module_name, fromlist=[__doc__])
    except ImportError:
        return None
    else:
        return module.__file__[:-1]
