"""\
Request body (POST input) service
"""

import cgi
import StringIO
import logging

from bn import AttributeDict
from pipestack.pipe import Pipe

log = logging.getLogger(__name__)

class InputPipe(Pipe):
    def enter(self, bag):
        if not bag.get(self.name):
            # We expect this to be a composite name
            if bag.environ.get('wsgi.input') and \
               bag.environ.get('REQUEST_METHOD', '').upper() == "POST":
                log.debug('Parsing the request body')
                s = StringIO.StringIO()
                try:
                    request_body_len = int(bag.environ['CONTENT_LENGTH'])
                    input = bag.environ['wsgi.input'].read(request_body_len)
                except (TypeError, ValueError):
                    raise Exception(
                        'Invalid HTTP post, no valid CONTENT_LENGTH'
                    )
                s.write(input)
                s.seek(0)
                # We don't want cgi.FieldStorage to merge in GET details so 
                # we don't give it the full environment
                new_environ = bag.environ.copy()
                if new_environ.has_key('QUERY_STRING'):
                    del new_environ['QUERY_STRING']
                bag[self.name] = cgi.FieldStorage(
                    fp=s, 
                    environ=new_environ,
                    keep_blank_values=True,
                    strict_parsing=True,
                )
                s.seek(0)
                bag.environ['wsgi.input'] = s
            else:
                log.debug('Not parsing the request body')
                bag[self.name] = None

