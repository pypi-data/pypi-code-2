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
import os
from coils.foundation import Backend

def filename_for_vcard(object_id, version):
    return '{0}/cache/vcard/{1}.{2}.vcf'.format(Backend.store_root(),
                                          object_id,
                                          version)

def is_vcard_cached(object_id, version):
    return os.path.exists(filename_for_vcard(object_id, version))

def read_cached_vcard(object_id, version):
    filename = filename_for_vcard(object_id, version)
    if (os.path.exists(filename)):
        handle = open(filename, 'rb')
        card = handle.read()
        handle.close()
    else:
        card = None
    return card

def cache_vcard(object_id, version, vcf):
    filename = filename_for_vcard(object_id, version)
    handle = open(filename, 'wb')
    handle.write(vcf)
    handle.close
