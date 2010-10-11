# $Id: wxRemAbout.py 8 2006-05-08 15:14:25Z dag $
import os.path, wx, wx.html
from nts.ntsVersion import version
from nts.ntsData import copyright

description = """\
nts (note taking simplified) provides a simple format for using 
text files to store notes, a command line interface for viewing
notes in a variety of convenient ways and a wx(python)-based
GUI for creating and modifying notes as well as viewing them.
"""

# license = "GNU General Public License (GPL)"
license = """\
This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2 of
the License, or (at your option) any later version. 
[ http://www.gnu.org/licenses/gpl.html ]

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
the GNU General Public License for more details.
"""

class About(wx.Panel):

	def __init__(self, parent):
		# First we create and fill the info object
		global version
		wx.Panel.__init__(self, parent, -1)
		info = wx.AboutDialogInfo()
		info.Name = "nts"
		info.Version = "%s" % version
		info.Copyright = "(C) %s Daniel A. Graham" % copyright
		info.Description = description
		info.WebSite = ("http://www.duke.edu/~dgraham/NTS", 
			"nts home page")
		info.Developers = [ "Daniel A. Graham <daniel.graham@duke.edu>", ]

		info.License = license

		# Then we call wx.AboutBox giving it that info object
		wx.AboutBox(info)
