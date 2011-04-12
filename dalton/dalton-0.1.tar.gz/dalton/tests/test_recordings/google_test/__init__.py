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
                                          'PREF=ID=f04dc7d73167635a:FF=0:TM=1302640254:LM=1302640254:S=P_Wqq2fnAKKz0pob; expires=Thu, 11-Apr-2013 20:30:54 GMT; path=/; domain=.google.com, NID=45=duKHo-hv9REBLBKCIThnPphP7KPnKJMzxp-rRsHDG64AVBVYIrVPjqH0Ic7txeIensXLZ7CgeMO41WDNVPbP8A0xM7lzjrV0bL_zWeTYNYlTR2u01NBW_o4WA87mB3nu; expires=Wed, 12-Oct-2011 20:30:54 GMT; path=/; domain=.google.com; HttpOnly'),
                     ('expires', '-1'),
                     ('server', 'gws'),
                     ('cache-control', 'private, max-age=0'),
                     ('date', 'Tue, 12 Apr 2011 20:30:54 GMT'),
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
                     ('date', 'Tue, 12 Apr 2011 20:30:54 GMT'),
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

