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


import glob
import time
import serial

class sconsole:
	def __init__(self):
		"""9600 8N1"""
		self.serial = serial.Serial(
			port='/dev/ttyS0',
			baudrate=9600,
			parity=serial.PARITY_NONE,
			stopbits=serial.STOPBITS_ONE,
			bytesize=serial.EIGHTBITS
		)
		self.serial.open()
		self.serial.isOpen()

	def __del__(self):
		self.serial.close()

	def scan(self):
		"""scan for available ports. return a list of device names."""
		return glob.glob('/dev/ttyS*') + glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')

	def read(self):
		while self.serial.inWaiting() > 0:
			return self.serial.read(self.serial.inWaiting())
		return None


	def updateConsole(self, console):
		b = console.get_buffer()
		cont = self.read()
		if cont:
			print cont
		if cont != None:
			if b and len(cont) > 1:
				cont = unicode(
					cont.replace('\x00', '.').decode('utf-8', 'replace').encode('utf-8'))
				b.insert(b.get_end_iter(), \
					cont)
				console.scroll_mark_onscreen(b.get_insert())
		return True

	def resetBoard(self):
		self.serial.setDTR(False)
		time.sleep(0.1)
		self.serial.setDTR(True)

	def clearConsole(self, w, console):
		b = console.get_buffer()
		b.delete(b.get_start_iter(), b.get_end_iter())
		b.set_text("")

	def getBaudrates(self):
		return [i[0] for i in self.serial.getSupportedBaudrates() if i[1] >= 300 and i[1] <= 1150000]

