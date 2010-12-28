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
#

import gconf
import os
import sys
import ConfigParser
import config
import prefs

import gettext
_ = gettext.gettext

BD_KEY = "/apps/gnoduino/board"

class Board(object):
	def __init__(self):
		global client
		self.board = 0
		self.boards = []
		self.programmers = []
		self.defaults = []
		conf = ConfigParser.RawConfigParser()
		client = gconf.client_get_default()
		if client.get_int(BD_KEY): config.cur_board = client.get_int(BD_KEY)
		try:
			path = os.path.join(os.getcwd(), "BOARDS")
			if os.path.exists(path):
				conf.read(path)
			else: raise
		except:
			try:
				path = os.path.join(sys.prefix, "share", "gnoduino", "BOARDS")
				if os.path.exists(path):
					conf.read(path)
				else: raise
			except Exception,e:
				print e
				raise SystemExit(_("Cannot load BOARDS file. Exiting."))
		c = 1
		for i in conf.sections():
			v = dict(conf.items(i))
			v['id'] = c
			v['desc'] = i
			self.boards.append(v)
			c = c + 1
		p = prefs.preferences()
		if config.cur_board == -1:
			config.cur_board = self.getBoardIdByName(p.getValue("board")) - 1
			client.set_int(BD_KEY, config.cur_board)

	def getBoards(self):
		return self.boards

	def getBoard(self):
		return config.cur_board

	def getBoardMemory(self, id):
		return self.boards[id]['maximum_size']

	def getBoardMCU(self, id):
		return self.boards[id]['mcu']

	def getBoardFCPU(self, id):
		return self.boards[id]['f_cpu']

	def getPGM(self, id):
		return self.boards[id]['protocol']

	def getPGMSpeed(self, id):
		return self.boards[id]['speed']

	def getFuseLock(self, id):
		return self.boards[id]['lock_bits']

	def getFuseUnlock(self, id):
		return self.boards[id]['unlock_bits']

	def getFuseHigh(self, id):
		return self.boards[id]['high_fuses']

	def getFuseLow(self, id):
		return self.boards[id]['low_fuses']

	def getFuseExtended(self, id):
		return self.boards[id]['extended_fuses']

	def getPath(self, id):
		return self.boards[id]['path']

	def getBootloader(self, id):
		return self.boards[id]['file']

	def setBoard(self, id):
		print "set board %d" % (id -1)
		config.cur_board = (id - 1)
		client.set_int(BD_KEY, config.cur_board)

	def getBoardIdByName(self, name):
		if name == None: return 1
		for i in self.boards:
			if i['name'] == name:
				return i['id']
