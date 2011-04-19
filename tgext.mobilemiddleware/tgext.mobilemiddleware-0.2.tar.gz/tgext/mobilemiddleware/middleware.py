from webob import Request
import re
from tg import redirect

class MobileMiddleware(object):
    def __init__(self, application, config):
        self.application = application

        mobile_re_config = config.get('mobile.agents', 'android|fennec|iemobile|iphone|ipod|ipad')
        self.mobile_re = re.compile(mobile_re_config, re.IGNORECASE)

    def __call__(self, environ, start_response):
        req = Request(environ)

        user_agent = req.headers.get('User-Agent', None)
        if user_agent and self.mobile_re.search(user_agent):
            req.is_mobile = True
        else:
            req.is_mobile = False

        resp = req.get_response(self.application)
        return resp(environ, start_response)
