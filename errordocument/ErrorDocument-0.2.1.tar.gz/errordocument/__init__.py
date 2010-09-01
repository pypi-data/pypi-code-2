"""\
Error documents bag
"""

import logging

from bn import AttributeDict
from configconvert import stringToObject
from configconvert.internal import eval_import
from pipestack.pipe import Marble, MarblePipe
from pipestack.ensure import ensure_function_marble as ensure
from stringconvert import unicodeToUnicode, unicodeToBoolean
from conversionkit import Field, Conversion, noConversion
from recordconvert import toRecord

log = logging.getLogger(__name__)

def render(marble, render_fn, code, message, status):
    template = marble.config.template#'error.dwt' 
    regions = {
        'heading': 'Error %s'%code,
        'doctitle': '<title>Error %s</title>'%status,
        'content': message,
    }
    marble.bag.http.response.status = status
    marble.bag.http.response.headers = [('Content-type', 'text/html')]
    marble.bag.http.response.body = [
        render_fn(
    	    marble.config.template, # Usually 'error.dwt' 
            regions, 
        )
    ]

def createRenderIfMissing():
    def createRenderIfMissing_post_converter(conversion, state):
        if conversion.successful and not conversion.result.has_key('render'):
            # The state argument is in a special format:
            pipe = state.pipe
            bag = state.bag
            @ensure(pipe.aliases.template)
            def render_template(marble, code, message, status):
                return render(marble, marble.bag[pipe.aliases.template].render, code, message, status)
            conversion.children['render'] = Conversion(render_template).perform(noConversion())
            result = conversion.result
            result['render'] = conversion.children['render'].result
    return createRenderIfMissing_post_converter

class ErrorDocumentMarble(Marble):

    def render(self, code=None, message=None, status=None):
        try:
            if status is None:
                status = self.bag.http.response.status
            parts = status.split(' ')
            if code is None:
                code = int(parts[0])
            if message is None:
                message = ' '.join(parts[1:])
            if not status:
                status = '%s %s'%(code, message)
            return self.config.render(self, code, message, status)
        except Exception, e:
            if not self.config.fallback:
                raise
            log.error('%r', e)
            # Display the error document
            self.bag.http.response.status = '500 Internal Server Error'
            self.bag.http.response.headers = [('Content-type', 'text/html')]
            self.bag.http.response.body = ['''
<html>
<head><title>%(status)s</title></head>
<body>
<h1>Error %(code)s</h1>
<p>%(message)s</p>
</body>     
</html>'''%dict(status=status, code=code, message=message)]

class ErrorDocumentPipe(MarblePipe):
    marble_class = ErrorDocumentMarble
    default_aliases = AttributeDict(template='template')
    options = dict(
        render = Field(
            stringToObject(),
            empty_error="No value specified for '%(name)s.render'",
        ),
        template = Field(
            unicodeToUnicode(),
            missing_or_empty_error="No value specified for '%(name)s.template'",
        ),
        fallback = Field(
            unicodeToBoolean(),
            missing_or_empty_default=False,
        ),
    )
    post_converters = [
        createRenderIfMissing()
    ]

