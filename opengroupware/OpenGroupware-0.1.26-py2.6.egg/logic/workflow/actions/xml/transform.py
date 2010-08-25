#
# Copyright (c) 2010 Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#
import os, base64
from lxml                import etree
from coils.core          import *
from coils.core.logic    import ActionCommand

class TransformAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "transform"
    __aliases__   = [ 'transformAction' ]

    def __init__(self):
        ActionCommand.__init__(self)

    def result_mimetype(self):
        return self._output_mimetype

    def do_action(self):
        source = etree.parse(self._rfile)
        xslt = etree.fromstring(self._xslt)
        transform = etree.XSLT(xslt)
        result = transform(source)
        self._wfile.write(unicode(result))

    def parse_action_parameters(self):
        self._xslt            = self._params.get('xslt', None)
        self._b64             = self._params.get('isBase64', 'NO').upper()
        self._output_mimetype = self._params.get('mimetype', 'application/xml')
        if (self._xslt is None):
            raise CoilsException('No XSLT provided for transform')
        if (self._b64 == 'YES'):
            self._xslt = base64.decodestring(self._xslt.strip())
        else:
            self._xslt = self.decode_text(self._xslt)

    def do_epilogue(self):
        pass