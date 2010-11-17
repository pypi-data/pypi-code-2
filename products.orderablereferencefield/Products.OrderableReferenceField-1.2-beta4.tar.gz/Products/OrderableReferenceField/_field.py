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
$Id: _field.py 9913 2008-07-23 22:42:39Z aclark $
"""

from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.Archetypes.Registry import registerField, registerWidget


class OrderableReferenceWidget(atapi.ReferenceWidget):
    _properties = atapi.ReferenceWidget._properties.copy()
    _properties.update({
        'type': 'orderablereference',
        'macro': 'orderablereference',
        'size': '6',
        'helper_js': ('orderablereference.js',),
        })


class OrderableReferenceField(atapi.ReferenceField):
    _properties = atapi.ReferenceField._properties.copy()
    _properties.update({
        'multiValued': True,
        'widget': OrderableReferenceWidget,
        })

    security = ClassSecurityInfo()

    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):
        atapi.ReferenceField.set(self, instance, value, **kwargs)

        if value is None:
            value = ()

        if not isinstance(value, (list, dict)):
            value = value,

        #convert objects to uids if necessary
        uids = []
        for v in value:
            if isinstance(v, str):
                uids.append(v)
            else:
                uids.append(v.UID())

        refs = instance.getReferenceImpl(self.relationship)
        
        for ref in refs:
            index = uids.index(ref.targetUID)
            ref.order = index

    security.declarePrivate('get')
    def get(self, instance, **kwargs):
        refs = instance.getReferenceImpl(self.relationship)
        refs.sort(lambda a,b:cmp(getattr(a,'order',None), getattr(b,'order',None)))
        return [ref.getTargetObject() for ref in refs]

    security.declarePrivate('getRaw')
    def getRaw(self, instance, **kwargs):
        refs = instance.getReferenceImpl(self.relationship)
        refs.sort(lambda a,b:cmp(getattr(a,'order',None), getattr(b,'order',None)))
        return [ref.targetUID for ref in refs]



registerWidget(
    OrderableReferenceWidget,
    title='Orderable Reference',
    used_for=('Products.OrderableReferenceField.OrderableReferenceField',)
    )

registerField(
    OrderableReferenceField,
    title="Orderable Reference Field",
    description=("Reference field that knows about an order of refs.")
    )

#addon for Relations
try:
    from Products.Relations.field import RelationField
except ImportError:
    class RelationField(atapi.ReferenceField):
        pass


class OrderableRelationField(RelationField):
    _properties = RelationField._properties.copy()
    _properties.update({
        'multiValued': True,
        'widget': OrderableReferenceWidget,
        })

    security = ClassSecurityInfo()

    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):
        RelationField.set(self, instance, value, **kwargs)

        if value is None:
            value = ()

        if not isinstance(value, (list, dict)):
            value = value,

        #convert objects to uids if necessary
        uids = []
        for v in value:
            if isinstance(v, str):
                uids.append(v)
            else:
                uids.append(v.UID())

        refs = instance.getReferenceImpl(self.relationship)
        
        for ref in refs:
            index = uids.index(ref.targetUID)
            ref.order = index

    security.declarePrivate('get')
    def get(self, instance, **kwargs):
        refs = instance.getReferenceImpl(self.relationship)
        refs.sort(lambda a,b:cmp(getattr(a,'order',None), getattr(b,'order',None)))
        return [ref.getTargetObject() for ref in refs]

    security.declarePrivate('getRaw')
    def getRaw(self, instance, **kwargs):
        refs = instance.getReferenceImpl(self.relationship)
        refs.sort(lambda a,b:cmp(getattr(a,'order',None), getattr(b,'order',None)))
        return [ref.targetUID for ref in refs]

registerField(
    OrderableRelationField,
    title="Orderable Relation Field",
    description=("Relation field that knows about an order of refs.")
    )
