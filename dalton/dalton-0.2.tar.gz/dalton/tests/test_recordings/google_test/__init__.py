import os
import dalton
from dalton import FileWrapper

here = os.path.abspath(os.path.dirname(__file__))

class StepNumber0(object):
    recorded_request = {
        'headers':  {},
        'url': '/',
        'method': 'GET',
        'body': None,
    }
    recorded_response = {
        'headers':  [('x-xss-protection', '1; mode=block'),
                     ('transfer-encoding', 'chunked'),
                     (                    'set-cookie',
                                          'PREF=ID=21631cc53907989b:FF=0:TM=1305048200:LM=1305048200:S=nYEfT-x5Kj-OtnfX; expires=Thu, 09-May-2013 17:23:20 GMT; path=/; domain=.google.com, NID=46=Novhlfv40rmZXIZ-NJR_ZJhhA4bnsu-nLsn0frD9-2Dd2KdWqNbyr1OrM2eeFCNJCk_SS27A3ggzwHBlWsHE5tSYOSLQFsLz3m7YNHNy2LEdlsxdZ32XShtgFJk6rJIZ; expires=Wed, 09-Nov-2011 17:23:20 GMT; path=/; domain=.google.com; HttpOnly'),
                     ('expires', '-1'),
                     ('server', 'gws'),
                     ('cache-control', 'private, max-age=0'),
                     ('date', 'Tue, 10 May 2011 17:23:20 GMT'),
                     ('content-type', 'text/html; charset=ISO-8859-1')],
        'body': FileWrapper('step_0_response.txt', here),
        'status': 200,
        'reason': 'OK',
        'version': 11,
    }
    next_step = 'StepNumber1'
    
    def handle_request(self, request):
        assert dalton.request_match(request, self.recorded_request)
        return (self.next_step, dalton.create_response(self.recorded_response))


class StepNumber1(object):
    recorded_request = {
        'headers':  {},
        'url': '/',
        'method': 'POST',
        'body': FileWrapper('step_1_request.txt', here),
    }
    recorded_response = {
        'headers':  [('content-length', '11816'),
                     ('x-xss-protection', '1; mode=block'),
                     ('server', 'gws'),
                     ('allow', 'GET, HEAD'),
                     ('date', 'Tue, 10 May 2011 17:23:20 GMT'),
                     ('content-type', 'text/html; charset=UTF-8')],
        'body': FileWrapper('step_1_response.txt', here),
        'status': 405,
        'reason': 'Method Not Allowed',
        'version': 11,
    }
    next_step = 'None'
    
    def handle_request(self, request):
        assert dalton.request_match(request, self.recorded_request)
        return (self.next_step, dalton.create_response(self.recorded_response))

