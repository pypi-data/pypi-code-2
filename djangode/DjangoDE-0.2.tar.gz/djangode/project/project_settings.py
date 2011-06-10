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

import pickle

class ProjectSettings(dict):
    def __init__(self, fp=None):
        if fp is not None:
            try:
                settings = pickle.load(fp)
            except EOFError:
                pass
            else:
                self.update(settings)

        self.dirty = False

    def save_to_file(self, fp):
        pickle.dump(dict(self.items()), fp)
        self.dirty = False

    def __setitem__(self, key, value):
        if key not in self or self[key] != value:
            self.dirty = True
        return dict.__setitem__(self, key, value)
