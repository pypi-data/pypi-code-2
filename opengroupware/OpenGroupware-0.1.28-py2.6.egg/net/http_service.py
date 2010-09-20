# Copyright (c) 2010 Adam Tauno Williams <awilliam@whitemice.org>
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
import multiprocessing, os
from server      import CoilsHTTPServer
from handler     import CoilsRequestHandler
from root        import RootFolder
from coils.core  import *
import time
import logging, logging.config

def serve_forever(server, i):
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


class HTTPService(Service):
    __service__ = 'coils.http'
    __auto_dispatch__ = True
    __is_worker__     = False

    def prepare(self):
        self._workers = []
        Service.prepare(self)
        RootFolder.load_protocols(self.log)
        sd = ServerDefaultsManager()
        HTTP_HOST = sd.string_for_default('CoilsListenAddress', '127.0.0.1')
        HTTP_PORT = sd.integer_for_default('CoilsListenPort', 8080)
        self.log.info("Starting Server @ %s:%d" % (HTTP_HOST, HTTP_PORT))
        self._httpd = CoilsHTTPServer((HTTP_HOST, HTTP_PORT), CoilsRequestHandler)
        for i in range(15):
            p = multiprocessing.Process(target=serve_forever,
                                        args=(self._httpd, i))
            self._workers.append(p)
            p.start()
        try:
            self.send(Packet('coils.http/__null', 'coils.master/__status','HTTP/201 ONLINE'))
        except Exception, e:
            self.log.exception(e)
            sys.exit(1)
