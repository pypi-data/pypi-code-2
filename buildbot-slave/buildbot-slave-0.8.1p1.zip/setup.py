#!/usr/bin/env python
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
Standard setup script.
"""

import sys
import os
from distutils.core import setup

from buildslave import version

scripts = ["bin/buildslave"]
# sdist is usually run on a non-Windows platform, but the buildslave.bat file
# still needs to get packaged.
if 'sdist' in sys.argv or sys.platform == 'win32':
    scripts.append("contrib/windows/buildslave.bat")

setup_args = {
    'name': "buildbot-slave",
    'version': version,
    'description': "BuildBot Slave Daemon",
    'long_description': "See the 'buildbot' package for details",
    'author': "Brian Warner",
    'author_email': "warner-buildbot@lothar.com",
    'maintainer': "Dustin J. Mitchell",
    'maintainer_email': "dustin@v.igoro.us",
    'url': "http://buildbot.net/",
    'license': "GNU GPL",
    'classifiers': [
        'Development Status :: 5 - Production/Stable',
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Testing',
        ],

    'packages': [
        "buildslave",
        "buildslave.commands",
        "buildslave.scripts",
        "buildslave.test",
        "buildslave.test.unit",
    ],
    'scripts': scripts
    }

# set zip_safe to false to force Windows installs to always unpack eggs
# into directories, which seems to work better --
# see http://buildbot.net/trac/ticket/907
if sys.platform == "win32":
    setup_args['zip_safe'] = False

try:
    # If setuptools is installed, then we'll add setuptools-specific arguments
    # to the setup args.
    import setuptools #@UnusedImport
except ImportError:
    setup_args['scripts'] = [
        'bin/buildslave'
    ]
else:
    setup_args['install_requires'] = [
        'twisted >= 2.0.0',
    ]
    setup_args['entry_points'] = {
        'console_scripts': [
            'buildslave = buildslave.scripts.runner:run',
        ],
    }

setup(**setup_args)
