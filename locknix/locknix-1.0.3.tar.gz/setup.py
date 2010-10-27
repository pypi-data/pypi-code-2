# Copyright (C) 2007-2010 by Barry A. Warsaw
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
# USA.

import ez_setup
ez_setup.use_setuptools()

from locknix import __version__
from setuptools import setup, find_packages



setup(
    name            = 'locknix',
    version         = __version__,
    summary         = 'NFS-safe file locking with timeouts for POSIX systems.',
    description     = 'NFS-safe file locking with timeouts for POSIX systems.',
    long_description= """\
locknix implements an NFS-safe file-based locking algorithm influenced by
the GNU/Linux open(2) manpage, under the description of the O_EXCL option.""",
    author          = 'Barry Warsaw',
    author_email    = 'barry@python.org',
    url             = 'https://launchpad.net/locknix',
    license         = 'LGPL',
    keywords        = 'locking',
    packages        = find_packages(),
    include_package_data = True,
    )
