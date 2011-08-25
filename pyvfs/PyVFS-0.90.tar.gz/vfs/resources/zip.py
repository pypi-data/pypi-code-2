# Copyright (c) 2011 Christopher S. Case
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""This is a vfs class for zip files."""

__docformat__ = "restructuredtext"

import time, zipfile
from cStringIO import StringIO

from resource import Resource

class ZipResource(Resource):

    """This is a vfs class for zip files.

    The following attributes are used:

    resourcePath
      This is the name of the zip file.

    zip
      This is a ``zipfile.ZipFile`` instance for working with the zip.

    Known bugs:

    If you think of a zip file as a filesystem, there is no path to represent
    the root of the filesystem as a directory.  It'd be nice to add code to
    treat "/" as the root of the filesystem.

    """

    def __init__(self, resourcePath):
        """Set the name of the zip file.

        If this isn't a zip file, raise a ValueError.

        """
        if not zipfile.is_zipfile(resourcePath):
            raise ValueError("``resourcePath`` must be a path to a zip file!")

        self.resourcePath = resourcePath
        self.zip = zipfile.ZipFile(resourcePath)

    def __repr__(self):
        return '<%s resourcePath="%s">' % (self.__class__.__name__, self.resourcePath)

    def isdir(self, path):
        """Return true if the pathname refers to an existing directory.

        """
        if path == '.' or path == '/':
            return True

        else:
            if self.exists(path) and not self.isfile(path):
                return True
            else:
                return False

    def lsdir(self, path):
        """Returns a list of files in ``path``.

        """
        ls = list()
        filelist = self.zip.namelist()

        for file in filelist:

            if path == '.' or path == '/':
                filename = file.split('/')[0]

                if filename not in ls:
                    ls.append(filename)
            else:
                path = self.translate_path(path)
                if file.startswith(path):
                    filename = file[len(path):]

                    if len(filename) > 0:
                        if filename not in ls:
                            ls.append(filename)

        ls.sort()
        return ls

    def exists(self, path):
        """Test whether a path exists.  Returns False for broken symbolic links

        """
        if path == '.' or path == '/':
            return True

        else:
            if path.startswith('/'):
                path = path[1:]

            to_try = [path]

            if not path.endswith("/"):
                to_try.append(path + "/")

            for x in to_try:
                try:
                    self.zip.getinfo(x)
                    return True

                except KeyError:
                    continue

            else:
                return False

    def isfile(self, path):
        """Test whether a path is a regular file.

        """
        if path.startswith('/'):
            path = path[1:]

        try:
            self.zip.getinfo(path)

            if path.endswith('/'):
                return False
            return True

        except KeyError:
            return False

    def open(self, name, mode='r'):
        """open(filename, [, mode='r']) -> fd

        Open a file from inside the zipfile. Returned as a StringIO.

        """
        name = self.translate_path(name)
        return StringIO(self.zip.read(name))

    def stat(self, path):
        """Return a stat for the given path.

        The stat that I'm capable of returning is very stripped.  It only has
        the two attributes ``st_mtime`` and ``st_size``.

        """
        path = self.translate_path(path)
        info = self.zip.getinfo(path)
        time_str = " ".join(map(str, info.date_time))
        time_tuple = time.strptime(time_str, "%Y %m %d %H %M %S")
        time_float = time.mktime(time_tuple)

        return Stat(time_float, info.file_size)

    def translate_path(self, path):
        """Translate ``path`` to the local filename syntax.

        """
        if path.startswith('/'):
            path = path[1:]

        if (not path.endswith("/")) and self.isdir(path):
            path += "/"

        return path


class Stat:

    def __init__(self, st_mtime, st_size):
        self.st_mtime = st_mtime
        self.st_size = st_size
