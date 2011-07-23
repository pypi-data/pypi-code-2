# Copyright 2010 Oren Zomer <oren.zomer@gmail.com>
#
# This file is part of pypsifas.
# 
# pypsifas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# pypsifas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with pypsifas.  If not, see <http://www.gnu.org/licenses/>.
#
# This file is using pybfc 0.2
# see pybfc-0.2.zip/README for more details.

"""
A python library for parsing and building of data structures with the ability
of solving simple heuristics of interdepent sub-structures. It is based on
the concept of defining data structures in a declarative manner, where complex
structures are composed by combining simpler ones.
"""

import os, sys

if not hasattr(sys, 'version_info') or sys.version_info < (2, 6, 0, 'final'):
    raise SystemExit("pypsifas requires Python 2.6 or later.")

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PACKAGE_NAME = 'psifas'

os.chdir(PROJECT_ROOT)

sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(1, os.path.join(PROJECT_ROOT, 'pybfc-0.2.zip'))
try:
    from bfc import setup
finally:
    del sys.path[0:2]

PACKAGES = setup.setup_packages(PROJECT_ROOT, PACKAGE_NAME)


try:
    VERSION_INFO = setup.read_version_info(PROJECT_ROOT, PACKAGE_NAME)
except (setup.ReadVersionError, OSError):
    VERSION_INFO = setup.read_version_info_from_file(PROJECT_ROOT, PACKAGE_NAME)
    VERSION = setup.version_info_to_version(VERSION_INFO)
else:
    VERSION = setup.write_version_file(PROJECT_ROOT, PACKAGE_NAME, VERSION_INFO)

from distutils.core import setup

if len(sys.argv) == 1:
    while True:
        user_answer = raw_input("Install %s%s? [y/n]\n" % (PACKAGE_NAME, VERSION)).lower()
        if user_answer in ('y', 'yes'):
            sys.argv.append('install')
            break
        elif user_answer in ('n', 'no'):
            break
        else:
            print "choose one of: y, yes, n, no"

setup(name = 'psifas',
      version = VERSION,
      author = 'Oren Zomer',
      author_email = 'oren.zomer@gmail.com',
      url = 'http://pypsifas.sourceforge.net/',
      download_url = 'http://pypsifas.sourceforge.net/',
      platforms = 'Any',
      description = __doc__.strip().split('\n')[0],
      long_description = __doc__,
      license = 'GNU GPLv3+',
      packages = PACKAGES,
      )
