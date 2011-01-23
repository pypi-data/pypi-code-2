from webob import Request, Response
import logging
log = logging.getLogger(__name__)


class EatExceptions(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        req = Request(environ)
        #print req
        try:
#            print "****THIS IS THE REQUEST****\n", req       
#            print "****THIS IS THE END OF THE REQUEST****\n"
            response = req.get_response(self.app)
#            print "****THIS IS THE RESPONSE****\n", response       
#            print "****THIS IS THE END OF THE RESPONSE****\n"
        except Exception, error:
            response = Response()
            raise
            print "error was:", error
            e = str(error)
            text = '500: An error has occured: ' + e
            response.status_int = 500
            response.body = text
            return response
        finally:
            log.debug('Sent HTTP Response: \n%s' % (response))

        return response(environ, start_response)
