# handler_dispatch.py
#
#

""" me2 dispatch handler.  dispatches remote commands.  """

## boot

from me2.lib.boot import boot
boot("gozerdata")

## me2 imports

from me2.utils.generic import fromenc, toenc
from me2.lib.version import getversion
from me2.utils.xmpp import stripped
from me2.utils.url import getpostdata, useragent
from me2.lib.plugins import plugs
from me2.lib.persist import Persist
from me2.utils.exception import handle_exception, exceptionmsg
from me2.lib.fleet import fleet
from me2.lib.errors import NoSuchCommand
from me2.lib.gae.utils.web import loginurl

## gaelib imports

from me2.lib.gae.web.bot import WebBot
from me2.lib.gae.web.event import WebEvent
from me2.lib.gae.utils.auth import checkuser

## google imports

from webapp2 import RequestHandler, Route, WSGIApplication
from google.appengine.ext.webapp import template
from google.appengine.api import users as gusers

## simplejson import

from me2.contrib.simplejson import loads

## basic imports

import sys
import time
import types
import os
import logging
import google

logging.warn(getversion('GAE DISPATCH'))

bot = WebBot()

class Dispatch_Handler(RequestHandler):

    """ the bots remote command dispatcher. """

    def options(self):
         self.response.headers.add_header('Content-Type', 'application/x-www-form-urlencoded')
         #self.response.headers.add_header("Cache-Control", "private")
         self.response.headers.add_header("Server", getversion())
         self.response.headers.add_header("Public", "*")
         self.response.headers.add_header('Accept', '*')
         self.response.headers.add_header('Access-Control-Allow-Origin', self.request.headers['Origin'])
         self.response.out.write("Allow: *")
         self.response.out.write('Access-Control-Allow-Origin: *') 
         logging.warn("dispatch - options response send to %s - %s" % (self.request.remote_addr, str(self.request.headers)))

    def post(self):

        """ this is where the command get disaptched. """
        starttime = time.time()
        try:
            logging.warn("DISPATCH incoming: %s - %s" % (self.request.get('content'), self.request.remote_addr))
            if not gusers.get_current_user():
                logging.warn("denied access for %s - %s" % (self.request.remote_addr, self.request.get('content')))
                self.response.out.write("acess denied .. plz login")
                self.response.set_status(400)
                return
            event = WebEvent(bot=bot).parse(self.response, self.request)
            event.cbtype = "DISPATCH"
            event.type = "DISPATCH"
            (userhost, user, u, nick) = checkuser(self.response, self.request, event)
            bot.gatekeeper.allow(userhost)
            event.bind(bot)
            bot.doevent(event)
        except NoSuchCommand:
            self.response.out.write("no such command: %s" % event.usercmnd)
        except google.appengine.runtime.DeadlineExceededError, ex:
            self.response.out.write("the command took too long to finish: %s" % str(time.time()-starttime))
        except Exception, ex:
            self.response.out.write("the command had an eror: %s" % exceptionmsg())
            handle_exception()

    get = post

# the application 

application = WSGIApplication([Route('/dispatch/', Dispatch_Handler) ], debug=True)

def main():
    global bot
    global application
    try: application.run()
    except google.appengine.runtime.DeadlineExceededError:
        pass
    except Exception, ex:
        logging.error("dispatch - %s" % str(ex))

if __name__ == "__main__":
    main()
