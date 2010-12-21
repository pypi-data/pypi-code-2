##
## util.py
## Login : <uli@pu.smp.net>
## Started on  Mon Nov 29 13:50:15 2010 Uli Fouquet
## $Id$
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
"""
Helpers that do not belong to a certain component.
"""
import os
import ntpath

def split_path(path, win_os=False):
    """Split a `path` into drive, path and filename extension.

    Returns a tuple (share, path, extension) where path has no 'share'
    (i.e. something like ``C:/`` but is a regular Unix path,
    extension starts with a dot (or is empty string). The share also
    may be an empty string.

    If ``win_os`` is set to True usage of :mod:`ntpath` is
    enforced. This is normally only needed during tests. Otherwise the
    Python standard lib path manipulators from :mod:`os.path` are
    used.
    
    Examples:
    
      >>> from odls.client.util import split_path
      >>> split_path('somepath')
      ('...', '/.../somepath', '')

      >>> split_path('some_file_with_extension.txt')
      ('...', '/.../some_file_with_extension.txt', '.txt')

      >>> split_path('c://my/path.file', win_os=True)
      ('c:', '/my/path.file', '.file')

      >>> split_path('c:\\my\path.file', win_os=True)
      ('c:', '/my/path.file', '.file')
      
    """
    path_mod = os.path
    if win_os == True:
        path_mod = ntpath
    ext = path_mod.splitext(path)[-1]
    path = path_mod.normpath(path_mod.abspath(path))
    drive, path = path_mod.splitdrive(path)
    path = path.replace('\\', '/')
    #if path.startswith('//'):
    #    path = path[1:]
    return (drive, path, ext)
