# -----------------------------------------------------------------------------
#    Myconf - Personal configuration and installed software backup
#    Copyright (C) 2011 Some Hackers In Town
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
# -----------------------------------------------------------------------------


class Target(object):
    """
    Target class represent a address for backing up.
    """

    def __init__(self, target_address):
        """
        Arguments:
        - `target_address`:
        """
        self._target_address = target_address

        def create_backup(self):
            """
            Create a mercurial repository or update an exist one.
            """
            os.system('hg init .')
            pass
