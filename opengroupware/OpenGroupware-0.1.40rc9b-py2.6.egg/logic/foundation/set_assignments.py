#
# Copyright (c) 2009 Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#
from sqlalchemy       import *
from coils.core       import *
from keymap           import COILS_COLLECTION_ASSIGNMENT_KEYMAP, COILS_COLLECTION_KEYMAP

class Assignment(KVC):

    def __init__(self):
        self.collection_id      = None
        self.sort_key           = None
        self.assigned_id        = None

    def __repr__(self):
        return '<Assignment CollectionId#{0} AssignedId#{1} SortKey:{2}>'.\
                format(self.collection_id, self.assigned_id, self.sort_key)


class SetAssignments(Command):
    __domain__ = "collection"
    __operation__ = "set-assignments"
    mode = None

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        self.collection  = params.get('collection', None)  ## The collection in question
        self.insert      = params.get('insert',     None)  ## Add these entities
        self.update      = params.get('update',     None)  ## Sync to this membership

    def check_parameters(self):
        if (self.collection is None):
            raise CoilsException('No collection provided to set-assignments')

    def get_max_key(self):
        max_key = 0
        for assignment in self.collection.assignments:
            if (assignment.sort_key > max_key):
                max_key = assignment.sort_key
        return max_key

    def get_assigned_ids(self):
        return [x.assigned_id for x in self.collection.assignments]

    def run(self):
        db = self._ctx.db_session()
        self.check_parameters()
        max_key      = self.get_max_key()
        assigned_ids = self.get_assigned_ids()
        # TODO: Check for write access!
        if (self.insert is not None):
            # INSERT mode, no sync other than keeping out entities that are already assigned
            if (not isinstance(self.insert, list)):
                raise CoilsException('Insert value must be a list of entities, received type "{0}"'.format(type(self.insert)))
            counter = 0
            insert_ids = [x.object_id for x in self.insert]
            for object_id in insert_ids:
                if (object_id not in assigned_ids):
                    assigned_ids.append(object_id)
                    max_key += 1
                    counter += 1
                    x = CollectionAssignment()
                    x.collection_id = self.collection.object_id
                    x.assigned_id = object_id
                    x.sort_key = max_key
                    db.add(x)
            self._result = (counter, 0, 0)
            return
        elif (self.update is not None):
            # UPDATE mode, sync the collection assignments to be those in the provided list; that list
            # may be Omphalos dictionaries of entities or ORM entity objects.  If Omphalos dictionaries
            # they MUST ALL be first-class entity representations or ALL be collectionAssignment entities.
            stats =  [0, 0, 0]
            if (not isinstance(self.update, list)):
                raise CoilsException('Update value must be a list, received type "{0}"'.format(type(self.update)))
            if (len(self.update) == 0):
                # Short circuit - delete all assignments
                counter = 0
                for x in self.collection.assignments:
                    db.delete(x)
                    stats[2] += 1
                self._result = stats
                return
            meta = { }
            if (isinstance(self.update[0], dict)):
                if 'assignedObjectId' in self.update[0]:
                    # The update data is a list of Omphalos collectionAssignment entities
                    for x in self.update:
                        meta[int(x.get('assignedObjectId'))] = { 'sortKey': x.get('sortKey', None) }
                else:
                    for x in self.update:
                        if 'objectId' in x:
                            meta[int(x.get('objectId'))] = { }
            else:
                for x in self.update:
                    meta[x.object_id] = { }
            removes = self.get_assigned_ids()
            # Update Loop
            for x in self.collection.assignments:
                if (x.assigned_id in meta):
                    sort_key = meta[x.assigned_id].get('sortKey', None)
                    if (sort_key is not None):
                        x.sort_key = sort_key
                    del meta[x.assigned_id] # Existing assignment updated, remove from meta
                    removes.remove(x.assigned_id) # Remove this id from the ids to be removed
                    stats[1] += 1
            # What items were not removed from menta in the update loop get added
            for k, v in meta.iteritems():
                kind = self._ctx.type_manager.get_type(k)
                # TODO: Filter out dis-allowed kinds, they must all be first-class proper entities
                z = CollectionAssignment()
                z.collection_id = self.collection.object_id
                z.assigned_id   = k
                if (v.get('sortKey', None) is not None):
                    z.sort_key = v.get('sortKey')
                else:
                    max_key += 1
                    z.sort_key = max_key
                z.entity_name = kind
                db.add(z)
                stats[0] += 1
            # Purge expired assignments
            if (len(removes) > 0):
                query = db.query(CollectionAssignment).\
                        filter(and_(CollectionAssignment.collection_id == self.collection.object_id,
                                    CollectionAssignment.assigned_id.in_(removes)))
                for x in query.all():
                    db.delete(x)
                    stats[2] += 1
            self._result = stats
            return
        else:
            raise CoilsException('No appropriate mode for this collection::set-assignments')
