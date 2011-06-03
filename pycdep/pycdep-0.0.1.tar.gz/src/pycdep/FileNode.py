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

class FileNode(object):
    """
    class to hold a file node
    a file node has two representations
     - file_name(self): returns file name, for use in file operations (abs path, always case sensitive)
     - analysis_name(self): returns truncated and optionally case modified file name, for use in analysis
    the file node knows whether it is a c/cpp file or a header file
    """
    def __init__(self, options, path):
        """
        remember command line options
        a node wraps a path.py path
        """
        self.options = options
        self.path = path.abspath()

    def file_name(self):
        """
        returns a representation that is suitable for
        interaction with the file system
        """
        return self.__pp(for_display=False)

    def analysis_name(self):
        """
        returns a representation that is suitable for
        dependency analysis
        """
        return self.__pp(for_display=True)

    def project_name(self):
        """
        returns the project name for a given file
        projectname is defined as the folder in which a file
        lives. projectname is derived from the analysis_name
        """
        from path import path
        return "%s" % path(self.analysis_name()).dirname()

    def is_code(self):
        """
        returns true for a c/cpp file
        """
        return self.file_name().endswith(self.options.cppsuffix)

    def is_header(self):
        """
        returns true for a header file
        """
        return self.file_name().endswith(self.options.headersuffix)

    def __pp(self, for_display=None):
        """
        Postprocess the filepath to get a readable name.
         * keep only last prefixlength parts of the name
         * convert from path to string
        """
        import os
        from path import path
        filename = "%s" % self.path
        for s in self.options.separators:
            filename = filename.replace(s, os.sep)
        filepath = path(filename)

        splitted = filter(lambda s: s not in self.options.separators, [ "%s" % f for f in filepath.splitall() ])
        rejoined = '/' + '/'.join(splitted) if ':\\' not in splitted[0] else '/'.join(splitted)

        if for_display:
            if not self.options.common_root:
                cutoff = splitted[-self.options.prefixlength:]
                rejoined = '/'.join(cutoff)
            else:
                for ro in self.options.common_root:
                    #print ro
                    if ro in rejoined:
                        index = rejoined.index(ro)
                        if self.options.strip_common_root:
                            rejoined = rejoined[index+len(ro)+1:]
                        else:
                            rejoined = rejoined[index:]
                        break
        if for_display and self.options.case_insensitive:
            result = rejoined.lower()
        else:
            result = rejoined

        return result

    def __hash__(self):
        """
        helper function so we can use nodes in a set
        """
        return hash( (self.file_name(), self.analysis_name()) )

    def __cmp__(self, other):
        """
        helper function so we can use nodes in a set
        """
        if self.file_name() < other.file_name():
            return -1
        elif self.file_name() > other.file_name():
            return 1
        if self.analysis_name() < other.analysis_name():
            return -1
        elif self.analysis_name() > other.analysis_name():
            return 1
        return 0

    def __repr__(self):
        """
        represent a node as [/full/path/to/file#shortened/path]
        * full path is always case sensitive and an absolute path
        * shortened path is cut off to a certain length, and can be transformed
          to all lowercase in case we are working on a case insensitive file system
        """
        return "FileNode(" + self.file_name() + "," + self.analysis_name() + ")"

if __name__ == "__main__":
    class Options(object):
        def __init__(self, flag):
            self.prefixlength = 5
            self.case_insensitive = False
            self.separators = ['/', '\\']
            self.strip_common_root = flag
            self.common_root = ["blah", "cpp/sub"]

    from path import path
    F = FileNode(Options(True), path("cpp\\sub/test.h"))
    print "Filenode: ", F
    print "Project name: ", F.project_name()
    print "Analysis name: ", F.analysis_name()

    F = FileNode(Options(False), path("cpp\\sub/test.h"))
    print "Filenode: ", F
    print "Project name: ", F.project_name()
    print "Analysis name: ", F.analysis_name()



