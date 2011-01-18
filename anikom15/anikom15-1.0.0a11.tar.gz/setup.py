# Filename: setup.py
#
# Copyright 2010 Westley Martinez
#
# This file is part of Anikom15's Computer Game (ACG).
# ACG is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# ACG is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ACG.  If not, see <http://www.gnu.org/licenses/>.
"""Common commands: (see '--help-commands' for more)

  setup.py build      will build the package underneath 'build/'
  setup.py install    will install the package

Global options:
  --verbose (-v)      run verbosely (default)
  --quiet (-q)        run quietly (turns verbosity off)
  --dry-run (-n)      don't actually do anything
  --help (-h)         show detailed help message
  --command-packages  list of packages that provide distutils commands

Information display options (just display information, ignore any commands)
  --help-commands     list all available commands
  --name              print package name
  --version (-V)      print package version
  --fullname          print <package name>-<version>
  --author            print the author's name
  --author-email      print the author's email address
  --maintainer        print the maintainer's name
  --maintainer-email  print the maintainer's email address
  --contact           print the maintainer's name if known, else the author's
  --contact-email     print the maintainer's email address if known, else the
                      author's
  --url               print the URL for this package
  --license           print the license of the package
  --licence           alias for --license
  --description       print the package description
  --long-description  print the long package description
  --platforms         print the list of platforms
  --classifiers       print the list of classifiers
  --keywords          print the list of keywords
  --provides          print the list of packages/modules provided
  --requires          print the list of packages/modules required
  --obsoletes         print the list of packages/modules made obsolete

usage: setup.py [global_opts] cmd1 [cmd1_opts] [cmd2 [cmd2_opts] ...]
   or: setup.py --help [cmd1 cmd2 ...]
   or: setup.py --help-commands
   or: setup.py cmd --help

"""

import sys
import os
from distutils.core import setup

NAME = 'anikom15'
VERSION = '1.0.0a11'
DESCRIPTION = "Anikom15\u2019s Computer Game"
LONG_DESCRIPTION = ''
with open('README.txt') as f:
    for line in f:
        LONG_DESCRIPTION += line
AUTHOR = 'Westley Mart\u00ednez'
AUTHOR_EMAIL = 'anikom15@gmail.com'
URL = 'http://innovations.selfip.net/projects/acg/'
DOWNLOAD_URL = URL + 'anikom15-' + VERSION + '.tar.gz'
CLASSIFIERS = ['Development Status :: 3 - Alpha',
               'Environment :: Other Environment',
               'Intended Audience :: Education',
               'Intended Audience :: End Users/Desktop',
               'License :: OSI Approved :: GNU General Public License (GPL)',
               'Natural Language :: English',
               'Operating System :: Microsoft :: Windows',
               'Operating System :: OS Independent',
               'Operating System :: POSIX',
               'Programming Language :: Python :: 3',
               'Topic :: Artistic Software',
               'Topic :: Games/Entertainment :: Arcade',
               'Topic :: Multimedia']
PLATFORMS = ['POSIX', 'Mac OS X', 'Windows']
LICENSE = 'GPLv3+'

def find_package_data(path):
    """Recursively collect EVERY file in path to a list."""
    oldcwd = os.getcwd()
    os.chdir(path)
    filelist = []
    for path, dirs, filenames in os.walk('.'):
        for name in filenames:
            filename = ((os.path.join(path, name)).replace('\\', '/'))
            filelist.append(filename.replace('./', 'data/'))
    os.chdir(oldcwd)
    return filelist


if 'install' in sys.argv or 'bdist_dumb' in sys.argv or \
     'bdist_rpm' in sys.argv:
    setup(name=NAME,
          version=VERSION,
          description=DESCRIPTION,
          long_description=LONG_DESCRIPTION,
          author=AUTHOR,
          author_email=AUTHOR_EMAIL,
          url=URL,
          download_url=DOWNLOAD_URL,
          classifiers=CLASSIFIERS,
          platforms=PLATFORMS,
          license=LICENSE,
          scripts=['scripts/anikom15'],
          packages=['acg'],
          package_dir={'acg': 'src/acg'},
          package_data={'acg': find_package_data('src/acg/data')})
elif 'bdist_wininst' in sys.argv or 'bdist_msi' in sys.argv:
    setup(name=NAME,
          version=VERSION,
          description=DESCRIPTION,
          long_description=LONG_DESCRIPTION,
          author=AUTHOR,
          author_email=AUTHOR_EMAIL,
          url=URL,
          download_url=DOWNLOAD_URL,
          classifiers=CLASSIFIERS,
          platforms=PLATFORMS,
          license=LICENSE,
          scripts=['scripts/anikom15', 'scripts/install-win32.py'],
          packages=['acg'],
          package_dir={'acg': 'src/acg'},
          package_data={'acg': find_package_data('src/acg/data')},
          data_files=[('Icons', ['data/anikom15.ico'])])
else:
    setup(name=NAME,
          version=VERSION,
          description=DESCRIPTION,
          long_description=LONG_DESCRIPTION,
          author=AUTHOR,
          author_email=AUTHOR_EMAIL,
          url=URL,
          download_url=DOWNLOAD_URL,
          classifiers=CLASSIFIERS,
          platforms=PLATFORMS,
          license=LICENSE,
          scripts=['scripts/anikom15', 'scripts/clean',
                   'scripts/install-win32.py'],
          packages=['acg'],
          package_dir={'acg': 'src/acg'},
          package_data={'acg': find_package_data('src/acg/data')},
          data_files=[('Icons', ['data/anikom15.ico'])])
