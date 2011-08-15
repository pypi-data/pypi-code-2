# -*- coding: utf-8 -*-

from urecord import Record

from intessa.conneg import ContentType
from intessa.conneg.default import DEFAULT_REGISTER

class Response(Record('api',
                      # The essence of an HTTP response:
                      'status_code',
                      'headers',
                      'content',
                      'codec_register')):

    """
    An HTTP response, created by calling an :class:`intessa.api.API`.

    The following attributes all need to be set when constructing a response.

    .. py:attribute:: api

        The :class:`intessa.api.API` instance which created this Response.

    .. py:attribute:: status_code

        An integer representing the HTTP status code of the response.

    .. py:attribute:: headers

        A case-insensitive dictionary (or dict-like object) containing header
        names and values.

    .. py:attribute:: content

        A bytestring (i.e. ``str`` instance) containing the body of the
        response.

    You may optionally set the following:

    .. py:attribute:: codec_register

        An instance of :class:`intessa.conneg.codec_base.CodecRegister`, to be
        used for decoding this response. Defaults to
        :data:`~intessa.conneg.default.DEFAULT_REGISTER`.

    All the other attributes are dynamically created by the class itself.
    """

    def __new__(cls, api, status_code, headers, content,
                codec_register=DEFAULT_REGISTER):
        return super(cls, cls).__new__(cls, api=api,
                                       status_code=status_code,
                                       headers=headers, content=content,
                                       codec_register=codec_register)

    def __repr__(self):
        if 'content-type' in self.headers:
            mimetype = self.headers['content-type'].split(';')[0]
            return '<intessa.Response[%d, %s]>' % (self.status_code, mimetype)
        return '<intessa.Response[%d]>' % (self.status_code,)

    @property
    def type(self):

        """
        A :class:`intessa.conneg.ContentType` for this response.

        Use this to implement conditional handling of various types.

        :raises: ``AttributeError`` if no Content-Type header was given.

        Example::

            >>> resp = Response(None, 200,
            ...     {'content-type': 'text/html; charset=utf-8'},
            ...     '<html></html>')
            >>> resp.type
            ContentType('text/html; charset=utf-8')
            >>> resp.type.media_type
            'text/html'
            >>> resp.type.params['charset']
            'utf-8'
        """

        if 'content-type' not in self.headers:
            raise AttributeError("Response does not have a content type")
        return ContentType(self.headers['content-type'])

    @property
    def value(self):

        ur"""
        The content of this HTTP response, decoded into a Python object.

        This method uses the :attr:`codec_register` to decode responses. An
        object is retrieved simply by passing the content type and content
        bytestring into ``codec_register.decode()``.

        Note that the object will be decoded once per access; store a reference
        to the returned object if you wish to use it more than once.

            >>> json = Response(None, 200,
            ...     {'content-type': 'application/json'},
            ...     '{"a": 1}')
            >>> json.value
            {'a': 1}

            >>> text = Response(None, 200,
            ...     {'content-type': 'text/plain; charset=utf-8'},
            ...     'H\xc3\xa9llo W\xc3\xb6rld')
            >>> text.value
            u'H\xe9llo W\xf6rld'
        """

        return self.codec_register.decode(self.type, self.content)
