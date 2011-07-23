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

class Dependency(object):
    """
    class that models a dependency between two files
    Dependency(source_node, include_file)
    """
    def __init__(self, source_node, include_node):
        """
        keep two nodes: 
         * source_node is the FileNode that holds the source code file being examined
         * include_node is the FileNode that holds the file being included
        """
        self.source_node = source_node
        self.include_node = include_node

    def __hash__(self):
        """
        helper function to use Dependencies in a set
        """
        return hash((self.source_node, self.include_node))

    def __cmp__(self, other):
        """
        helper function to use Dependencies in a set
        """
        if self.source_node < other.source_node:
            return -1
        elif self.source_node > other.source_node:
            return 1

        if self.include_node < other.include_node:
            return -1
        elif self.include_node > other.include_node:
            return 1
        return 0

    def __repr__(self):
        """
        generate a representation of this object for usage in 
        debug messages
        """
        return "Dependency(%s, %s)" % (self.source_node.analysis_name(), self.include_node.analysis_name())

