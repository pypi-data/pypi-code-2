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
import StringIO
from lxml        import etree
from xlwt        import Workbook, easyxf
from format      import COILS_FORMAT_DESCRIPTION_OK, Format

class SimpleXLSFormat(Format):

    def __init__(self):
        Format.__init__(self)
        self._styles = None

    def set_description(self, fd):
        code = Format.set_description(self, fd)
        if (code[0] == 0):
            self.description = fd
            self._definition = self.description.get('data')
            # TODO: Verify XLS format parameters
            return (COILS_FORMAT_DESCRIPTION_OK, 'OK')
        else:
            return code

    @property
    def mimetype(self):
        return 'application/vnd.ms-excel'

    def process_record_in(self, record):
        raise NotImplementedException('Cannot read XLS documents.')

    def init_styles(self):
        self._styles = { }
        source = self._definition.get('styles', [])
        for style in source:
            descriptor = 'font:{0};alignment:{1};pattern:{2}'.\
                            format(source[style].get('font', ''),
                                   source[style].get('alignment', ''),
                                   source[style].get('pattern', ''))
            format = source[style].get('format', None)
            if (format is None):
                self._styles[style] = easyxf(descriptor)
            else:
                self._styles[style] = easyxf(descriptor, num_format_str=format)

    def begin_output(self):
        if (self._styles is None):
            self.init_styles()
        self._book = Workbook(style_compression=2)
        self._sheet = self._book.add_sheet('Sheet 1')
        if ('header' in self._definition):
            self._sheet.header_str = self._definition.get('header')
        if ('footer' in self._definition):
            self._sheet.footer_str = self._definition.get('footer')
        if ('portrait' in self._definition):
            if (self._definition.get('portrait')):
                self._sheet.portrait = True
            else:
                self._sheet.portrait = False
        counter = 0
        style = self._styles.get('_title')
        for column in self._definition.get('columns'):
            if (style is None):
                self._sheet.row(0).write(counter, column.get('title'))
            else:
                self._sheet.row(0).write(counter, column.get('title'), style)
            self._sheet.col(counter).width = int(column.get('width'))
            counter = counter + 1
        self._sheet.set_panes_frozen(True)
        self._sheet.set_horz_split_pos(1)

    def end_output(self):
        pass

    def process_out(self, rfile, wfile):
        doc = etree.parse(rfile)
        self.begin_output()
        self._row = 1
        for record in doc.xpath(u'/ResultSet/row'):
            self.process_record_out(record)
            self._row = self._row + 1
        self.end_output()
        self._book.save(wfile)
        self._book = None

    def process_record_out(self, record):
        self._column = 0
        for column in self._definition.get('columns'):
            value = record.xpath(u'{0}[1]/text()'.format(column.get('name')))
            if (len(value) > 0):
                value = value[0]
            else:
                value = None
            kind  = column.get('kind', 'string')
            style = column.get('style', None)
            if (style is not None):
                style = self._styles.get(style, None)
            if (kind == 'float'):
                if value is None:
                    value = column.get('default', 0.0)
                if (style is None):
                    self._sheet.row(self._row).write(self._column, float(value))
                else:
                    self._sheet.row(self._row).write(self._column, float(value), style)
            elif (kind == 'integer'):
                if value is None:
                    value = column.get('default', 0)
                if (style is None):
                    self._sheet.row(self._row).write(self._column, int(value))
                else:
                    self._sheet.row(self._row).write(self._column, int(value), style)
            else:
                if (value is not None):
                    value = self.decode_text(value)
                if (style is None):
                    self._sheet.row(self._row).write(self._column, value)
                else:
                    self._sheet.row(self._row).write(self._column, value, style)
            self._column = self._column + 1
        self._sheet.flush_row_data()
