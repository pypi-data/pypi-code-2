# handler_task.py
#
#

""" me2 task handler. """

## me2 imports

from me2.lib.plugins import plugs
from me2.lib.version import getversion
from me2.utils.exception import handle_exception
from me2.lib.tasks import taskmanager

## google imports

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

## simplejson import

from waveapi.simplejson import loads

## basic imports

import wsgiref.handlers
import logging
import google

## vars

periodicals =  ['me2.plugs.common.rss', 'me2.plugs.botevent']
mountpoints = ['rss', 'botevent']

##

logging.info(getversion('TASK'))

for plugin in periodicals:
    plugs.reload(plugin)


class TaskHandler(webapp.RequestHandler):

    """ the bots task handler. """

    def get(self):
        try:
            """ this is where the task gets dispatched. """
            path = self.request.path
            if path.endswith('/'):
                path = path[:-1]
            taskname = path.split('/')[-1].strip()
            logging.debug("using taskname: %s" % taskname)

            inputdict = {}
            for name, value in self.request.environ.iteritems():
                if not 'wsgi' in name:
                    inputdict[name] = value

            taskmanager.dispatch(taskname, inputdict, self.request, self.response)

        except google.appengine.runtime.DeadlineExceededError:
            return
        except Exception, ex:
            handle_exception()
            #self.send_error(500)

    def post(self):
        """ this is where the task gets dispatched. """
        try:
            path = self.request.path
            if path.endswith('/'):
                path = path[:-1]
            taskname = path.split('/')[-1].strip()
            logging.debug("using taskname: %s taken from %s" % (taskname, path))
            if not taskname:
                return

            inputdict = {}
            for name, value in self.request.environ.iteritems():
                if not 'wsgi' in name:
                    inputdict[name] = value

            taskmanager.dispatch(taskname, inputdict, self.request, self.response)
        except google.appengine.runtime.DeadlineExceededError:
            return
        except Exception, ex:
            handle_exception()
            #self.send_error(500)

# the application 

mountlist = []

for mount in mountpoints:
    mountlist.append(('/tasks/%s' % mount, TaskHandler))

application = webapp.WSGIApplication(mountlist, debug=True)

def main():
    global application
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
