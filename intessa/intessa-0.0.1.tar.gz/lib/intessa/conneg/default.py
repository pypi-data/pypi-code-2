# -*- coding: utf-8 -*-

"""Houses the default global codec register and codecs."""

import simplejson
import lxml.etree
import lxml.objectify

from intessa.conneg.codec_base import CodecRegister, Codec
from intessa.conneg.content_type import ContentType


DEFAULT_REGISTER = CodecRegister()


class TextCodec(Codec):

    """Default text codec."""

    def encode(media_type, string, encoding='utf-8', errors='strict'):

        ur"""
        Encode a unicode string as a bytestring using an encoding.

        :param encoding:
            The encoding to use (default: ``'utf-8'``).
        :param errors:
            The strategy for handling encoding errors (default: ``'strict'``).
            See the documentation on the built-in ``unicode.encode()`` for more
            information about this option.

            >>> TextCodec.encode('text/plain', u"Héllo Wörld")
            (ContentType('text/plain; charset=utf-8'), 'H\xc3\xa9llo W\xc3\xb6rld')
            >>> TextCodec.encode('text/plain', u"Héllo Wörld", encoding='latin1')
            (ContentType('text/plain; charset=latin1'), 'H\xe9llo W\xf6rld')
        """

        encoded = string.encode(encoding, errors)
        c_type = ContentType('%s; charset=%s' % (media_type, encoding))
        return (c_type, encoded)

    def decode(c_type, bytes):

        ur"""
        Decode a bytestring to unicode, using the content type's charset.

            >>> TextCodec.decode(ContentType('text/plain; charset=utf-8'),
            ...                  'H\xc3\xa9llo W\xc3\xb6rld')
            u'H\xe9llo W\xf6rld'
            >>> TextCodec.decode(ContentType('text/plain; charset=latin1'),
            ...                              'H\xe9llo W\xf6rld')
            u'H\xe9llo W\xf6rld'

        If no charset is present, this method assumes the input is UTF-8::

            >>> TextCodec.decode(ContentType('text/plain'),
            ...                  'H\xc3\xa9llo W\xc3\xb6rld')
            u'H\xe9llo W\xf6rld'

        The decoder always uses 'strict' error handling::

            >>> TextCodec.decode(ContentType('text/plain; charset=us-ascii'), # doctest: +ELLIPSIS
            ...                  'H\xc3\xa9llo W\xc3\xb6rld')
            Traceback (most recent call last):
            ...
            UnicodeDecodeError: 'ascii' codec can't decode byte 0xc3 in position 1: ordinal not in range(128)
        """

        return bytes.decode(c_type.params.get('charset', 'utf-8'))

DEFAULT_REGISTER['text/plain'] = TextCodec


class JSONCodec(Codec):

    """Default JSON codec, powered by simplejson."""

    def encode(media_type, obj, **params):

        r"""
        Encode an object as JSON using ``simplejson.dumps()``.

        Additional parameters will be passed to ``simplejson.dumps()`` as-is.

            >>> JSONCodec.encode('application/json', {"a": 1})
            ('application/json', '{"a": 1}')
            >>> JSONCodec.encode('application/json', {"a": 1}, indent=True)
            ('application/json', '{\n "a": 1\n}')
        """

        return (media_type, simplejson.dumps(obj, **params))

    def decode(content_type, bytes):

        """
        Decode a JSON bytestring using ``simplejson.loads()``.

            >>> JSONCodec.decode('application/json', '{"a": 1}')
            {'a': 1}
        """

        return simplejson.loads(bytes)

DEFAULT_REGISTER['application/json'] = JSONCodec
DEFAULT_REGISTER['text/javascript'] = JSONCodec


class XMLCodec(Codec):

    """Default XML codec, using ``lxml.objectify``."""

    def encode(media_type, etree, **params):

        ur"""
        Encode an lxml ``ElementTree`` using ``lxml.etree.tostring()``.

        By default, the output will include an XML prolog, and will be
        utf-8-encoded. This can be overridden by passing ``xml_declaration``
        (``True`` or ``False``, default ``True``) and ``encoding`` (default
        ``'utf-8'``) keywords.

        See http://lxml.de/api/lxml.etree-module.html#tostring for a detailed
        overview of available options.

            >>> tree = lxml.etree.fromstring('<obj><attr>value</attr></obj>')
            >>> tree.find('attr').text = u"vålúè"
            >>> XMLCodec.encode('application/xml', tree)
            ('application/xml', "<?xml version='1.0' encoding='utf-8'?>\n<obj><attr>v\xc3\xa5l\xc3\xba\xc3\xa8</attr></obj>")
        """

        params.setdefault('xml_declaration', True)
        params.setdefault('with_tail', False)
        if params['xml_declaration']:
            params.setdefault('encoding', 'utf-8')

        return (media_type, lxml.etree.tostring(etree, **params))

    def decode(content_type, bytes):

        """
        Decode an XML bytestring to a Python object, using ``lxml.objectify``.

        For more information on these objects, see
        http://lxml.de/objectify.html.

            >>> doc = XMLCodec.decode('application/xml', '<obj><attr>value</attr></obj>')
            >>> doc # doctest: +ELLIPSIS
            <Element obj at 0x...>
            >>> doc.tag
            'obj'
            >>> doc.attr
            'value'
        """

        return lxml.objectify.fromstring(bytes)

DEFAULT_REGISTER['application/xml'] = XMLCodec
