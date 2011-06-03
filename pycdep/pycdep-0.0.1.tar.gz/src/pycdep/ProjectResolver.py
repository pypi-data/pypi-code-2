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

class ProjectResolver(object):
    """
    class that translates the name of an include file as found 
    in a c/cpp or header file to an absolute path
    """ 
    def __init__(self, options):
        """
        make an ordered list of candidate paths
        """
        from oset import oset
        self.options = options
        self.paths_to_examine = oset([])
        self.__init_folders()

    def abs_node(self, cpp_filenode, includefile):
        """
        takes a FileNode denoting the current cpp file being examined, 
        and an includefile which is a string extracted from that c/cpp/header file,
        and resolves the include file name to a full path, taking into account
        the include file folders specified on the command line.
        """
        import os
        includefilename = includefile.name.replace("/", os.sep).replace("\\", os.sep)
        from path import path
        p = path(cpp_filenode.file_name()).abspath().dirname()
        # if we are dealing with a quoted include file, first try to find the header file in the current path
        if includefile.include_type == 'Quoted':
            full_incl_name = (p / path(includefilename)).normpath()
            if full_incl_name.isfile():
                return FileNode(self.options, full_incl_name)
        # if not found, try all of the include folders, 
        # in the order they were passed to the application
        for candidate_folders in self.paths_to_examine:
            full_incl_name = (path(candidate_folders.file_name()) / path(includefilename)).normpath()
            if full_incl_name.isfile():
                return FileNode(self.options, full_incl_name)

        import logging
        logging.warning("Couldn't resolve header file '%s' included from '%s'" % (includefilename, cpp_filenode.file_name()))
        return None

    def __init_folders(self):
        """
        perform a one-time expensive initialization
        """
        from path import path
        from oset import oset
        self.paths_to_examine = oset([])
        o = self.options
        for folder in self.options.include:
            self.paths_to_examine.add(FileNode(o, path(folder)))
        for folder in self.options.recursive_include:
            self.paths_to_examine.add(FileNode(o, path(folder)))
            for f in path(folder).walkdirs():
                self.paths_to_examine.add(FileNode(o, f))
        for folder in self.options.exclude:
            self.paths_to_examine.remove(FileNode(o, path(folder)))
        for folder in self.options.recursive_exclude:
            self.paths_to_examine.add(FileNode(o, path(folder)))
            for f in path(folder).walkdirs():
                self.paths_to_examine.remove(FileNode(o, f))

if __name__ == "__main__":
    from path import path
    from IncludeFile import IncludeFile
    class Options(object):
        """
        mock object
        """
        def __init__(self):
            """
            initialize options 
            """
            self.recursive_include = [path(".")]
            self.include = []
            self.recursive_exclude = []
            self.exclude = []
            self.prefixlength = 2
            self.case_insensitive = True
            self.separators = ['/', '\\']
            self.common_root = ''
            self.strip_common_root_folder = False

    p = ProjectResolver(Options())
 
    file_under_test = path("/home/shimpe/development/python/PyCDep/src/pycdep/cpp/test.cpp")
    file_under_test2 = path("/home/shimpe/development/python/PyCDep/src/pycdep/cpp/sub/test.cpp")

    print p.abs_node(FileNode(Options(), file_under_test), IncludeFile("test.h",'quoted'))
    print p.abs_node(FileNode(Options(), file_under_test), IncludeFile("sub/test.h",'angular'))
    print p.abs_node(FileNode(Options(), file_under_test), IncludeFile("sub2/test2.h", 'quoted'))

    print p.abs_node(FileNode(Options(), file_under_test2), IncludeFile("test.h",'quoted'))
    print p.abs_node(FileNode(Options(), file_under_test2), IncludeFile("sub/test.h",'angular'))
    print p.abs_node(FileNode(Options(), file_under_test2), IncludeFile("sub2/test2.h", 'quoted'))
    print p.abs_node(FileNode(Options(), file_under_test2), IncludeFile("..\\test.h", 'quoted'))

