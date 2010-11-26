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
import os, sys, glob, inspect, re
from coils.core  import *
from pathobject  import PathObject
from xmlrpc      import XMLRPCServer
from protocol    import Protocol

class RootFolder(PathObject):
    _protocol_dict = None

    def get_name(self):
        return ''

    @staticmethod
    def load_protocols(logger):
        RootFolder._protocol_dict = { }
        for bundle_name in Backend.get_protocol_bundle_names():
            bundle =  __import__(bundle_name, fromlist=['*'])
            RootFolder.scan_bundle(bundle, logger)
        msg = 'loaded protocols:'
        for k in RootFolder._protocol_dict.keys():
            msg = '%s [%s=%s]' % (msg, k, RootFolder._protocol_dict[k])
        logger.info(msg)

    @staticmethod
    def scan_bundle(bundle, logger):
        logger.debug('Scanning bundle {0} for protocols.'.format(bundle))
        for name, data in inspect.getmembers(bundle, inspect.isclass):
            # Only load classes specifically from this bundle
            if (data.__module__[:len(bundle.__name__)] == bundle.__name__):
                if(issubclass(data, Protocol)):
                    # TODO: is this the best way to test for an enumerable?
                    if (hasattr(data.__pattern__, '__iter__')):
                        for entity in data.__pattern__:
                            if (RootFolder._protocol_dict.has_key(data.__pattern__)):
                                RootFolder._protocol_dict[data.__pattern__].append(data)
                            else:
                                RootFolder._protocol_dict[data.__pattern__] = [ ]
                                RootFolder._protocol_dict[data.__pattern__].append(data)
                    else:
                         if (RootFolder._protocol_dict.has_key(data.__pattern__)):
                            RootFolder._protocol_dict[data.__pattern__].append(data)
                         else:
                            RootFolder._protocol_dict[data.__pattern__] = [ ]
                            RootFolder._protocol_dict[data.__pattern__].append(data)
        return

    def is_public():
        return False

    def init_context(self, allow_anonymous):
        self.log.debug('Initializing context for handler')
        metadata = self.request.get_metadata()
        if (metadata['authentication']['mechanism'] == 'anonymous'):
            if (allow_anonymous):
                self.log.debug('Anonymous context created for handler.')
                #self.context = AnonymousContext(metadata)
                self.context = AssumedContext(10100)
                return
            else:
                self.log.debug('Request is anonymous but authentication is required.')
                raise AuthenticationException('Requested path requires authentication')
        self.context = AuthenticatedContext(metadata)

    def object_for_key(self, name):
        ''' Lookup the handler for the first element in the requested path. '''
        if (RootFolder._protocol_dict is None):
            # Scan for protocols if protocol list has not been initialized
            RootFolder.load_protocols(self.log)
        for pattern in RootFolder._protocol_dict.keys():
            if (re.search(pattern, name) is not None):
                if(len(RootFolder._protocol_dict[pattern]) == 1):
                    # This pattern is only attached to one bundle
                    if (RootFolder._protocol_dict[pattern][0].__xmlrpc__ == True):
                        # XML-RPC request
                        self.init_context(False)
                        return XMLRPCServer(self, RootFolder._protocol_dict[pattern], context=self.context,
                                                                                       request=self.request)
                    else:
                        # This is a normal operation, not an XML-RPC request
                        handler = RootFolder._protocol_dict[pattern][0](self, request=self.request,
                                                                              parameters=self.parameters)
                        # A handler's context is initialized AFTER an instance is made, a handler cannot
                        # use the context within its constructor.
                        if (handler.is_public()):
                            self.init_context(True)
                        else:
                            self.init_context(False)
                        handler.context = self.context
                        return handler
                else:
                    # Must be an XML-RPC Bundle, only XML-RPC supports name spaces (multiple bundles per path)
                    self.init_context(False)
                    return XMLRPCServer(self, RootFolder._protocol_dict[pattern], context=self.context,
                                                                                   request=self.request)