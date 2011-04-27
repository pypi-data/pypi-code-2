# Copyright (C) 2008 Marco Pantaleoni. All rights reserved
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License version 2 as
#    published by the Free Software Foundation.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

# VERSION = (major, minor, release-tag)
#
# Remember that for setuptools the release-tag can have special meaning:
#   words alphabetically before 'final' are pre-release tags, otherwise
#   are post-release tags, *BUT*
#   'pre', 'preview' and 'rc' prefixes are considered equivalend to 'c'
#
#    http://peak.telecommunity.com/DevCenter/setuptools#specifying-your-project-s-version
#
VERSION = (0, 9, 'dev')

from sflib.version import get_version as sf_get_version, get_version_setuptools as sf_get_version_setuptools

def get_version(*args, **kwargs):
    kwargs['VERSION'] = VERSION
    kwargs['path'] = __file__
    kwargs['cr_dirname'] = __file__
    return sf_get_version(*args, **kwargs)

def get_version_setuptools(*args, **kwargs):
    kwargs['VERSION'] = VERSION
    kwargs['path'] = __file__
    kwargs['cr_dirname'] = __file__
    return sf_get_version_setuptools(*args, **kwargs)
