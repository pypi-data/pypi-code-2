import sys
from twisted.python import log
log.startLogging(sys.stdout)

from twisted.internet import reactor
from twisted.web import server, resource

from quebert import process as subp

import run_task

class Catchall(resource.Resource):
    def getChild(self, segment, request):
        return self

    def render(self, request):
        def _cb(data):
            request.write(data)
            request.finish()

        subp.execute(run_task.dispatch, request.content.read(), request.uri).addBoth(_cb)
        return server.NOT_DONE_YET

reactor.listenTCP(8000, server.Site(Catchall()))
reactor.run()
