"""Module used to create version file and get version"""

__copyright__ = """
    This file is part of Tasks-Tracker.

    Tasks-Tracker is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    Tasks-Tracker is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Tasks-Tracker.  If not, see <http://www.gnu.org/licenses/>.
"""

MAJOR_REV = 0
VERSION_FILE = 'pytasks/lib/_bzrversion.py'

class Version(object):
    @classmethod
    def current_release(cls):
        return '%d.%s' % (MAJOR_REV, cls.revision_number())
    
    @classmethod
    def revision_number(cls):
        from _bzrversion import version_info
        return version_info['revno']
    
    @classmethod
    def revision_id(cls):
        from _bzrversion import version_info
        return version_info['revision_id']
    
    @classmethod
    def build_date(cls):
        from _bzrversion import version_info
        return version_info['build_date']


def get_version():        
    return Version()


def create_version_file():
    import os
    
    print 'generating version info file [%s]...' % VERSION_FILE
    
    BZR_VERSION_INFO_COMMAND = 'bzr version-info --format=python > %s' % VERSION_FILE
    os.system(BZR_VERSION_INFO_COMMAND)