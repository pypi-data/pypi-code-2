# Copyright (c) 2011 Adam Tauno Williams <awilliam@whitemice.org>
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
import time
from coils.foundation    import *
from coils.core          import *
from coils.net           import *
from coils.core.omphalos import Render         as Omphalos_Render
from coils.core.omphalos import render_account as Omphalos_RenderAccount

class API(object):

    def __init__(self, context):
        self.context = context
        self.api     = ZOGIAPI(self.context)

    def _apply_defaults(self, parameters, defaults):
        result = [ ]
        for i in range(0, len(defaults)):
            if (len(parameters) > i):
                result.append(parameters[i])
            else:
                result.append(defaults[i])
        return result

    def api_getfavoritesbytype(self, kind, detail):
        parameters = self._apply_defaults(parameters, ('Contact', 0))
        if (kind in ['contact', 'enterprise', 'project']):
            x = self.context.run_command('{0}::get-favorite'.format(parameters[0].lower()))
            if (len(x) > 0):
                result = Render.Results(x, detail, self.context)
                return result
        return [ ]

    def api_getloginaccount(self, params):
        # Status: Implemeted
        account = self.context.run_command('account::get')
        defaults = self.context.run_command('account::get-defaults')
        return Omphalos_RenderAccount(account, defaults, 65503, self.context)

    def api_getobjectbyid(self, parameters):
        # Parameters: object id, detail level, flags
        # Status: Implemented
        parameters = self._apply_defaults(parameters, (self.context.account_id, 0, {}))
        kind = self.context.type_manager.get_type(parameters[0])
        if (kind == 'Unknown'):
            result = { 'entityName': 'Unknown', 'objectId': parameters[0] }
        else:
            x = getattr(self.api, 'get_%ss_by_ids' % kind.lower())([parameters[0]])
            if ((x is not None) and (len(x) == 1)):
                result = Omphalos_Render.Result(x[0], parameters[1], self.context)
            else:
                result = { 'entityName': 'Unknown', 'objectId': parameters[0] }
        return result

    def api_getobjectsbyid(self, parameters):
        # Status: Implemented
        parameters = self._apply_defaults(parameters, ([self.context.account_id], 0))
        result = [ ]
        index = self.context.type_manager.group_ids_by_type(parameters[0])
        for key in index.keys():
            x = getattr(self.api, 'get_%ss_by_ids' % key.lower())(index[key])
            if (x is None):
                self.context.log.debug('result of Logic was None')
            else:
                self.context.log.debug('retrieved %d %s objects' % (len(x), key))
                result.extend(x)
        result = Omphalos_Render.Results(result, parameters[1], self.context)
        return result

    def api_putobject(self, parameters):
        # Status: Implemented
        # http://code.google.com/p/zogi/wiki/putObject
        parameters = self._apply_defaults(parameters, (None, {}))
        payload = parameters[0]
        if (isinstance(payload, dict)):
            if (payload.has_key('entityName')):
                entity_name = payload['entityName'].lower()
            if (payload.has_key('_FLAGS')):
                flags = payload['_FLAGS']
                if (isinstance(flags, str)):
                    flags = flags.split(',')
            else:
                flags = []
            result = getattr(self.api, 'put_%s' % entity_name)(payload, parameters[1])
            if (result is not None):
                self.context.commit()
            result = Render.Result(result, 65535, self.context)
        else:
            raise CoilsException('Put entity has not entityName attribute')
        return result

    def api_deleteobject(self, parameters):
        # TODO: Implement
        # payload can be an object Id or an actual object
        # http://code.google.com/p/zogi/wiki/deleteObject
        parameters = self._apply_defaults(parameters, (None, {}))
        if (isinstance(payload, int) or isinstance(payload, str)):
            object_id = int(payload)
        else:
            object_id = int(payload.get('objectId'))
        kind = self.context.type_manager.get_type(object_id)
        x = getattr(self.api, 'delete_%s' % kind.lower())(object_id, flags)
        if (x is None):
            return False
        self.context.commit()
        return x

    def api_searchforobjects(self, parameters):
        # Status: Implemented
        # http://code.google.com/p/zogi/wiki/searchForObjects
        parameters = self._apply_defaults(parameters, ('Contact', [], 0, {}))
        flags = parameters[3]
        full_flags = { 'limit': 100, 'revolve': False, 'filter': None }
        if (isinstance(flags, dict)):
            for key in flags.keys():
                if (key == 'limit'):
                    full_flags['limit'] = flags['limit']
                elif (key == 'revolve'):
                    full_flags['revolve'] = flags['revolve']
        else:
            # Flags is not a dictionary!
            pass
        x = getattr(self.api, 'search_%s' % parameters[0].lower())(parameters[1], full_flags)
        result = [ ]
        start = time.time()
        if (len(x) > 0):
            for y in x:
                if (hasattr(y, '__entityName__')):
                    # Result contains ORM
                    z = Omphalos_Render.Result(y, parameters[2], self.context)
                    if (z is not None):
                        result.append(z)
                else:
                    result.append(y)
        self.context.log.info('Rendering searchForObjects results consumed {0}s'.format(time.time() - start))
        self.context.log.info('searchForObjects returning {0} entities'.format(len(result)))
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