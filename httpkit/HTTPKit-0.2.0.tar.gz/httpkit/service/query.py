"""\
Query string service
"""

import cgi
import logging

from pipestack.pipe import Pipe

log = logging.getLogger(__name__)

class QueryPipe(Pipe):
    def enter(self, bag):
        if bag.environ.get('QUERY_STRING') \
           and bag.environ.get('REQUEST_METHOD', '').upper() == "GET":
            bag[self.name] = cgi.FieldStorage(
                environ=bag.environ, 
                keep_blank_values=True
            )
        else:
            bag[self.name] = cgi.FieldStorage()


