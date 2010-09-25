# gnoduino - Python Arduino IDE implementation
# Copyright (C) 2010  Lucian Langa
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


import os
import sys

import gettext
_ = gettext.gettext

class preferences(object):

	def __init__(self):
		self.defaults = []
		try:
			path = os.path.expanduser('~/.arduino/preferences.txt')
			if os.path.exists(path):
				f = open(path)
			else: raise
		except:
			try:
				path = os.path.join(sys.prefix, "share", "gnoduino", "preferences.txt")
				if os.path.exists(path):
					f = open(path)
				else: raise
			except Exception,e:
				print e
				raise SystemExit(_("Cannot load defaults file. Installation problem."))

		for i in f:
			self.defaults.append(i.rstrip("\n").split("="))

	def getValue(self, value):
		for i in self.defaults:
			if i[0] == value:
				return i[1]
		return None
