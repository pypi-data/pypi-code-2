##############################################################################
#
# OrderableReferenceField - Orderable Reference Field
# Copyright (C) 2006 Zest Software
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
##############################################################################
"""
$Id:  $
"""
__author__ = """Jean-Paul Ladage <j.ladage@zestsoftware.nl>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *

from Products.OrderableReferenceField.config import *
from Products.OrderableReferenceField import OrderableReferenceField
from Products.OrderableReferenceField import OrderableReferenceWidget


schema = Schema((
    OrderableReferenceField(
        name = 'contact',
        vocabulary_display_path_bound = "-1",
        widget = OrderableReferenceWidget(label='Contact'),
        allowed_types = ('ContactPerson', ),
        multiValued = 1,
        relationship = 'favorite_contact'),
    ),)

Favorite_schema = BaseSchema.copy() + schema.copy()


class MyFavorite(BaseContent):
    """A group of favorite contacts
    """
    security = ClassSecurityInfo()

    archetype_name = meta_type = portal_type = 'MyFavorite'
    schema = Favorite_schema


registerType(MyFavorite, PROJECTNAME)
