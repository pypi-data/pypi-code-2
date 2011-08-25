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

"""This represents a mountable resource to the vfs."""

import os, posixpath

class Resource(object):

    """This is the base class for all mountable resources.

    resourcePath:
        This represents the original path of the resource.

    """
    resourcePath = ""
    __curdir = ""
    __pardir = ""


    def __init__(self, resourcePath):
        """Set the resourcePath of the filesystem.

        """
        self.resourcePath = resourcePath

    def __repr__(self):
        return '<%s resourcePath="%s">' % (self.__class__.__name__, self.resourcePath)

    def isdir(self, path):
        """Return true if the pathname refers to an existing directory.

        """
        raise NotImplementedError("Attempted to call function on base \
            Resource class.")

    def lsdir(self, path):
        """Returns a list of files in ``path``.

        """
        raise NotImplementedError("Attempted to call function on base \
            Resource class.")

    def isfile(self, path):
        """Test whether a path is a regular file.

        """
        raise NotImplementedError("Attempted to call function on base \
            Resource class.")

    def exists(self, path):
        """Test whether a path exists.  Returns False for broken symbolic links

        """
        raise NotImplementedError("Attempted to call function on base \
            Resource class.")

    def join(self, a, *path):
        """Join two or more pathname components, inserting '/' as needed.
        If any component is an absolute path, all previous path components
        will be discarded.

        """
        # Posixpath behavior is desired on all platforms
        return posixpath.join(a, *path)

    def splitext(self, path):
        """Split the extension from a pathname.

        Extension is everything from the last dot to the end, ignoring
        leading dots.  Returns "(root, ext)"; ext may be empty.

        """
        # Posixpath behavior is desired on all platforms
        return posixpath.splitext(path)

    def splitdrive(self, path):
        """Split a pathname into drive and path. On Posix, drive is always
        empty.

        """
        # Posixpath behavior is desired on all platforms
        return posixpath.splitdrive(path)

    def split(self, path):
        """Split a pathname.  Returns tuple "(head, tail)" where "tail" is
        everything after the final slash.  Either part may be empty.

        """
        # Posixpath behavior is desired on all platforms
        return posixpath.split(path)

    def stat(self, path):
        """stat(path) -> stat result

        Perform a stat system call on the given path.

        """
        raise NotImplementedError("Attempted to call function on base \
            Resource class.")

    def open(self, filename, mode='r'):
        """open(filename, [, mode='r']) -> fd

        Open a file (for low level IO).

        """
        raise NotImplementedError("Attempted to call function on base \
            Resource class.")

    @property
    def curdir(self):
        """The current directory, relative to the root of the resource.

        """
        return self.__curdir

    @property
    def pardir(self):
        """The parent directory relative to the current directory.

        """
        return self.__pardir

    def translate_path(self, path):
        """Translate ``path`` to the local filename syntax.

        """
        raise NotImplementedError("Attempted to call function on base \
            Resource class.")
