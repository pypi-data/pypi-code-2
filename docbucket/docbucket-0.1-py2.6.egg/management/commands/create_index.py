#!/usr/bin/env python
#coding=utf8
#
#       Copyright 2010 Antoine Millet <antoine@inaps.org>
#
#       This file is part of DocBucket.
#       
#       Foobar is free software: you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation, either version 3 of the License, or
#       (at your option) any later version.
#       
#       Foobar is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

from django.core.management.base import NoArgsCommand, CommandError
from django.conf import settings
from docbucket.models import WHOOSH_SCHEMA
from whoosh import index
from whoosh.filedb.filestore import FileStorage
import os

class Command(NoArgsCommand):
	help = 'Create the index of search engine'

	def handle_noargs(self, *args, **options):
		if not os.path.exists(settings.WHOOSH_INDEX):
			os.mkdir(settings.WHOOSH_INDEX)
			ix = index.create_in(settings.WHOOSH_INDEX, WHOOSH_SCHEMA)
