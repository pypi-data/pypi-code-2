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
from datetime import datetime
import pytz, time
from coils.foundation  import *
from coils.core        import *
from coils.net         import *
#from render import Render
#from render_object import as_string, as_datetime, as_integer
#from render_account import render_account
#from render_timezone import render_timezone
from coils.core.omphalos import *

ZOGI_DEFAULT_SEARCH_LIMIT = 150

class API(Protocol):
    __pattern__   = 'RPC2'
    __namespace__ = 'zogi'
    __xmlrpc__    = True

    def __init__(self, context):
        self.context = context
        self.context.log.debug('zOGI API Handler Marshalled')

    #
    # Public API
    #

    def getAuditEntries(self, floor):
        # TODO: Implement
        return [ ]

    def getFavoritesByType(self, kind, detail):
        kind = kind.lower()
        if (kind in ['contact', 'enterprise', 'project']):
            x = self.context.run_command('{0}::get-favorite'.format(kind))
            if (len(x) > 0):
                result = Render.Results(x, detail, self.context)
                return result
        return [ ]

    def unflagFavorites(self, ids):
        # TODO: Implement
        # ids may be an array of IDs or a CSV string of IDs
        # What is the return value of this very rarely used function?
        return None

    def flagFavorites(self, ids):
        # TODO: Implement
        # ids may be an array of IDs or a CSV string of IDs
        # What is the return value of this very rarely used function?
        return None

    def getLoginAccount(self, detail=65535):
        # Status: Implemeted
        # http://code.google.com/p/zogi/wiki/getLoginAccount
        account = self.context.run_command('account::get')
        defaults = self.context.run_command('account::get-defaults')
        return render_account(account, defaults, detail, self.context)

    def getObjectById(self, object_id, detail_level = 0, flags = {}):
        # Status: Implemented
        # 'objectId=%d level=%d' % (object_id, detail_level)
        kind = self.context.type_manager.get_type(object_id)
        if (kind == 'Unknown'):
            result = { 'entityName': 'Unknown', 'objectId': object_id }
        else:
            x = getattr(self, '_get_%ss_by_ids' % kind.lower())([object_id])
            if ((x is not None) and (len(x) == 1)):
                result = Render.Result(x[0], detail_level, self.context)
            else:
                result = { 'entityName': 'Unknown', 'objectId': object_id }
        return result

    def getObjectsById(self, object_ids, detail_level):
        # Status: Implemented
        result = [ ]
        index = self.context.type_manager.group_ids_by_type(object_ids)
        for key in index.keys():
            #print '_get_%ss_by_ids' % key.lower()
            x = getattr(self, '_get_%ss_by_ids' % key.lower())(index[key])
            if (x is None):
                self.context.log.debug('result of Logic was None')
            else:
                self.context.log.debug('retrieved %d %s objects' % (len(x), key))
                result.extend(x)
        result = Render.Results(result, detail_level, self.context)
        return result

    def getNotifications(self, start, end):
        # TODO: Implement
        # http://code.google.com/p/zogi/wiki/getNotifications
        return [ ]

    def getObjectVersionsById(self, ids):
        # TODO: Implement
        # Result: [{'entityName': 'Appointment', 'version': [''], 'objectId': 29420},
        #          {'entityName': 'Enterprise', 'version': [3], 'objectId': 21060},
        #          {'entityName': 'Contact', 'version': [7], 'objectId': 10120}]
        # http://code.google.com/p/zogi/wiki/getObjectVersionsById
        return [ ]

    def getTypeOfObject(self, id):
        # TODO: Implement
        # http://code.google.com/p/zogi/wiki/getTypeOfObject
        return 'Unknown'

    def putObject(self, payload):
        # Status: Implemented
        # http://code.google.com/p/zogi/wiki/putObject
        if (isinstance(payload, dict)):
            if (payload.has_key('entityName')):
                entity_name = payload['entityName'].lower()
            if (payload.has_key('_FLAGS')):
                flags = payload['_FLAGS']
                if (isinstance(flags, str)):
                    flags = flags.split(',')
            else:
                flags = []
            result = getattr(self, '_put_%s' % entity_name)(payload, flags)
            if (result is not None):
                self.context.commit()
            result = Render.Result(result, 65535, self.context)
        else:
            raise CoilsException('Put entity has not entityName attribute')
        return result

    def deleteObject(self, payload, flags={}):
        # TODO: Implement
        # payload can be an object Id or an actual object
        # http://code.google.com/p/zogi/wiki/deleteObject
        if (isinstance(payload, int) or isinstance(payload, str)):
            object_id = int(payload)
        else:
            object_id = int(payload.get('objectId'))
        kind = self.context.type_manager.get_type(object_id)
        x = getattr(self, '_delete_%s' % kind.lower())(object_id, flags)
        if (x is None):
            return False
        self.context.commit()
        return x

    def searchForObjects(self, kind, criteria, detail, flags=None):
        # Status: Implemented
        # http://code.google.com/p/zogi/wiki/searchForObjects
        full_flags = { 'limit': 100, 'revolve': False, 'filter': None }
        if (flags is not None):
            if (isinstance(flags, dict)):
                for key in flags.keys():
                    if (key == 'limit'):
                        full_flags['limit'] = flags['limit']
                    elif (key == 'revolve'):
                        full_flags['revolve'] = flags['revolve']
        x = getattr(self, '_search_%s' % kind.lower())(criteria, full_flags)
        result = [ ]
        start = time.time()
        if (len(x) > 0):
            for y in x:
                if (hasattr(y, '__entityName__')):
                    # Result contains ORM
                    z = Render.Result(y, detail, self.context)
                    if (z is not None):
                        result.append(z)
                else:
                    result.append(y)
        self.context.log.info('Rendering searchForObjects results consumed {0}s'.format(time.time() - start))
        self.context.log.info('searchForObjects returning {0} entities'.format(len(result)))
        return result

    #
    # getObjectById methods
    #

    def _get_accounts_by_ids(self, ids):
        # TODO: Implement
        return [ ]

    def _get_appointments_by_ids(self, ids):
        x = self.context.run_command('appointment::get', ids=ids)
        return x

    def _get_contacts_by_ids(self, ids):
        x = self.context.run_command('contact::get', ids=ids )
        return x

    def _get_docs_by_ids(self, ids):
        #WARN: Stub
        return [ ]

    def _get_enterprises_by_ids(self, ids):
        x = self.context.run_command('enterprise::get', ids=ids )
        return x

    def _get_projects_by_ids(self, ids):
        x = self.context.run_command('project::get', ids=ids )
        return x

    def _get_resources_by_ids(self, ids):
        x = self.context.run_command('resource::get', ids=ids )
        return x

    def _get_tasks_by_ids(self, ids):
        x = self.context.run_command('task::get', ids=ids )
        return x

    def _get_teams_by_ids(self, ids):
        x = self.context.run_command('team::get', ids=ids )
        return x

    def _get_unknowns_by_ids(self, ids):
        # TODO: Implement
        return [ ]
        x = [ ]
        for object_id in ids:
            x.append({'entityName' : 'Unknown', 'objectId' : object_id})
        return x

    # searchForObjects methods

    def _search_account(self, criteria, flags):
        #TODO: Implement
        raise 'Not Implemented'

    def _search_appointment(self, criteria, flags):
        # TODO: extend the zOGI API to include support for startDate + timespan (in days?)
        result = [ ]
        params = {}
        # appointmentType (kinds of appointments)
        if (criteria.has_key('appointmentType')):
            params['kinds'] = criteria['appointmentType']
        # startDate
        if (criteria.has_key('startDate')):
            x = criteria['startDate']
            if (isinstance(x, str)):
                if (len(x) == 10):
                    x =  datetime.strptime(x, '%Y-%m-%d')
                    x.hour = 0
                    x.minute = 0
                elif (len(x) == 16):
                    x = datetime.strptime(x, '%Y-%m-%d %H:%M')
            params['start'] = x
        # endDate
        if (criteria.has_key('endDate')):
            x = criteria['endDate']
            if (isinstance(x, str)):
                if (len(x) == 10):
                    x =  datetime.strptime(x, '%Y-%m-%d')
                    x.hour = 23
                    x.minute = 59
                elif (len(x) == 16):
                    x = datetime.strptime(x, '%Y-%m-%d %H:%M')
            params['end'] = x
        # Clean up participants value if one provided
        # This is turned into a list of integers (presumed object-ids)
        # The appointment::get-range command will take care of the
        # internal ugliness of converting the object ids of resources
        # into resource names.
        if (criteria.has_key('participants')):
            parts = criteria['participants']
            if (isinstance(parts, int)):
                parts = [ parts ]
            elif (isinstance(parts, str)):
                r = [ ]
                for part in parts.split(','):
                    r.append(int(part.strip()))
                parts = r
            elif (isinstance(parts, list)):
                r = [ ]
                for part in parts:
                    r.append(int(part))
                parts = r
            else:
                raise CoilsException('Unable to parse participants value for search request.')
            params['participants'] = parts
        return self.context.run_command('appointment::get-range', **params)

    def _polish_company_search_params(self, criteria, flags):
        # Used by _search_contact and _search_enterprise
        params = { 'limit': flags.get('limit') }
        if ('revolve' in flags):
            if (flags['revolve'] == 'YES'):
                params['revolve'] = True
            else:
                params['revolve'] = False
        else:
            params['revolve'] = False
        if (isinstance(criteria, list)):
            params['criteria'] = criteria
        elif (isinstance(criteria, dict)):
            params['criteria'] = [ criteria ]
        else:
            raise 'Unable to comprehend criteria'
        return params

    def _search_contact(self, criteria, flags):
        params = self._polish_company_search_params(criteria, flags)
        return self.context.run_command('contact::search', **params)

    def _search_enterprise(self, criteria, flags):
        params = self._polish_company_search_params(criteria, flags)
        return self.context.run_command('enterprise::search', **params)

    def _search_project(self, criteria, flags):
        # TODO: Implement zOGI-ness
        # Supported keys: kind, name, number, objectId, ownerObjectId, and placeHolder
        # If a conjunction is specified (either "AND" or "OR") then the name and number
        # keys are compared fuzzy, otherwise all keys must match exactly [AND].
        query = [ ]
        if ('conjunction' in criteria):
            expression = 'ILIKE'
            conjunction = criteria['conjunction']
        else:
            expression = 'EQUALS'
            conjunction = 'AND'
        for key in ('kind','name', 'number', 'objectId', 'ownerObjectId', 'placeHolder'):
            if key in criteria:
                if (expression == 'EQUALS') and (isinstance(criteria.get(key), basestring)):
                    value = criteria.get(key)
                else:
                    value = '%{0}%'.format(criteria.get(key))
                query.append({ 'conjunction': conjunction,
                               'expression': expression,
                               'key': key,
                               'value': value } )
        return self.context.run_command('project::search', criteria=query,
                                                            limit=flags.get('limit', None))

    def _search_resource(self, criteria, flags):
        #Implemented: Implement "All Search", no criteria
        #Implemented: Implement "Exact Search", name or criteria
        #Implemented: "Fuzzy Search", indicated by any conjunction in criteria
        if (len(criteria) == 0):
            # All Search
            return self.context.run_command('resource::get')
        elif (isinstance(criteria, dict)):
            # Transform legacy zOGI search into a criteria search
            x = [ ]
            if ('conjunction' in criteria):
                conjunction = criteria['conjunction'].upper()
                expression = 'ILIKE'
                del criteria['conjunction']
            else:
                conjunction = 'AND'
                expression = 'EQUALS'
            for k in criteria:
                if (expression == 'ILIKE'):
                    value = '%{0}%'.format(criteria[k])
                else:
                    value = criteria[k]
                x.append({'key': k,
                          'value': value,
                          'expression': expression,
                          'conjunction': conjunction })
            return self.context.run_command('resource::search', criteria=x)
        elif (isinstance(criteria, list)):
            # Assume the search is a well-formed criteria server
            # WARN: This feature is not supported by legacy/Obj-C zOGI
            return self.context.run_command('resource::search', criteria=criteria)

    def _search_task(self, criteria, flags):
        result = [ ]
        params = {}
        if (isinstance(criteria, str)):
            if (criteria == 'archived'):
                return self.context.run_command('task::get-archived')
            elif (criteria == 'delegated'):
                return self.context.run_command('task::get-delegated')
            elif (criteria == 'todo'):
                return self.context.run_command('task::get-todo')
            elif (criteria == 'assigned'):
                return self.content.run_command('task::get-assigned')
        elif (isinstance(criteria, list)):
            # convert criteria to search qualified
            return self.context.run_command('task::search', criteria=criteria)
        raise CoilsException('Invalid search critieria')

    def _search_time(self, criteria, flags):
       utctime = self.context.get_utctime()
       is_dst = 0
       if (self.context.get_timezone().dst(utctime).seconds > 0):
            is_dst = 1
       return [{ 'entityName': 'time',
                  'gmtTime': as_datetime(utctime),
                  'isDST': is_dst,
                  'offsetFromGMT': as_integer(self.context.get_offset_from(utctime)),
                  'offsetTimeZone': as_string(self.context.get_timezone().zone),
                  'userTime': as_datetime(self.context.as_localtime(utctime)) }]

    def _search_timezone(self, criteria, flags):
        result = [ ]
        utctime = self.context.get_utctime()
        for tz_def in COILS_TIMEZONES:
            #tz = pytz.timezone(tz_def['code'])
            #is_dst = 0
            #if (tz.dst(utctime).seconds > 0):
            #    is_dst = 1
            #result.append({ 'abbreviation': tz_def['abbreviation'],
            #                'description': tz_def['description'],
            #                'entityName': 'timeZone',
            #                'isCurrentlyDST': is_dst,
            #                'offsetFromGMT': as_integer((86400 - tz.utcoffset(utctime).seconds) * -1),
            #                'serverDateTime': utctime.astimezone(tz)})
            result.append(render_timezone(tz_def['code'], self.context))
        return result

    def _search_team(self, criteria, flags):
        #TODO: Implement "All" query
        #TODO: Implement "Mine" query
        if (criteria == 'all'):
            return self.context.run_command('team::get')
        elif (criteria == 'mine'):
            return self.context.run_command('team::get', member_id=self.context.account_id)
        raise 'Not Implemented'

    # putObject methods

    def _put_account(self, payload, flags):
        # TODO: Implement
        raise 'Not Implemented'

    def _put_appointment(self, payload, flags):
        object_id = int(payload.get('objectId', 0))
        if (object_id == 0):
            appointment = self.context.run_command('appointment::new', values=payload)
        else:
            appointment = self.context.run_command('appointment::set', values=payload, id=object_id)
        return appointment

    def _delete_contact(self, object_id, flags):
        contact = self.context.run_command('contact::get', id=object_id)
        if (contact is not None):
            return self.context.run_command('contact::delete', object=contact)
        return False

    def _put_contact(self, payload, flags):
        object_id = int(payload.get('objectId'))
        if (object_id == 0):
            contact = self.context.run_command('contact::new', values=payload)
        else:
            contact = self.context.run_command('contact::set', values=payload, id=object_id)
        return contact

    def _put_defaults(self, payload, flags):
        # TODO: Implement
        raise 'Not Implemented'

    def _put_document(self, payload, flags):
        # TODO: Implement
        raise 'Not Implemented'

    def _delete_enterprise(self, object_id, flags):
        enterprise = self.context.run_command('enterprise::get', id=object_id)
        if (enterprise is not None):
            return self.context.run_command('enterprise::delete', object=enterprise)
        return False

    def _put_enterprise(self, payload, flags):
        object_id = int(payload.get('objectId'))
        if (object_id == 0):
            enterprise = self.context.run_command('enterprise::new', values=payload)
        else:
            enterprise = self.context.run_command('enterprise::set', values=payload, id=object_id)
        return enterprise

    def _put_folder(self, payload, flags):
        # TODO: Implement
        raise 'Not Implemented'

    def _put_note(self, payload, flags):
        # TODO: Implement
        raise 'Not Implemented'

    def _put_objectlink(self, payload, flags):
        # TODO: Implement
        raise 'Not Implemented'

    def _put_participantstatus(self, payload, flags):
        """ { 'comment': 'My very very very very long comment',
              'objectId': 10621,
              'rsvp': 1,
              'status': 'TENTATIVE',
              'entityName': 'ParticipantStatus' } """
        # The objectId is the objectId of THE APPOINTMENT, participantStatus is
        # unique in that it is a write-only entity.
        self.context.begin()
        object_id = int(payload['objectId'])
        self.context.run_command('participant::set', appointment_id=object_id,
                                                     participant_id=self.context.account_id,
                                                     status=payload.get('status', 'NEEDS-ACTION'),
                                                     comment=payload.get('comment', None),
                                                     rsvp=payload.get('rsvp',    None))
        self.context.commit()
        appointment = self.context.run_command('appointment::get', id=object_id)
        return appointment

    def _put_project(self, payload, flags):
        # TODO: Implement
        raise 'Not Implemented'

    def _put_resource(self, payload, flags):
        # TODO: Implement
        raise 'Not Implemented'

    def _put_task(self, payload, flags):
        object_id = int(payload.get('objectId', 0))
        if (object_id == 0):
            task = self.context.run_command('task::new', values=payload)
        else:
            task = self.context.run_command('task::set', values=payload, id=object_id)
        return task

    def _put_tasknotation(self, payload, flags):
        object_id = int(payload.get('taskObjectId'))
        task = self.context.run_command('task::comment', values=payload, id=object_id)
        return task

    def _delete_task(self, object_id, flags):
        return self.context.run_command('task::delete', id=object_id)

    def _put_team(self, payload, flags):
        # TODO: Implement
        raise 'Not Implemented'

    def _put_workflow(self, payload, flags):
        # TODO: Implement
        raise 'Not Implemented'
