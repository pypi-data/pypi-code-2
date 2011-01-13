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
# THE SOFTWARE.
#
import sys, time
import logging
from datetime    import datetime
from backend     import Backend
from alchemy     import ObjectInfo, Appointment, ProjectAssignment, Participant, \
                         CompanyAssignment, Contact, Enterprise, Team, Project, \
                         Task, Team, Collection, CollectionAssignment

COILS_TYPEMANAGER_CACHE = { }

class TypeManager:

    __slots__ = ('_log', '_orm')

    def __init__(self):
        self._log =logging.getLogger("typemanager")
        self._orm = Backend().db_session()

    def check_cache(self, object_id):
        # Expire entries
        try:
            if (COILS_TYPEMANAGER_CACHE.has_key(object_id)):
                return COILS_TYPEMANAGER_CACHE[object_id][0]
        except TypeError, e:
            self._log.error('objectId was {0} = {1}'.format(type(object_id), object_id))
            self._log.exception(e)
        except Exception, e:
            self._log.exception(e)
        return None

    def set_cache(self, object_id, kind):
        COILS_TYPEMANAGER_CACHE[object_id] = []
        COILS_TYPEMANAGER_CACHE[object_id].append(kind)
        COILS_TYPEMANAGER_CACHE[object_id].append(datetime.now())
        return kind

    def get_type(self, object_id):
        # MEMOIZE ME!
        x = self.check_cache(object_id)
        if (x is not None):
            return x
        query = self._orm.query(ObjectInfo).filter(ObjectInfo.object_id == object_id)
        data = query.all()
        if (len(data) == 0):
            return self._deep_search(object_id)
        elif (len(data) > 0):
            kind = str(data[0].kind)
            if (kind == "Date"):
                return self.set_cache(object_id, 'Appointment')
            elif (kind == "Job"):
                return self.set_cache(object_id, 'Task')
            elif (kind == "Person"):
                return self.set_cache(object_id, 'Contact')
            elif (kind == "AppointmentResource"):
                return self.set_cache(object_id, 'Resource')
            elif (kind == "DateCompanyAssignment"):
                return self.set_cache(object_id, 'participant')
            elif (kind == "DateCompanyAssignment"):
                return self.set_cache(object_id, 'participant')
            else:
                return self.set_cache(object_id, kind)
        else:
            # It is not possible to get here?
            return 'Unknown'

    def filter_ids_by_type(self, object_ids, entity_name):
        groups = self.group_ids_by_type(object_ids)
        if (entity_name in groups):
            return groups[entity_name]
        return []

    def group_ids_by_type(self, object_ids):
        result = { }
        for object_id in object_ids:
            entity_name = self.get_type(object_id)
            if ( result.has_key(entity_name) ):
                result[entity_name].append(object_id)
            else:
                result[entity_name] = [ object_id ]
        return result

    def group_by_type(self, **params):
        if (params.has_key('objects')):
            return self._group_objects(params['objects'])
        elif (params.has_key('ids')):
            return self._group_ids(params['ids'])

    def _group_objects(self, entities):
        start = time.time()
        result = { }
        for entity in entities:
            entity_name = entity.__entityName__
            if (result.has_key(entity_name)):
                result[entity_name].append(entity)
            else:
                result[entity_name] = [ entity ]
        end = time.time()
        self._log.debug('duration of grouping was %0.3fs' % (end - start))
        return result

    def _group_ids(self, object_ids):
        result = { }
        for object_id in object_ids:
            entity_name = self.get_type(object_id)
            if ( result.has_key(entity_name) ):
                result[entity_name].append(object_id)
            else:
                result[entity_name] = [ object_id ]
        return result

    def _deep_search(self, object_id):
        #TODO: Update obj_info ?
        #HACK: This entire method!
        # Types are: Appointment, Contact, Enterprise, participant (?), Project,
        #            Resource (?), Task,
        self._log.warn("Performing deep search for type of objectId#%s", object_id)
        # Appointment
        query = self._orm.query(Appointment).filter(Appointment.object_id == object_id)
        data = query.all()
        if (len(data) > 0):
            query = None
            data = None
            return self.set_cache(object_id, 'Appointment')
        # Contact
        query = self._orm.query(Contact).filter(Contact.object_id == object_id)
        data = query.all()
        if (len(data) > 0):
            query = None
            data = None
            return self.set_cache(object_id, 'Contact')
        # Enterprise
        query = self._orm.query(Enterprise).filter(Enterprise.object_id == object_id)
        data = query.all()
        if (len(data) > 0):
            query = None
            data = None
            return self.set_cache(object_id, 'Enterprise')
        # participant
        query = self._orm.query(Participant).filter(Participant.object_id == object_id)
        data = query.all()
        if (len(data) > 0):
            query = None
            data = None
            return self.set_cache(object_id, 'participant')
        # Project
        query = self._orm.query(Project).filter(Project.object_id == object_id)
        data = query.all()
        if (len(data) > 0):
            query = None
            data = None
            return self.set_cache(object_id, 'Project')
        # Team
        query = self._orm.query(Team).filter(Team.object_id == object_id)
        data = query.all()
        if (len(data) > 0):
            query = None
            data = None
            return self.set_cache(object_id, 'Team')
        # Task
        query = self._orm.query(Task).filter(Task.object_id == object_id)
        data = query.all()
        if (len(data) > 0):
            query = None
            data = None
            return self.set_cache(object_id, 'Task')
        # Collection
        #query = self._orm.query(Collection).filter(Collection.object_id == object_id)
        #data = query.all()
        #if (len(data) > 0):
        #    query = None
        #    data = None
        #    return "Collection"
        #self._log.warn("Deep search failed to find type for objectId#%s", object_id)
        return self.set_cache(object_id, 'Unknown')