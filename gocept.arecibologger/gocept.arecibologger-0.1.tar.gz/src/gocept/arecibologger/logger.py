# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import logging
import urllib
import socket
import App.config
import Products.SiteErrorLog.SiteErrorLog
import ZPublisher.HTTPResponse
from zExceptions.ExceptionFormatter import format_exception

log = logging.getLogger('gocept.arecibologger')

HOST = socket.gethostname()


def report_to_aricebo(errorlog, info, request):
    c = App.config.getConfiguration().product_config['gocept.arecibologger']
    if 'AUTHENTICATED_USER' in request:
        user = request['AUTHENTICATED_USER'].getId()
    else:
        user = None
    type_ = str(getattr(info[0], '__name__', info[0]))
    status = ZPublisher.HTTPResponse.status_codes.get(type_.lower(), 500)
    data = {'account': c['account'],
            'url': request['URL'],
            'server': HOST,
            'user_agent': request.get('HTTP_USER_AGENT'),
            'status': str(status),
            'type': type_,
            'traceback': ''.join(format_exception(*info, **{'as_html': 0})),
            'request': request.text(),
            'username': user}
    encoded = urllib.urlencode(data)
    result = urllib.urlopen(c['server'], encoded).read()
    if result != 'Error recorded':
        raise RuntimeError('Invalid response from Arecibo server.')


old_raising = Products.SiteErrorLog.SiteErrorLog.SiteErrorLog.raising
def arecibo_raising(self, info):
    type_ = str(getattr(info[0], '__name__', info[0]))
    if type_ in self._ignored_exceptions:
        return
    try:
        report_to_aricebo(self, info, self.REQUEST)
    except:
        log.exception('Failed to report error to Arecibo.')
    return old_raising(self, info)

Products.SiteErrorLog.SiteErrorLog.SiteErrorLog.raising = arecibo_raising
