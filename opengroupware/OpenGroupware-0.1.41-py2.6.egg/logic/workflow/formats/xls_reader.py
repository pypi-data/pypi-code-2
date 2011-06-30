#
# Copyright (c) 2011 Adam Tauno Williams <awilliam@whitemice.org>
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

class ColumnarXLSReaderFormat(Format):
    # Issue#152 : Implement a Columnar XLS Format for importing XLS documents

    def __init__(self):
        Format.__init__(self)

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

    def process_in(self, rfile, wfile):
        # TODO: Open document
        # TODO: Read date-type from book
        # TODO: Select sheet
        self._sheet = self._book.sheet_by_index(0)
        wfile.write(u'<?xml version="1.0" encoding="UTF-8"?>')
        wfile.write(u'<ResultSet formatName=\"{0}\" className=\"{1}\" tableName="{2}">'.\
            format(self.description.get('name'),
                   self.__class__.__name__,
                   self.description.get('tableName', '_undefined_')))
        # Initialize fields
        self._fields = {}
        for i in range(0, len(self._definition.get('fields'))):
            field = self._definition.get('fields')[i]
            self._fields[field['name']] = field
        # Initialize columns from first row
        self._columns = {}
        for colx in range(0,sheet.ncols):
            self._columns[sheet.cell_value(rowx=0,colx=colx)] = colx
        # Process rows
        for rowx in range(1, sheet.nrows):
            try:
                data = self.process_record_in(rowx)
                counter += 1
                self.pause(counter)
            except RecordFormatException, e:
                self.reject(wrapper.current, str(e))
                self.log.warn('Record format exception on record {0}: {1}'.format(self.in_counter, unicode(record)))
                if (self._discard_on_error):
                    self.log.info('Record {0} of input message dropped due to format error'.format(self.in_counter))
                else:
                    raise e
            else:
                if (data is not None):
                    wfile.write(data)
        wfile.write(u'</ResultSet>')
        return

    def process_record_in(self, rowid):
        stream = StringIO.StringIO(''.rjust(record_length, ' '))
        for i in range(0, len(self._definition.get('fields'))):
            field = self._definition.get('fields')[i]
            if field['name'] in self._columns:
                value = self._sheet.cell_value(rowx=rowid, colx=self._columns[field['name']])
                if (field.get('strip', True)): value = value.strip()
                if (field.get('upper', True)): value = value.upper()
                elif (field.get('lower', True)): value = value.lower()
                if (field['kind'] in ['date']):
                    if (len(value) > 0):
                        value = Format.Reformat_Date_String(value, field['format'], '%Y-%m-%d')
                    else:
                        value = None
                elif (field['kind'] in ['datetime']):
                    if (len(value) > 0):
                        value = Format.Reformat_Date_String(value, field['format'], '%Y-%m-%d %H:%M:%S')
                    else:
                        value = None
                elif (field['kind'] in ['integer', 'float']):
                    try:
                        floor = field.get('floor', None)
                        cieling = field.get('cieling', None)
                        if (field['kind'] == 'integer'):
                            value = int(value)
                        else:
                            # Float
                            value = (float(value) * float(sign))
                        if (floor is not None) and (value < floor):
                            message = 'Value {0} below floor {1}'.format(value, floor)
                            self.log.warn(message)
                            raise ValueError(message)
                        if (cieling is not None) and (value > cieling):
                            message = 'Value {0} above cieling {1}'.format(value, cieling)
                            self.log.warn(message)
                            raise ValueError(message)
                    except ValueError, e:
                        message = 'Value error converting value \"{0}\" to type \"{1}\" for attribute \"{2}\".'.\
                                format(value, field['kind'], field['name'])
                        self.log.warn(message)
                        raise RecordFormatException(message, e)
            else:
                if field.get('required', False):
                    value = field.get('default', None)
                else:
                    raise RecordFormatException('Required field "{0}" is absent from row {1}'.\
                                                format(field['name'], rowid))
            if (valuse is None):
                row.append(u'<{0} dataType=\"{1}\" isNull=\"true\" isPrimaryKey=\"{2}\"/>'.\
                    format(field['name'], field['kind'], isKey))
            else:
                row.append(u'<{0} dataType=\"{1}\" isNull=\"false\" isPrimaryKey=\"{2}\">{3}</{4}>'.\
                    format(field['name'], field['kind'], field.get('key', 'false'), value, field['name']))
        stream.seek(0)
        row = stream.getvalue()
        stream.close()
        return u'<row>{0}</row>'.format(row)

    def process_out(self, rfile, wfile):
        raise NotImplementedException('Cannot write XLS documents.')