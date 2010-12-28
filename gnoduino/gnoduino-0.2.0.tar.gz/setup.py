#!/usr/bin/python
#
# Arduino python implementation
# Copyright (C) 2010  Lucian Langa <cooly@gnome.eu.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import glob
import os
import re
import logging
import subprocess
from distutils.core import setup

def runProg(cmdline):
	sout = ""
	serr = ""
	logging.debug("CMD:-%s", cmdline)
	try:
		p = subprocess.Popen(cmdline,
			stdout = subprocess.PIPE,
			stderr = subprocess.STDOUT,
			stdin = subprocess.PIPE,
			close_fds = True)
		poll = select.poll()
		poll.register(p.stdout, select.POLLIN)
		while gtk.events_pending():
			gtk.main_iteration()
		(sout,serr) = p.communicate()
		while gtk.events_pending():
			gtk.main_iteration()
		if p.poll()==1: raise
	except:
		logging.debug("ERR:%s", sout)
		return (False, sout)
	return (True, sout)

def get_gnoduino_version():
	"""Get version from src/__init__.py."""
	text = open(os.path.join("src", "__init__.py"), "r").read()
	return re.search(r"__version__ *= *['\"](.*?)['\"]", text).group(1)

compline = "scripts/gen_boards.py"
(run, sout) = runProg(compline)
compline = "scripts/gen_programmers.py"
(run, sout) = runProg(compline)
compline = "scripts/gitlog.sh"
(run, sout) = runProg(compline)
data_files = [('share/gnoduino/ui', ['ui/main.ui']),
		('share/gnoduino/', ['BOARDS', 'ChangeLog', 'NEWS', 'PROGRAMMERS', 'preferences.txt']),
		('share/gnoduino/pixmaps', glob.glob('pixmaps/*.png')),
		('share/gnoduino/scripts', ['scripts/gen_boards.py', 'scripts/gen_programmers.py']),
]
for r,d,f in os.walk("hardware"):
	if ".git" not in r and f:
		data_files.append([os.path.join("share", "gnoduino", r), [os.path.join(r,i) for i in f]])
print data_files

setup(name='gnoduino',
	version=get_gnoduino_version(),
	description='Gnome Arduino IDE implementation',
	package_dir={'gnoduino': 'src'},
	packages = ['gnoduino'],
	scripts = ['gnoduino'],

	author='Lucian Langa',
	author_email='lucilanga@gnome.org',
	url='http://gnome.eu.org/evo/index.php/Gnoduino',
	license='GPL',
	platforms='linux',
	data_files = data_files
)

