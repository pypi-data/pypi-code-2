# -*- coding: utf-8 -*-
"""String formatting for Python 2.5.

This is an implementation of the advanced string formatting (PEP 3101).

Author: Florent Xicluna
"""

import re

_format_str_re = re.compile(
    r'((?<!{)(?:{{)+'                       # '{{'
    r'|(?:}})+(?!})'                        # '}}
    r'|{(?:[^{](?:[^{}]+|{[^{}]*})*)?})'    # replacement field
)
_format_sub_re = re.compile(r'({[^{}]*})')  # nested replacement field
_format_spec_re = re.compile(
    r'((?:[^{}]?[<>=^])?)'      # alignment
    r'([-+ ]?)'                 # sign
    r'(#?)' r'(\d*)' r'(,?)'    # base prefix, minimal width, thousands sep
    r'((?:\.\d+)?)'             # precision
    r'(.?)$'                    # type
)
_field_part_re = re.compile(
    r'(?:(\[)|\.|^)'            # start or '.' or '['
    r'((?(1)[^]]*|[^.[]*))'     # part
    r'(?(1)(?:\]|$)([^.[]+)?)'  # ']' and invalid tail
)


def _strformat(value, format_spec=""):
    """Internal string formatter.

    It implements the Format Specification Mini-Language.
    """
    m = _format_spec_re.match(str(format_spec))
    if not m:
        raise ValueError('Invalid conversion specification')
    align, sign, prefix, width, comma, precision, conversion = m.groups()
    is_numeric = hasattr(value, '__float__')
    is_integer = is_numeric and hasattr(value, '__index__')
    if prefix and not is_integer:
        raise ValueError('Alternate form (#) not allowed in %s format '
                         'specifier' % ('float' if is_numeric else 'string'))
    if is_numeric and conversion == 'n':
        # Default to 'd' for ints and 'g' for floats
        conversion = 'd' if is_integer else 'g'
    elif sign and not is_numeric:
        raise ValueError('Sign not allowed in string format specifier')
    if comma:
        # TODO: thousand separator
        pass
    try:
        if ((is_numeric and conversion == 's') or
            (not is_integer and conversion in set('cdoxX'))):
            raise ValueError
        rv = ('%' + prefix + precision + (conversion or 's')) % (value,)
    except ValueError:
        raise ValueError("Unknown format code %r for object of type %r" %
                         (conversion, value.__class__.__name__))
    if sign not in '-' and value >= 0:
        # sign in (' ', '+')
        rv = sign + rv
    if not width:
        return rv
    zero = (width[0] == '0')
    width = int(width)
    if width <= len(rv):
        return rv
    fill, align = align[:-1], align[-1:]
    if not fill:
        fill = '0' if zero else ' '
    if align == '^':
        padding = width - len(rv)
        # tweak the formatting if the padding is odd
        if padding % 2:
            rv += fill
        rv = rv.center(width, fill)
    elif align == '=' or (zero and not align):
        if not is_numeric:
            raise ValueError("'=' alignment not allowed in string format "
                             "specifier")
        if value < 0 or sign not in '-':
            rv = rv[0] + rv[1:].rjust(width - 1, fill)
        else:
            rv = rv.rjust(width, fill)
    elif align in ('>', '=') or (is_numeric and not align):
        # numeric value right aligned by default
        rv = rv.rjust(width, fill)
    else:
        rv = rv.ljust(width, fill)
    return rv


def _format_field(value, parts, conv, spec):
    """Format a replacement field."""
    for k, part, _ in parts:
        if k:
            if part.isdigit():
                value = value[int(part)]
            else:
                value = value[part]
        else:
            value = getattr(value, part)
    if conv:
        value = ('%r' if (conv == 'r') else '%s') % (value,)
    if hasattr(value, '__format__'):
        value = value.__format__(spec)
    elif hasattr(value, 'strftime') and spec:
        value = value.strftime(str(spec))
    else:
        value = _strformat(value, spec)
    return value


class FormattableString(object):
    """Class which implements method format().

    The method format() behaves like str.format() in python 2.6+.

    >>> FormattableString(u'{a:5}').format(a=42)
    ... # Same as u'{a:5}'.format(a=42)
    u'   42'

    """

    __slots__ = '_index', '_kwords', '_nested', '_string', 'format_string'

    def __init__(self, format_string):
        self._index = 0
        self._kwords = {}
        self._nested = {}

        self.format_string = format_string
        self._string = _format_str_re.sub(self._prepare, format_string)

    def __eq__(self, other):
        if isinstance(other, FormattableString):
            return self.format_string == other.format_string
        # Compare equal with the original string.
        return self.format_string == other

    def _prepare(self, match):
        # Called for each replacement field.
        part = match.group(0)
        if part[0] == part[-1]:
            # '{{' or '}}'
            assert part == part[0] * len(part)
            return part[:len(part) // 2]
        repl = part[1:-1]
        field, _, format_spec = repl.partition(':')

        literal, _, conversion = field.partition('!')
        name_parts = _field_part_re.findall(literal)
        if literal[:1] in '.[':
            # Auto-numbering
            if self._index is None:
                raise ValueError(
                    "cannot switch from manual field specification "
                    "to automatic field numbering")
            name = str(self._index)
            self._index += 1
            if not literal:
                del name_parts[0]
        else:
            name = name_parts.pop(0)[1]
            if name.isdigit() and self._index is not None:
                # Manual specification
                if self._index:
                    raise ValueError(
                        "cannot switch from automatic field numbering "
                        "to manual field specification")
                self._index = None
        for k, v, tail in name_parts:
            if not v:
                raise ValueError("Empty attribute in format string")
            if tail:
                raise ValueError("Only '.' or '[' may follow ']' "
                                 "in format field specifier")
        if name_parts and k == '[' and not literal[-1] == ']':
            raise ValueError("Missing ']' in format string")
        if '{' in format_spec:
            format_spec = _format_sub_re.sub(self._prepare, format_spec)
            rv = (name_parts, conversion, format_spec)
            self._nested.setdefault(name, []).append(rv)
        else:
            rv = (name_parts, conversion, format_spec)
            self._kwords.setdefault(name, []).append(rv)
        return r'%%(%s)s' % id(rv)

    def format(self, *args, **kwargs):
        """Same as str.format() and unicode.format() in Python 2.6+."""
        if args:
            kwargs.update(dict((str(i), value)
                               for (i, value) in enumerate(args)))
        params = {}
        for name, items in self._kwords.items():
            value = kwargs[name]
            for item in items:
                parts, conv, spec = item
                params[str(id(item))] = _format_field(value, parts, conv, spec)
        for name, items in self._nested.items():
            value = kwargs[name]
            for item in items:
                parts, conv, spec = item
                spec = spec % params
                params[str(id(item))] = _format_field(value, parts, conv, spec)
        return self._string % params


def selftest():
    import datetime
    F = FormattableString

    assert F(u"{0:{width}.{precision}s}").format('hello world',
             width=8, precision=5) == u'hello   '

    d = datetime.date(2010, 9, 7)
    assert F(u"The year is {0.year}").format(d) == u"The year is 2010"
    assert F(u"Tested on {0:%Y-%m-%d}").format(d) == u"Tested on 2010-09-07"
    print 'Test successful'

if __name__ == '__main__':
    selftest()
