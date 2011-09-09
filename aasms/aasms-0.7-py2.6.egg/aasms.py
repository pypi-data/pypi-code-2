# File: aasms.py
# Author: Michael Stevens <mstevens@etla.org>
# Copyright (C) 2010

#	 This file is part of aasms.
#
#	 aasms is free software: you can redistribute it and/or modify
#	 it under the terms of the GNU General Public License as published by
#	 the Free Software Foundation, either version 3 of the License, or
#	 (at your option) any later version.
#
#	 aasms is distributed in the hope that it will be useful,
#	 but WITHOUT ANY WARRANTY; without even the implied warranty of
#	 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	 GNU General Public License for more details.
#
#	 You should have received a copy of the GNU General Public License
#	 along with aasms.	If not, see <http://www.gnu.org/licenses/>.

import urllib, urllib2

SMS_URL="http://sms.aaisp.net.uk/sms.cgi"

class SmsSender(object):

	def __init__(self, username = None, iccid = None, password = None):
		"""Create a new SmsSender.

		Creates a new SmsSender. Requires either username or iccid, and password as assigned by aaisp.net.
		"""

		if username and iccid:
			raise SmsError("must not have both username and iccid")
		
		self.username = username
		self.iccid = iccid
		self.password = password

	def send(self,
			 message,
			 destination = None,
			 limit = None,
			 sendtime = None,
			 replace = False,
			 flash = False,
			 report = False,
			 costcentre = None,
			 private = False,
			 udh = None,
			 originator = None):
		"""Send a SMS message.

		Warning: This is the bit that's billable!
		"""

		if not (destination or self.iccid):
			raise SmsError("Must have a destination or iccid")

		if destination and self.iccid:
			raise SmsError("Got destination and iccid, don't know where to send message")

		if self.iccid and not originator:
			raise SmsError("iccid requires originator")
		
		fields = {
				"password" : self.password,
				"message" : message,
				}

		if destination != None:
			fields["destination"] = destination

		if self.iccid != None:
			fields["iccid"] = self.iccid

		if self.username != None:
			fields["username"] = self.username
			
		if limit:
			fields["limit"] = limit

		if sendtime:
			fields["sendtime"] = sendtime

		if replace:
			fields["replace"] = 1

		if flash:
			fields["flash"] = 1

		if report:
			fields["report"] = 1

		if costcentre:
			fields["costcentre"] = 1

		if private:
			fields["private"] = 1

		if udh:
			fields["udh"] = udh

		if originator:
			fields["originator"] = originator

		data = urllib.urlencode(fields)
		response = urllib2.urlopen(SMS_URL, data)

		line1 = response.readline()
		status = response.readline()

		if status.startswith("ERR:"):
			raise SmsError(status[:-2])

class SmsError(Exception):
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)

	def error(self):
		"""Get the error message as reported by aaisp.net or ourselves"""

		return self.value
