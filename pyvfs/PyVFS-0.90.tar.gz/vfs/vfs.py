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

import os, zipfile

from resources import Resource, FileResource, ZipResource

class VFS(object):
    __mounts = dict()

    def __init__(self):
        pass

    def __getitem__(self, item):
        """Returns the Resource instance at the mount point `item`.

        Raises a key exception if the item isn't found.
        """
        try:
            return self.__mounts[item]

        except KeyError:
            raise KeyError("Mount point %s not mounted in VFS!" % (item,))

    def __setitem__(self, key, value):
        """Mounts `value` at mount point `key`.

        Raises an error if `value` isn't a Resource instance, or if it isn't of
        a mountable type.
        """

        if isinstance(value, Resource):
            self.__mounts[key] = value

        elif isinstance(value, str):
            self.mount(value, key)

        else:
            raise ValueError("Value not of type Resource, or str!")

    def __contains__(self, item):
        """VFS.__contains__(mount) -> True if ``VFS`` has a key ``mount``,
        else False

        """
        return self.__mounts.__contains__(item)

    def mount(self, resource, name):
        """Mounts `resource` at mount point `name`.

        Raises an error if the resource isn't of a mountable type.
        """
        resource = os.path.abspath(resource)

        if os.path.exists(resource):
           if os.path.isdir(resource):
               res = FileResource(resource)
               self.__mounts[name] = res
           elif zipfile.is_zipfile(resource):
               res = ZipResource(resource)
               self.__mounts[name] = res
           else:
               raise ValueError("Resource is not a directory or mountable \
                filetype.")
        else:
            raise ValueError("Resource does not exist, or is not a valid path.")
        pass

    def unmount(self, name):
        """Unmounts the resource at mount point `name`. Does not attempt to
        remove the resource; we assume python's smart about garbage collection,
        and if you've held on to an instance of it, we assume you know what
        you're doing.

        Raises an error if the resource isn't found.
        """
        try:
            del self.__mounts[name]

        except KeyError:
            raise KeyError("%s not mounted!" & (name,))

    def getResource(self, name):
        """Returns the Resource instance at the mount point `name`.
        """
        return self[name]

    def mounts(self):
        return self.__mounts.keys()
