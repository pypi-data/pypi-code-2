##
## base.py
## Login : <uli@pu.smp.net>
## Started on  Sat Jul 31 12:21:21 2010 Uli Fouquet
## 
## Copyright (C) 2010 Uli Fouquet
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
## 
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##
"""Base components for core functionality.
"""
import os

# Types of changes...

#: No change marker
NONE = None

#: File/directory added marker
ADDED = 0x01

#: File/directory changed marker
MODIFIED = 0x02

#: File/directory deleted marker
DELETED = 0x04

# File types we support...

#: Unidentifiable file type
UNKNOWN_TYPE = None

#: Regular file
FILE_TYPE = 0x01

#: A directory
DIR_TYPE = 0x02


class FSChange(object):
    """A change in filesystem.

    Changes in filesystem are files or directories which were
    modified.
    """

    #: the filesystem path of the dir/file that changed
    path = None

    #: the basename of the filesystem entity (a dir or file)
    basename = None

    #: the type of change
    changetype = NONE

    #: the file type of the change
    filetype = UNKNOWN_TYPE

    #: the basename of the dir/file that changed
    
    def __init__(self, path, changetype=MODIFIED):
        self.path = os.path.abspath(path)
        self.basename = os.path.basename(path)
        self.changetype = changetype
        if os.path.isdir(self.path):
            self.filetype = DIR_TYPE
        elif os.path.isfile(self.path):
            self.filetype = FILE_TYPE
        else:
            pass
        return

class FSWalker(object):
    """A walker for the filesystem.

    This plain walker scans a directory or file for changes. It does
    this by comparing the timestamp of all files found with a given
    one. It's a simple pure Python implementation and does not store
    any status information. Therefore it is runnable with virtually
    any Python version and requires no extra modules. The drawback is,
    that his walker cannot detect file/directory deletion.

    """

    def walk(self, root_dir, timestamp):
        """Walk the filetree rooted at `root_dir` and message changes.

        Changes are files, changed in time elapsed since `timestamp`.

        Returns a generator of :class:`FSChange` objects.

        The `root_dir`, despite of its name can also be a regular
        file.

        .. todo:: Consider using standard lib :func:`os.walk`
        """
        status = self._checkStatus(root_dir, timestamp)
        if status is not NONE:
            yield FSChange(root_dir, changetype=status)
        if os.path.isdir(root_dir):
            for filename in os.listdir(root_dir):
                fullpath = os.path.join(root_dir, filename)
                for x in self.walk(fullpath, timestamp):
                    yield x

    def _checkStatus(self, path, timestamp):
        """Check whether file in `path` was changed since `timestamp`.

        Returns ``NONE``, ``MODIFIED`` or ``DELETED`` if the file
        cannot be opened.

        .. versionchanged:: 0.2

           Returns state instead of ``True``/``False``.
        """
        try:
            mtime = os.stat(path).st_mtime
            if mtime - timestamp < 0:
                return NONE
        except OSError:
            return DELETED
        return MODIFIED
