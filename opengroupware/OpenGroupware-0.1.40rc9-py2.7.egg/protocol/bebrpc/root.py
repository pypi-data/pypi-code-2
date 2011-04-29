# Copyright (c) 2011 Morrison Industries
import time, json
from coils.net           import PathObject, Protocol
from coils.core          import CoilsException, \
                                  NoSuchPathException, \
                                  AuthenticationException, \
                                  AccessForbiddenException
from api                 import get_api

class BEBRPCRoot(PathObject, Protocol):
    __pattern__   = 'bebrpc'
    __namespace__ = None
    __xmlrpc__    = False

    def __init__(self, parent, **params):
        PathObject.__init__(self, parent, **params)

    def is_public(self):
        return False

    def get_name(self):
        return 'beb'

    def do_POST(self):

        def encode(o):
            if (isinstance(o, datetime)):
                return  o.strftime('%Y-%m-%d')
            raise TypeError()

        mimetype = self.request.headers.get('Content-Type', None)
        if (mimetype == 'application/json'):
            start = time.time()
            payload = self.request.get_request_payload()
            try:
                print payload
                values = json.loads(payload)
            except Exception, e:
                self.log.exception(e)
                raise CoilsException('Unable to parse JSON payload.')
            if (isinstance(values, dict)):
                start = time.time()
                if ('method' in values):
                    # TODO: check version
                    self.log.info(values)
                    method      = 'api_{0}'.format(values['method'].replace('.', '_').strip().lower())
                    response_id = values.get('id', None)
                    parameters  = values.get('params', [])
                    api = get_api(method.split('_')[1], context=self.context)
                    if (hasattr(api, method)):
                        try:
                            result = getattr(api, method)(parameters)
                        except Exception, e:
                            self.log.exception(e)
                            response =  { 'result':  None,
                                          'version': '1.1',
                                          'error':   str(e),
                                          'id':      response_id }
                            if (self.context.amq_available):
                                end = time.time()
                                self.context.send(None,
                                                  'coils.administrator/performance_log',
                                                  { 'lname': 'bebrpc',
                                                    'oname': values['method'].strip().lower(),
                                                    'runtime': (end - start),
                                                    'error': True } )
                        else:
                            if (self.context.amq_available):
                                end = time.time()
                                self.context.send(None,
                                                  'coils.administrator/performance_log',
                                                  { 'lname': 'bebrpc',
                                                    'oname': values['method'].strip().lower(),
                                                    'runtime': (end - start),
                                                    'error': False } )
                            response =  { 'result':   result,
                                          'version':  '1.1',
                                          'error':    None,
                                          'id':      response_id }
                    else:
                        self.log.error('Request for non-implmented JSON-RPC API {0}'.format(method))
                        response =  { 'result':   None,
                                      'version':  '1.1',
                                      'error':    'JSON-RPC API implements no such method as {0}'.format(method),
                                      'id':       response_id }
                    try:
                        response = json.dumps(response, default=encode)
                    except:
                        raise CoilsException('Unable to represent response as JSON content.')
                    self.request.simple_response(200, data=response,
                                                      mimetype='application/json')
                else:
                    raise CoilsException('No RPC method specified in request')
            else:
                pass #???
        else:
            raise CoilsException('Unexpected Content-Type; must be application/json')
