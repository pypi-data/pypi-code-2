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
# THE SOFTWARE.
#
try:
    import ijson
except:
    HAS_IJSON = False
else:
    HAS_IJSON = True

import json
from coils.core    import NotImplementedException, \
                           BLOBManager
from filter       import OpenGroupwareServerSideFilter

class JSONOSSFilter(OpenGroupwareServerSideFilter):

    @property
    def handle(self):
        if (self._mimetype != 'application/json'):
            raise Exception('Input type for JSONDecoder is not mimetype application/json')
        if (hasattr(self, '_mode')):
            if (self._mode == 'pagination'):
                return self.paginate()
            elif (self._mode == 'count'):
                return self.count()
            else:
                raise NotImplementedException('JSON OSSF mode {0} not implemented'.format(self._mode))
        else:
            # If no mode was specified then we don't do anything, just pass back our
            # input file handle.
            return self._rfile

    def paginate(self):
        if (hasattr(self, '_path')):
            if (hasattr(self, '_range')):
                value = self._range.split('-')
                if (len(value[0]) == 0): start = 0
                else: start = int(value[0])
                if (len(value[1]) == 0): end = -1
                else: end = int(value[1])
            else:
                start = 0
                end   = -1
            data = [ ]
            counter = 0
            if (HAS_IJSON):
                for item in ijson.items(self._rfile, self._path):
                    if (counter >= start):
                        data.append(item)
                    if (end > 0):
                        if counter >= end: break
                    counter += 1
            else:
                # TODO: Implement a non-ijson fallback
                raise NotImplementedException('JSON OSSF currently requires the ijson module.')
            tmp = BLOBManager.ScratchFile()
            print json
            json.dump(data, tmp)
            tmp.seek(0)
            return tmp
        else:
            # If no path for was specified then we don't paginate, just pass back our
            # input file handle.
            return self._rfile

    def count(self):
        counter = 0
        if (hasattr(self, '_path')):
            if (HAS_IJSON):
                for item in ijson.items(self._rfile, self._path):
                    counter += 1
            else:
                # TODO: Implement a non-ijson fallback
                raise NotImplementedException('JSON OSSF currently requires the ijson module.')
        tmp = BLOBManager.ScratchFile()
        tmp.write(unicode(counter))
        tmp.seek(0)
        return tmp

    @property
    def mimetype(self):
        if (self._mode == 'pagination'):
            return 'application/json'
        elif (self._mode == 'count'):
            return 'text/plain'