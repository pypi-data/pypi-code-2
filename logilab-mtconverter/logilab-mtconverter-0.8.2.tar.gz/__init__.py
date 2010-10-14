# copyright 2006-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of logilab-mtconverter.
#
# logilab-mtconverter is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 2.1 of the License, or (at your
# option) any later version.
#
# logilab-mtconverter is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with logilab-mtconverter. If not, see <http://www.gnu.org/licenses/>.
"""Mime type conversion package.

  2006-2008 `LOGILAB S.A. <http://www.logilab.fr>`_ (Paris, FRANCE),
  all rights reserved.

  http://www.logilab.org/project/rql --
  mailto:python-projects@logilab.org

  `Lesser General Public License version 2`
"""
__docformat__ = "restructuredtext en"

from logilab.mtconverter.__pkginfo__ import version as __version__

import locale
import mimetypes
import re
import string
import htmlentitydefs
import codecs
from StringIO import StringIO

try:
    import chardet
except ImportError:
    # chardet unvailable
    chardet = None

mimetypes.encodings_map['.bz2'] = 'bzip2' # register bzip2 encoding
try:
    DEFAULT_ENCODING = locale.getpreferredencoding()
except locale.Error:
    DEFAULT_ENCODING = locale.getpreferredencoding(do_setlocale=False)

BINARY_ENCODINGS = set(('gzip', 'bzip2', 'base64'))

TEXT_MIMETYPES = set(('application/xml', 'application/xhtml+xml'))

UNICODE_POLICY = 'strict'

CHARSET_DECL_RGX = re.compile('(?:charset|(?:(?:en)?coding))[=:\s"\']*([^\s"\']*)',
                              re.I | re.S | re.U)
CHARSET_DECL_SEARCH_SIZE = 512

CHARDET_MIN_SIZE = 20
CHARDET_CONFIDENCE_THRESHOLD = 0.75

def need_guess(mimetype, encoding):
    """return True if we can complete given mimetype / encoding information"""
    if not mimetype:
        return True
    if not encoding and is_text_mimetype(mimetype):
        return True
    return False

def is_text_mimetype(mimetype):
    return (mimetype.startswith('text/') or mimetype in TEXT_MIMETYPES)

def guess_encoding(buffer, fallbackencoding=None):
    """try to guess encoding from a buffer"""
    if hasattr(buffer, 'getvalue'): # may be a StringIO
        buffer = buffer.getvalue()
    # try to get a character set declaration
    m = CHARSET_DECL_RGX.search(buffer[:CHARSET_DECL_SEARCH_SIZE])
    if m is not None:
        guessed = m.group(1)
        try:
            # ensure encoding is known by python
            codecs.lookup(guessed)
            return guessed
        except LookupError:
            pass
    if buffer.lstrip().startswith('<?xml'):
        # xml files with no encoding declaration default to UTF-8
        return 'UTF-8'
    # use text analysis if enough data
    if chardet is not None and len(buffer) > CHARDET_MIN_SIZE:
        detected = chardet.detect(buffer)
        if detected['confidence'] >= CHARDET_CONFIDENCE_THRESHOLD:
            return detected['encoding']
    return fallbackencoding or DEFAULT_ENCODING

def guess_mimetype_and_encoding(format=None, encoding=None, data=None,
                                filename=None, fallbackencoding=None,
                                fallbackmimetype=u'application/octet-stream'):
    if format and format.split('/')[-1] in BINARY_ENCODINGS:
        format = None # try to do better
    if filename and not format:
        format, enc = mimetypes.guess_type(filename)
        if format:
            if not encoding:
                encoding = enc
        elif enc:
            format = u'application/%s' % enc
        else:
            format = fallbackmimetype
    if not encoding and data and format and is_text_mimetype(format):
        encoding = guess_encoding(data, fallbackencoding)
    return format, encoding


CONTROL_CHARS = [chr(ci) for ci in range(32)]
TR_CONTROL_CHARS = [' '] * len(CONTROL_CHARS)
for c in ('\n', '\r', '\t'):
    TR_CONTROL_CHARS[ord(c)] = c
TR_CONTROL_CHARS[ord('\f')] = '\n'
TR_CONTROL_CHARS[ord('\v')] = '\n'
ESC_CAR_TABLE = string.maketrans(''.join(CONTROL_CHARS),
                                 ''.join(TR_CONTROL_CHARS))
ESC_UCAR_TABLE = unicode(ESC_CAR_TABLE, 'latin1')

# XXX deprecate at some point (once less used :)
#@obsolete('use xml_escape')
def html_escape(data):
    return xml_escape(data)

def xml_escape(data):
    """escapes XML forbidden characters in attributes and PCDATA"""
    if isinstance(data, unicode):
        data = data.translate(ESC_UCAR_TABLE)
    else:
        data = data.translate(ESC_CAR_TABLE)
    return (data.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
            .replace('"','&quot;').replace("'",'&#39;'))

def html_unescape(data):
    """unescapes XML/HTML entities"""
    for entityname, codepoint in htmlentitydefs.name2codepoint.iteritems():
        data = data.replace('&%s;' % entityname, unichr(codepoint))
    return data.replace('&#39;', "'")

class TransformData(object):
    """wrapper arround transformed data to add extra infos such as MIME
    type and encoding in case it applies
    """
    def __init__(self, data, mimetype, encoding=None, **kwargs):
        self.__dict__.update(kwargs)
        self.data = data
        self.mimetype = mimetype
        self.encoding = encoding
        if not self.is_binary() and not encoding and not isinstance(self.data, unicode):
            self.encoding = guess_encoding(data)

    def get(self, attr, default=None):
        """get an optional data attribute"""
        return getattr(self, attr, default)

    def decode(self, force=False):
        """return the data as an unicode string"""
        if isinstance(self.data, unicode):
            return self.data
        if force:
            if self.encoding in BINARY_ENCODINGS:
                self.binary_decode()
        elif self.is_binary():
            raise Exception("can't decode binary stream (mime type: %s, encoding: %s)"
                            % (self.mimetype, self.encoding))
        if self.encoding:
            encoding = self.encoding
        else:
            encoding = guess_encoding(self.data)
        return self.data.decode(encoding, UNICODE_POLICY)

    def encode(self, encoding=None):
        """return the data as an encoded string"""
        if (encoding is None or self.encoding == encoding) and \
               isinstance(self.data, str):
            return self.data
        encoding = encoding or self.encoding or 'utf8'
        return self.decode().encode(encoding)

    def is_binary(self):
        return (not is_text_mimetype(self.mimetype)
                or self.encoding in BINARY_ENCODINGS)

    def check_encoding(self):
        if is_text_mimetype(self.mimetype) and self.is_binary():
            raise TransformError()

    def binary_decode(self):
        if self.encoding == 'gzip':
            import gzip
            stream = gzip.GzipFile(fileobj=StringIO(self.data))
            self.data = stream.read()
            self.encoding = guess_encoding(self.data)
        elif self.encoding == 'bzip2':
            import bz2
            self.data = bz2.decompress(StringIO(self.data)) # StringIO or not?
            self.encoding = guess_encoding(self.data)
        elif self.encoding == 'base64':
            import base64
            self.data = base64.decodestring(self.data)
            self.encoding = guess_encoding(self.data)


class MtConverterError(Exception):
    """base class for this package's errors"""

class MissingBinary(MtConverterError):
    """raised when a system binary on whic rely a transform has not been found
    """
class TransformError(MtConverterError):
    """raised when something can't be transformed due to missing necessary
    transforms
    """


def register_pil_transforms(engine, verb=True):
    try:
        from logilab.mtconverter.transforms import piltransforms
    except ImportError:
        # pil not available, do nothing
        if verb:
            print "PIL isn't available, image transforms won't be available'"
        return False
    else:
        for trclass in piltransforms.transform_classes:
            engine.add_transform(trclass())
        return True


def register_pygments_transforms(engine, verb=True):
    try:
        from logilab.mtconverter.transforms import pygmentstransforms
    except ImportError:
        # pygments not available, do nothing
        if verb:
            print "PYGMENTS isn't available, transforms won't be available'"
        return False
    else:
        for trclass in pygmentstransforms.transform_classes:
            engine.add_transform(trclass())
        return True


def register_base_transforms(engine, verb=True):
    from logilab.mtconverter.transforms import cmdtransforms, text_to_text, \
         xml_to_text, text_to_html, xlog_to_html
    from logilab.mtconverter.transforms.python import python_to_html
    from logilab.mtconverter.transforms.html2text import html_to_formatted_text
    from logilab.mtconverter.transforms.odt2text import odt_to_unformatted_text
    from logilab.mtconverter.transforms.pgpsignature import pgpsignature_to_text
    engine.add_transform(text_to_text())
    engine.add_transform(xml_to_text())
    engine.add_transform(text_to_html())
    engine.add_transform(xlog_to_html())
    engine.add_transform(python_to_html())
    engine.add_transform(html_to_formatted_text())
    engine.add_transform(odt_to_unformatted_text())
    engine.add_transform(pgpsignature_to_text())
    for trclass in cmdtransforms.transform_classes:
        try:
            engine.add_transform(trclass())
        except MissingBinary, ex:
            if verb:
                print ex
    return True
