"""Utilities for creating and manipulating HTTP ``Accept`` headers."""

from content_type import ContentType


def make_accept_header(spec):

    """
    Build an accept header.

    Works on single strings:

        >>> make_accept_header('text/html')
        'text/html'

    Works on iterables of strings:

        >>> make_accept_header(('text/html', 'application/json'))
        'text/html,application/json'

    Works on iterables of type/quality pairs:

        >>> make_accept_header((('text/html', 0.7), ('application/json', 0.9)))
        'text/html;q=0.7,application/json;q=0.9'

    And mixed input:

        >>> make_accept_header((('text/html', 0.7), 'application/json'))
        'text/html;q=0.7,application/json'
    """

    if isinstance(spec, basestring):
        return ContentType(spec).media_type

    output = []
    for c_type in spec:
        if isinstance(c_type, basestring):
            output.append(ContentType(c_type).media_type)
        else:
            media_type = ContentType(c_type[0]).media_type
            quality = c_type[1]
            output.append('%s;q=%.1f' % (media_type, quality))
    return ','.join(output)
