# -*- coding: utf8 -*-
__version__ = "$Revision: 137 $ $Date: 2011-02-27 21:14:48 +0100 (dim. 27 févr. 2011) $"
__author__  = "Guillaume Bour <guillaume@bour.cc>"
__license__ = """
	Copyright (C) 2010-2011, Guillaume Bour <guillaume@bour.cc>

	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU Affero General Public License as
	published by the Free Software Foundation, version 3.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU Affero General Public License for more details.

	You should have received a copy of the GNU Affero General Public License
	along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import sqlite3, cgi
from mother.callable import Callable, callback
from tag  import *
from link import *


class Strawberry(Callable):
	def __init__(self, db=None, context=None):
		self.db	 = db
		#db.create()

		# create default link
		try:
			Link(
				link = 'http://devel.bour.cc/strawberry',
				name = 'strawberry project home page',
				stars = 5,
				valid = True,
				
				tags  = [Tag(id=1, name='bookmarks service')],
			).save()
		
		except Exception, e:
			print e

