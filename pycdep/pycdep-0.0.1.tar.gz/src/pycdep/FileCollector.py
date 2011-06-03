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

from FileNode import FileNode

class FileCollector(object):
    """
    class to collect files (nodes) that will be analyzed
    """
    def __init__(self, options):
        """
        remember the command line options
        """
        self.options = options

    def nodes(self):
        """
        calculate a list of files (nodes) to examine
        """
        cpp = "*" + self.options.cppsuffix
        h = "*" + self.options.headersuffix
        from path import path
        files_to_examine = set([])
        o = self.options
        for folder in o.include:
            files_to_examine.update( [FileNode(o, f) for f in path(folder).files(cpp) ] )
            files_to_examine.update( [FileNode(o, f) for f in path(folder).files(h)   ] )
        for folder in o.recursive_include:
            files_to_examine.update( [FileNode(o, f) for f in path(folder).walkfiles(cpp, errors="warn") ] )
            files_to_examine.update( [FileNode(o, f) for f in path(folder).walkfiles(h, errors="warn")   ] )
        for folder in o.exclude:
            files_to_examine.difference_update( [FileNode(o, f) for f in path(folder).files(cpp)] )
            files_to_examine.difference_update( [FileNode(o, f) for f in path(folder).files(h)  ] )
        for folder in o.recursive_exclude:
            files_to_examine.difference_update( [ FileNode(o, f) for f in path(folder).walkfiles(cpp, errors="warn") ] )
            files_to_examine.difference_update( [ FileNode(o, f) for f in path(folder).walkfiles(h, errors="warn")   ] )
        return files_to_examine
