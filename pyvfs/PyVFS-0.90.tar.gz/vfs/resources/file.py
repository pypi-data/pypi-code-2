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

"""This is a vfs class for the normal filesystem."""

__docformat__ = "restructuredtext"

import os
from resource import Resource


class FileResource(Resource):

    """This is a vfs class for the normal filesystem.

    It's mostly a wrapper for os.path, with one caveat. All paths passed in are
    assumed to be relative to ``resourcePath``, making '/' mean the root of the
    resource. This means that the path '/var' will automatically be translated
    into ``os.path.join(resourcePath, 'var')``.

    The following attributes are used:

    resourcePath
      This is the original path of the resource, on the filesystem.

    """

    def __init__(self, resourcePath):
        """Set the resourcePath of the filesystem.

        If this isn't a directory, raise a ValueError.

        """
        if not os.path.isdir(resourcePath):
            raise ValueError("resourcePath must be a directory")

        self.resourcePath = resourcePath

    def __repr__(self):
        return '<%s resourcePath="%s">' % (self.__class__.__name__, self.resourcePath)

    def isdir(self, path):
        """Return true if the pathname refers to an existing directory.

        """
        path = self.translate_path(path)
        return os.path.isdir(path)

    def lsdir(self, path):
        """Returns a list of files in ``path``.

        """
        path = self.translate_path(path)
        return os.listdir(path)

    def exists(self, path):
        """Test whether a path exists.  Returns False for broken symbolic links

        """
        path = self.translate_path(path)
        return os.path.exists(path)

    def isfile(self, path):
        """Test whether a path is a regular file.

        """
        path = self.translate_path(path)
        return os.path.isfile(path)

    def stat(self, path):
        """stat(path) -> stat result

        Perform a stat system call on the given path.

        """
        path = self.translate_path(path)
        return os.stat(path)

    def open(self, filename, mode='r'):
        """open(filename, [, mode='r']) -> fd

        Open a file (for low level IO).

        """
        filename = self.translate_path(filename)
        return open(filename, mode)

    def translate_path(self, path):
        """Translate ``path`` to the local filename syntax.

        Actually, ``path`` is already in the local filename syntax, but this is
        your last chance to do anything else, such as making it an absolute
        path, etc.

        """
        # Strip off leading /, since that's assumed to be the root of the
        # resource. The only time that isn't true would be with join, which
        # doesn't use this function anyway.
        if path.startswith('/'):
            path = path[1:]

        return os.path.abspath(self.join(self.resourcePath, path))
