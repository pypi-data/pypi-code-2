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
$Id$
"""

from Products.CMFCore import utils as cmfutils
from Products.CMFCore import permissions

from Products.Archetypes.atapi import *
from Products.Archetypes import listTypes

from Products.OrderableReferenceField._field import OrderableReferenceField
from Products.OrderableReferenceField._field import OrderableReferenceWidget
from Products.OrderableReferenceField.config import *


def initialize(context):
    """Initializer called when used as a Zope 2 product."""

    import Products.OrderableReferenceField.examples

    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME), PROJECTNAME)

    cmfutils.ContentInit(
        PROJECTNAME + ' Content',
        content_types = content_types,
        permission = permissions.AddPortalContent,
        extra_constructors = constructors,
        fti = ftis,
    ).initialize(context)
