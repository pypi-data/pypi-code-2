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
import logging
from FileNode import FileNode
from path import path

class ProjectResolver(object):
    """
    class that translates the name of an include file as found 
    in a c/cpp or header file to an absolute path
    """ 
    def __init__(self, options):
        """
        make an ordered list of candidate paths
        """
        self.options = options
        self.__init_folders()
        self.unresolvable = set([])

    def abs_node(self, cpp_filenode, includefile):
        """
        takes a FileNode denoting the current cpp file being examined, 
        and an includefile which is a string extracted from that c/cpp/header file,
        and resolves the include file name to a full path, taking into account
        the include file folders specified on the command line.
        """
        logging.debug("Investigating %s, included from %s" % (includefile, cpp_filenode))
        includefilename = includefile.name.replace("\\", "/")

        p = path(cpp_filenode.file_name()).dirname()
        includepath = path(includefilename)
        # if we are dealing with a quoted include file, first try to find the header file in the current path
        if includefile.include_type == 'Quoted':
            full_incl_name = (p / includepath)
            fn = FileNode(self.options, full_incl_name)
            if fn in self.files_to_examine:
                logging.debug("   Recognized in current path %s" % fn)
                return fn

        if includefilename in self.unresolvable:
            # speedup handling of known unresolvable header files
            logging.warning("Skipping unknown include file '%s' included from '%s'" % (includefilename, cpp_filenode.file_name()))
            return None


        # if not found, try all of the include folders, 
        # in the order they were passed to the application
        for candidate_folders in self.paths_to_examine:
            full_incl_name = (path(candidate_folders.file_name()) / includepath) 
            fn = FileNode(self.options, full_incl_name)
            if fn in self.files_to_examine:
                logging.debug("   Recognized %s" % fn)
                #print "   Recognized in search paths %s" % fn
                return fn
            #else:
            #    print "Tried if %s exists..." % full_incl_name

        self.unresolvable.add(includefilename)
        logging.warning("Couldn't resolve header file '%s' included from '%s'" % (includefilename, cpp_filenode.file_name()))
        #print "Couldn't resolve header file '%s' included from '%s'" % (includefilename, cpp_filenode.file_name())
        return None

    def __init_folders(self):
        """
        perform a one-time expensive initialization
        """
        from path import path
        from oset import oset
        import logging
        self.paths_to_examine = oset([])
        self.files_to_examine = oset([])
        o = self.options
        for folder in self.options.include:
            p = path(folder)
            self.paths_to_examine.add(FileNode(o, p))
            logging.debug("add path ", p)
            for fl in p.files():
              logging.debug("    add file ", fl)
              self.files_to_examine.add(FileNode(o, fl))
        for folder in self.options.recursive_include:
            p = path(folder)
            logging.debug("add path ", p)
            self.paths_to_examine.add(FileNode(o, p))
            for f in p.walkdirs():
                logging.debug("    add file ", f)
                self.paths_to_examine.add(FileNode(o, f))
            for fl in p.walkfiles():
                logging.debug("    add file ", fl)
                self.files_to_examine.add(FileNode(o, fl))
        for folder in self.options.exclude:
            p = path(folder)
            self.paths_to_examine.remove(FileNode(o, p))
            logging.debug("remove path ", p)
            for fl in p.files():
              self.files_to_examine.remove(FileNode(o, fl))
              logging.debug("    remove file ", fl)
           
        for folder in self.options.recursive_exclude:
            p = path(folder)
            logging.debug("remove path ", p)
            self.paths_to_examine.remove(FileNode(o, p))
            for f in p.walkdirs():
                self.paths_to_examine.remove(FileNode(o, f))
                logging.debug("remove path ", f)
            for fl in p.walkfiles():
                self.files_to_examine.remove(FileNode(o, fl))
                logging.debug("    remove file ", fl)

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

