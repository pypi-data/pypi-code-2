# Copyright (c) 2010 by Yaco Sistemas
#
# This file is part of django-playerlayer.
#
# django-playerlayer is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# django-playerlayer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with django-playerlayer.  If not, see <http://www.gnu.org/licenses/>.

from django.core.exceptions import ImproperlyConfigured


class ItemData(dict):

    def __init__(self, item):
        self.item = item
        self.collection = item.collection

    def __getitem__(self, key):
        try:
            return super(ItemData, self).__getitem__(key)
        except KeyError:
            fields_slugs = ['"%s"' % f.slug for f in self.collection.fields.all()]
            raise ImproperlyConfigured(
                'You want to get the "%s" field of "%s" item, but the collection only has defined these fields: %s' %
                (key, self.item, ', '.join(fields_slugs))
            )
