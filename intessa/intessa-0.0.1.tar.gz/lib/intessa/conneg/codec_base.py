from urecord import Record

from intessa.conneg.content_type import ContentType


class CodecRegister(dict):

    r"""
    A dictionary mapping media types to :class:`Codecs <Codec>`.

    Keys should be media types as bytestrings, and values should be
    :class:`Codec` subclasses (or at least match the decode/encode interface).

    As an example, start by defining a codec::

        >>> import simplejson
        >>> class JSONCodec(Codec):
        ...     def encode(media_type, obj, **params):
        ...         return (media_type, simplejson.dumps(obj, **params))
        ...     def decode(content_type, bytes):
        ...         return simplejson.loads(bytes)

    Create a register and add the codec to it::

        >>> reg = CodecRegister()
        >>> reg['application/json'] = JSONCodec
        >>> reg['application/json'] is JSONCodec
        True

    You can then encode and decode objects using the same method signatures as
    on individual codecs. The codec register will dispatch based on the media
    type provided::

        >>> reg.encode('application/json', {"a": 1})
        ('application/json', '{"a": 1}')
        >>> reg.encode('application/json', {"a": 1}, indent=True)
        ('application/json', '{\n "a": 1\n}')
        >>> reg.decode('application/json', '{"a": 1}')
        {'a': 1}
    """

    def encode(self, media_type, obj, **params):
        encoded = self[media_type].encode(media_type, obj, **params)
        if isinstance(encoded, str):
            return (media_type, encoded)
        return encoded

    def decode(self, content_type, bytes):
        if not isinstance(content_type, ContentType):
            content_type = ContentType(content_type)
        return self[content_type.media_type].decode(content_type, bytes)


class Codec(object):

    """
    A superclass for implementing codecs.
    
    This class should be considered abstract (:meth:`encode` and :meth:`decode`
    are unimplemented), but it has a metaclass which will make those methods
    static.

    Example::

        >>> import simplejson
        >>> class JSONCodec(Codec):
        ...     def encode(media_type, obj, **params):
        ...         return (media_type, simplejson.dumps(obj, **params))
        ...     def decode(content_type, bytes):
        ...         return simplejson.loads(bytes)
        >>> JSONCodec.encode('application/json', {"a": 1})
        ('application/json', '{"a": 1}')
        >>> JSONCodec.decode('application/json', '{"a": 1}')
        {'a': 1}

    Note that ``encode()`` and ``decode()`` do not take ``self``; the metaclass
    will make them static methods automatically. This allows you to register
    the classes directly on a :class:`CodecRegister`.
    """

    class __metaclass__(type):
        def __new__(mcls, name, bases, attrs):
            if 'decode' in attrs:
                attrs['decode'] = staticmethod(attrs['decode'])
            if 'encode' in attrs:
                attrs['encode'] = staticmethod(attrs['encode'])
            return super(mcls, mcls).__new__(mcls, name, bases, attrs)

    def encode(media_type, obj, **params):

        """
        Encode a Python object into the given media type.

        :param media_type:
            The desired ``type/subtype`` media type for the output.
        :param obj:
            The Python object to encode.
        :params: Any additional parameters for the encoder.
        :returns:
            A two-tuple of ``(content_type, bytes)``, where ``content_type``
            should be a ``str`` of the full ``Content-Type`` header (including
            parameters) and ``bytes`` a ``str`` of the encoded output.
        """

        raise NotImplementedError

    def decode(content_type, bytes):

        """
        Decode a bytestring to a Python object, given its content-type.

        :param intessa.conneg.ContentType content_type:
            The declared ``Content-Type`` header from the HTTP server.
        :param str bytes:
            A string of the content itself.
        :returns: A Python object.
        """

        raise NotImplementedError
