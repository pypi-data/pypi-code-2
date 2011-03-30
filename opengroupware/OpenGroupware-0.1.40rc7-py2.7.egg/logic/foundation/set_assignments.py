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
        self.collection    = params.get('collection', None)
        self.assignments   = params.get('assignments', None)
        self.insert   = params.get('insert', None)
        self.membership  = params.get('membership', None)

    def check_parameters(self):
        if (self.collection is None):
            raise CoilsException('No collection provided to set-assignments')
        if ((self.membership is not None) and (self.insert is not None)):
            raise CoilsException('Only insert or membership can be provided to set-assignments')

    def map_entities(self, entities):
        values =  []
        if (entities is not None):
            if (isinstance(entities, list)):
                for entity in entities:
                    values.append({'assignedObjectId' : entity.object_id})
            else:
                raise CoilsException('Provided entities must be in a list')
            self.assignments = values

    def map_membership(self):
        #adds provded entities to collection
        self.map_entities(self.membership)
        self.map_assignments()
        for assignment in self.collection.assignments:
            self.assignments.append(assignment)

    def map_assignments(self):
        result = []
        for assignment in self.assignments:
            x = Assignment()
            x.take_values(assignment, COILS_COLLECTION_ASSIGNMENT_KEYMAP)
            x.collection_id = self.collection.object_id
            result.append(x)
        self.assignments = result

    def run(self):
        db = self._ctx.db_session()
        self.check_parameters()
        if (self.membership is None):
            #removes current assignments and inserts given
            self.map_entities(self.insert)
            self.map_assignments()
        else:
            self.map_membership()
        # TODO: Check for write access!
        assignments    = [ ]
        max_key        = 0
        #
        # Sync assignments with provides list of assignments
        #
        for x in self.assignments:
            for y in self.collection.assignments:
                if (x.assigned_id == int(y.assigned_id)):
                    # Take the sort_key from the provided entity, if a sort_key value
                    # was specified; otherwise all we need to know is that the assignment
                    # is still present
                    if x.sort_key is not None:
                        y.sort_key = x.sort_key
                        if (y.sort_key > max_key):
                            max_key = y.sort_key
                    assignments.append(x)
                    break
            else:
                # This is a new assignment
                z = CollectionAssignment()
                z.take_values(x, None)
                if (z.sort_key is not None):
                    if (z.sort_key > max_key):
                        max_key = z.sort_key
                db.add(z)
                assignments.append(z)
        #
        # Purge expired assignments
        #
        unassignments  = [ ]  # Will accumulate the list of expired assignment object ids
        assigned_ids = [x.assigned_id for x in assignments]
        for x in self.collection.assignments:
            if (x.assigned_id not in assigned_ids):
                unassignments.append(x.object_id)
        assigned_ids = None
        if (len(unassignments) > 0):
            # Delete the dangling assignments
            query = db.query(CollectionAssignment).\
                    filter(and_(CollectionAssignment.collection_id == self.collection.object_id,
                                 CollectionAssignment.object_id.in_(unassignments)))
            count = 0
            for x in query.all():
                db.delete(x)
                count = count + 1
            self.log.debug('{0} assignments deleted from collection.'.format(count))
        #
        # Fix NULL sort keys
        #
        for assignment in assignments:
            if (assignment.sort_key is None):
                max_key += 1
                assignment.sort_key = max_key
