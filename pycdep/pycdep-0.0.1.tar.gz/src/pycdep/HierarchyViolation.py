# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: stefaan.himpe@gmail.com

class HierarchyViolation(object):
    """
    class to hold a hierarchy violation
    """
    def __init__(self, from_proj, to_proj):
        self.from_proj = from_proj
        self.to_proj = to_proj

    def __cmp__(self, other):
        if self.from_proj < other.from_proj:
            return -1
        elif self.from_proj > other.from_proj:
            return 1
        if self.to_proj < other.to_proj:
            return -1
        elif self.from_proj > other.from_proj:
            return 1
        return 0

    def __hash__(self):
        return hash( (self.from_proj, self.to_proj) )

    def __repr__(self):
        return "HierarchyViolation('%s', '%s')" % (self.from_proj, self.to_proj)
