#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  Copyright (c) 2009, 2010, 2011 Anaël Verrier
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, version 3 only.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys

from distutils.core import setup
from distutils.command import build_scripts
from distutils.command.install import install


scripts = {'helm_launcher.py': 'helm'}
conf_files = ['config.py']




###############################################################################
# This fucking distutils don't let me install the scripts under a different   #
# name. So here is an evil hack (yeah it's a lovely monkey patch).            #
#                                                                             #
# Please do not read if you are a minor!                                      #
###############################################################################
from os.path import basename

def my_basename(path):
    if path in scripts:
        return scripts[path]

    return basename(path)


orig_copy_scripts = build_scripts.build_scripts.copy_scripts

def my_copy_scripts(self):
    build_scripts.os.path.basename = my_basename
    orig_copy_scripts(self)
    build_scripts.os.path.basename = basename

build_scripts.build_scripts.copy_scripts = my_copy_scripts
###############################################################################
# This is the end of this marvelous piece of code.                            #
# Thanks distutils!                                                           #
###############################################################################




###############################################################################
# And another one evil hack for this fucking distutils. We can not handle     #
# configuration files with distutils to respect unixen's FHS. Because when we #
# use --prefix=/usr/local, the config files will be installed in /etc/foo.cfg #
# or /usr/etc/foo.cfg depending of what we write in data_files argument       #
# (('/etc', ['foo.cfg']) or ('etc', ['foo.cfg'])).                            #
# Complete description of this problem (and the solution) can be found on:    #
# http://stackoverflow.com/questions/3325606/                                 #
#                                                                             #
# Please do not read if you are a minor!                                      #
###############################################################################
class my_install(install):
    def finalize_options(self):
        if self.prefix in (None, '/usr', '/usr/local'):
            self.conf_prefix = '/etc/xdg'
        else:
            self.conf_prefix = os.path.join(self.prefix, 'etc/xdg')

        install.finalize_options(self)

    def install_conf(self):
        dest_dir = os.path.join((self.root or ''), self.conf_prefix, 'helm')
        self.mkpath(dest_dir)
        for file_ in conf_files:
            dest = os.path.join(dest_dir, os.path.basename(file_))
            self.copy_file(file_, dest)

    def run(self):
        install.run(self)
        self.install_conf()
###############################################################################
# This is the end of this (yet another) marvelous piece of code.              #
# Thanks distutils!                                                           #
###############################################################################




long_description = """Helm is a system monitor written in python.
He uses GTK and Cairo for the rendering.

You can customize the widgets to display and create your own. You can also
create your own views and models.

Helm is distributed under the GPLv3 license."""

setup(name='helm',
      version='0.2',
      description='Helm is a system monitor released under GNU GPLv3.',
      long_description=long_description,
      author=u'Anaël Verrier',
      author_email='elghinn@free.fr',
      license='GNU GPLv3',
      url='http://helm.last-exile.org/',
      download_url='http://helm.last-exile.org/#download',
      provides=['helm'],
      keywords=['monitoring'],
      classifiers=(
          'Development Status :: 4 - Beta',
          'Environment :: X11 Applications',
          'Environment :: X11 Applications :: GTK',
          'Intended Audience :: End Users/Desktop',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Topic :: System :: Monitoring',
          ),
      packages=['helm', 'helm.models', 'helm.views', 'helm.widgets'],
      scripts=scripts,
      cmdclass={'install': my_install,},
      )
