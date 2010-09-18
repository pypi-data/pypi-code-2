"""\
WSGI service for easy calling of WSGI applications
"""

import logging

log = logging.getLogger(__name__)

from wsgipack.helper.wsgi import WSGIObject

class WSGIService(object):

    @staticmethod
    def create(flow, name, config=None):
        return WSGIService()

    @staticmethod
    def config(flow, name):
        # No configuration 
        return None

    def start(self, flow, name):
        flow[name] = WSGIObject(flow)
 

