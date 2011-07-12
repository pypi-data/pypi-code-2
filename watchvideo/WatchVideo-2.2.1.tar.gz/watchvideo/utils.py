# -*- coding: utf-8 -*-
# Copyright (C) 2010  Michał Masłowski  <mtjm@mtjm.eu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""
Other functions.
"""


import os.path


__all__ = ("PATH", "is_executable", "is_command")


#: The list of paths searched for executables.
PATH = os.environ["PATH"].split(os.path.pathsep)


def is_executable(path):
    """Return `True` if `path` exists, is file and is executable."""
    if not os.path.isfile(path):
        return False
    return os.access(path, os.X_OK)


def is_command(prog):
    """Return `True` if `prog` is found as program."""
    if is_executable(prog):
        return True
    for path in PATH:
        if is_executable(os.path.join(path, prog)):
            return True
    return False
