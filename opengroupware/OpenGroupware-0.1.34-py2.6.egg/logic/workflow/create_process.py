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
import pickle, shutil
from xml.sax              import make_parser
from bpml_handler         import BPMLSAXHandler
from coils.core           import *
from coils.core.logic     import CreateCommand
from keymap               import COILS_PROCESS_KEYMAP
from utility              import filename_for_process_markup, \
                                   filename_for_process_code, \
                                   filename_for_route_markup

class CreateProcess(CreateCommand):
    __domain__ = "process"
    __operation__ = "new"

    def __init__(self):
        CreateCommand.__init__(self)

    def prepare(self, ctx, **params):
        self.keymap =  COILS_PROCESS_KEYMAP
        self.entity = Process
        CreateCommand.prepare(self, ctx, **params)

    def parse_parameters(self, **params):
        CreateCommand.parse_parameters(self, **params)
        if ('data' in params):
            self.values['data'] = params['data']
        elif ('filename' in params):
            self.values['handle'] = os.open(params['filename'], 'rb')
        elif ('handle' in params):
            self.values['handle'] = params['handle']

    def copy_markup(self, route):
        # TODO: Error meaningfully if the route has no markup
        source = BLOBManager.Open(filename_for_route_markup(route), 'rb')
        target = BLOBManager.Create(filename_for_process_markup(self.obj))
        shutil.copyfileobj(source, target)
        target.flush()
        source.seek(0)
        bpml = source.read()
        BLOBManager.Close(source)
        BLOBManager.Close(target)
        self.obj.set_markup(bpml)

    def compile_markup(self):
        # TODO: Use the markup already in memory!
        handle = BLOBManager.Open(filename_for_process_markup(self.obj), 'rb', encoding='binary')
        parser = make_parser()
        handler = BPMLSAXHandler()
        parser.setContentHandler(handler)
        parser.parse(handle)
        code = handler.get_processes()
        BLOBManager.Close(handle)
        handle = BLOBManager.Create(filename_for_process_code(self.obj), encoding='binary')
        pickle.dump(code, handle)
        BLOBManager.Close(handle)

    def run(self, **params):
        # TODO: Verify MIME f input message against MIME of input message for route.
        CreateCommand.run(self, **params)
        # Verify route id
        route = self._ctx.run_command('route::get', id=self.obj.route_id,
                                                    access_check=self.access_check)
        if (route is not None):
            # Route is available
            # Allocate the input message of the process
            message = None
            if ('data' in self.values):
                message = self._ctx.run_command('message::new', process=self.obj,
                                                                label=u'InputMessage',
                                                                data=self.values['data'])
            elif ('handle' in self.values):
                message = self._ctx.run_command('message::new', process=self.obj,
                                                                label=u'InputMessage',
                                                                handle=self.values['handle'])
            else:
                raise CoilsException('Cannot create process without input')
            self.obj.input_message = message.uuid
            self.copy_markup(route)
            self.compile_markup()
            self.save()
        else:
            raise CoilsException('No such route or route not available')
