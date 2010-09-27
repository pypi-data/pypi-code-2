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
import io
from datetime           import datetime
# Core
from coils.core         import *
from coils.net          import *
# DAV Classses
from coils.protocol.dav.foundation     import *
from workflow                          import WorkflowPresentation

class SignalObject(DAVObject, WorkflowPresentation):
    ''' Represent a BPML markup object in WebDAV '''

    def __init__(self, parent, name, **params):
        DAVObject.__init__(self, parent, name, **params)

    def do_GET(self):
        #if (self.entity.state in ['C', 'F']):
        #    raise AccessForbiddenException('Cannot create message in completed or failed process.')
        if (self.entity is None):
            self.signal_queue_manager()
            self.request.send_response(201, 'OK')
            self.request.send_header('Content-Type', 'text/plain')
            self.request.end_headers()
            return
        elif (self.entity.__entityName__ == 'Route'):
            route_id = self.entity.object_id
            if (('key' in self.parameters) and ('value' in self.parameters)):
                #code  = self.parameters.get('code', 'default')
                key   = self.parameters.get('key')[0].upper()
                value = self.parameters.get('value')[0]
                if (key == 'INPUTMESSAGE'):
                    self.log.debug('Attempting to create new process from route {0}'.format(route_id))
                    try:
                        process = self.create_process(route=self.entity, data=value)
                        self.context.commit()
                        self.log.info('Process {0} created via signal by {1}.'.format(process.object_id, self.context.get_login()))
                        message = self.get_input_message(process)
                        self.start_process(process)
                    except Exception, e:
                        self.log.exception(e)
                        raise CoilsException('Failed to create process')
                    w = BufferedWriter(self.request.wfile, False)
                    paths = self.get_process_urls(process)
                    w.write('OK PID:{0} MSG{1} WATCH:{2}'.format(process.object_id, message.uuid, paths['output']))
                    self.request.send_response(200, 'OK')
                    self.request.send_header('Content-Type', 'text/plain')
                    self.request.send_header('X-COILS-WORKFLOW-MESSAGE-UUID', message.uuid)
                    self.request.send_header('X-COILS-WORKFLOW-MESSAGE-LABEL', message.label)
                    self.request.send_header('X-COILS-WORKFLOW-PROCESS-ID', process.object_id)
                    self.request.send_header('X-COILS-WORKFLOW-OUTPUT-URL', paths['output'])
                    self.request.send_header('Content-Length', str(w.getSize()))
                    self.request.end_headers()
                    w.flush()
                    return
                raise CoilsException('Workflow presentation object does not understand signal key {0}'.format(key))
            else:
                raise CoilsException('Workflow signals must contain a key and value parameter.')
            self.request.send_response(201, 'OK')
            self.request.send_header('Content-Type', 'text/plain')
            self.request.end_headers()
            return
        elif (self.entity.__entityName__ == Process):
            # TODO: Implement signalling processes
            self.request.send_response(201, 'OK')
            self.request.send_header('Content-Type', 'text/plain')
            self.request.end_headers()
            return
        raise NotImplementedException('This workflow presentation object does not support signals.')
