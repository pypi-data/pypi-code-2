"""Setup file to create installs, eggs and/or install Tasks-Tracker"""

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

from setuptools import setup, find_packages

from pytasks.lib import versionlib

VERSION = versionlib.get_version().current_release()
NAME = 'Tasks-Tracker'
DESCRIPTION = 'A simple command line project task tracking tool.'
AUTHOR = 'Mohamed Diarra'
AUTHOR_EMAIL = 'moh@softwebia.com'
URL = 'https://launchpad.net/tasks-tracker'


PKG_DEPENDENCIES = [
    'configobj==4.6.0',
]

setup(
      name = NAME,
      version = VERSION,
      description = DESCRIPTION,
      author = AUTHOR,
      author_email = AUTHOR_EMAIL,
      url = URL,
      license = __copyright__,

      packages = find_packages(),
      install_requires=PKG_DEPENDENCIES,

      entry_points = {
            'console_scripts': [
                        'tasks = pytasks.main:run'
                        ]
      },
)