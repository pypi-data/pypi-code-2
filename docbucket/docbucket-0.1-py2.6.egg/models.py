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

import mongoengine as me
from datetime import datetime
from whoosh import fields, index
from django.conf import settings


class DocumentClass(me.Document):
	name = me.StringField(max_length=200, required=True)
	slug = me.StringField(max_length=20, required=True)

	def __unicode__(self):
		return self.name


class Thumbnail(me.EmbeddedDocument):
	size = me.StringField(max_length=30, required=True)
	image = me.FileField()


class Document(me.Document):
	name = me.StringField(max_length=200, required=True)
	attachment = me.FileField()
	thumbnails = me.ListField(me.EmbeddedDocumentField(Thumbnail))
	physical_location = me.StringField(max_length=50)
	
	# Doc metas:
	page_number = me.IntField()
	created = me.DateTimeField(default=datetime.now)
	access = me.DateTimeField(default=None)
	document_class = me.ReferenceField(DocumentClass)
	
	# Search engine stuff:
	content = me.DictField()

	def get_thumbnail(self, size):
		''' Get the thumbnail of specified size. '''
		if not self.thumbnails:
			self.reload()
		found = [t for t in self.thumbnails if t.size == size]
		if found:
			return found[0].image
		else:
			return None

	def delete(self, *args, **kwargs):
		ix = index.open_dir(settings.WHOOSH_INDEX)
		ix.delete_by_term('doc_id', str(self.id))
		ix.commit()
		return super(Document, self).delete(*args, **kwargs)

#
# Search engine stuff:
#

WHOOSH_SCHEMA = fields.Schema(name=fields.TEXT(stored=True),
                              content=fields.TEXT,
                              doc_id=fields.ID(stored=True, unique=True))
