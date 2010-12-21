# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D

import simplejson

from paste.fileapp import _FileIter

# a json method decorator
#
# json content type: http://www.ietf.org/rfc/rfc4627.txt
# parses and consumes input data when the content-type indicates that it is 
# json data ('application/json') and puts it in the environment under the key
# 'benri.json'
#
# the response is automatically dumped as json if the content-type header is
# set to 'application/json'

JSON_CONTENT_TYPE = 'application/json'
JSON_HEADER = ('Content-Type', JSON_CONTENT_TYPE)

def json(f, name=None, **kwds):
    def wrapped(*args, **kwargs):
        #print "json: wrapped", args, kwargs
        _self = args[0]
        environ = args[1]
        response = args[2]

        json_header = [JSON_HEADER]

        # used to wrap the start response
        class _Wrap(object):
            def __init__(self):
                self.status = None
                self.headers = []
            
            def resp(self, status, headers):
                self.status = status
                self.headers = headers
       
        req_data = {}
       
        try:
            if environ['REQUEST_METHOD'] in ['PUT', 'POST']:
                chunks = []
                
                for chunk in _FileIter(environ['wsgi.input'], size=int(environ['CONTENT_LENGTH']), block_size=2**14):
                   chunks.append(chunk)

                req_data = simplejson.loads(''.join(chunks))
        except KeyError, e:
            response('400 BAD REQUEST', json_header)
            return [simplejson.dumps("No data in request.")]
        except Exception, e:
            response('400 BAD REQUEST', json_header)
            return [simplejson.dumps("Received invalid JSON data. %s" % (str(e)))]
                    
        wrap = _Wrap()
        try:
            environ['benri.json'] = req_data
            ret_list = f(_self, environ, wrap.resp)
        except:
            raise

        try:
            ret_data = ret_list[0]
        # dont add the json header if it is already part of the headers,
        # and dont transform the data
        # or if the content-type is set already
            if 'content-type' in [a.lower() for (a,b) in wrap.headers]:
                response(wrap.status, wrap.headers)
            # ret is always a list with one element
                return [ret_data]
            else:
                response(wrap.status, json_header + wrap.headers)
                return [simplejson.dumps(ret_data)]
        
        # return this when the data is empty
        except IndexError, e:
            response(wrap.status, [('Content-type', 'text/plain')])
            return []
                    
    wrapped.__doc__ = f.__doc__
    return wrapped
