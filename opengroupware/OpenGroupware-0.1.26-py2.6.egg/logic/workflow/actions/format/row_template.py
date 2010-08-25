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
import re, datetime
from lxml import etree
from coils.core          import *
from coils.core.logic    import ActionCommand

class RowTemplateAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "row-template"
    __aliases__   = [ 'rowTemplate', 'rowTemplateAction' ]

    def __init__(self):
        ActionCommand.__init__(self)

    def do_action(self):
        doc = etree.parse(self._rfile)
        rows = StandardXML.Read_Rows(self._rfile)
        for row in rows:
            text = self._template
            fields = row[0] # keys
            fields.update(row[1]) # non-key fields
            labels = set(re.findall('{:[A-z]*}', text))
            for label in labels:
                name = label[2:-1]
                if name in fields:
                    value = fields[name]
                    if (isinstance(value, datetime.datetime)):
                        value = value.strftime(self._dt_format)
                    else:
                        value = unicode(value)
                    text = text.replace(label, value)
            self._wfile.write(text)

    def parse_action_parameters(self):
        self._template = self._params.get('template')
        self._dt_format = self._params.get('datetimeFormat', '%Y-%m-%d')
        self._template = self.process_label_substitutions(self._template)

    def do_epilogue(self):
        pass
