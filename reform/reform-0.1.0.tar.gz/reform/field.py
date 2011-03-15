'''
All fields derive from the :class:`Field` class. A field has 2 methods:
:meth:`Field.validate` and :meth:`Field.convert`. `validate` is called first,
and if the value is valid, `convert` is called.
'''
import re

try:
    from collections import OrderedDict
except ImportError:
    from _ordered_dict import OrderedDict

class StopValidation(Exception):
    '''Raise this exception inside a validator to stop calling other
    validators.'''
    pass


class Field(object):
    '''If `required` is `True`, the field has to be present and non-empty.
    `default` is the value returned if the field is empty or absent.

    `id` and `label` are the tag's id and its label text. For example::

        Field(id='field1', label='The First Field')

    Its tag will look like::

        <... id='field1' ...>

    And its label will be::

        <label for='field1'>The First Field</label>
    '''
    # Set this to true to stop the validation as soon as there is an error.
    stop_on_error = False

    def __init__(self, required=False, default=None, id=None, label=None):
        self.required = required
        self.default = default
        self.id = id
        self.label = label

    def validate(self, value):
        '''Return an error if the field is invalid. If the field is valid it
        doesn't return anything::

            >>> f = Field(required=True)
            >>> f.validate('something')
            >>> f.validate('')
            u'Required'

        It can also raise a ``StopValidation`` exception. In this case the
        arguments are used as errors::

            raise StopValidation(u'Some error')

        ``u'Some error'`` will be added in the error list.
        '''
        if self.required and not value:
            return u'Required'

    @staticmethod
    def convert(value):
        '''Convert `value` into its Python equivalent. By default it just
        return the passed value.
        '''
        return value


class String(Field):
    '''You can specify its minimum and maximum length with ``min_length`` and
    ``max_length``::

        >>> s = String(min_length=2, max_length=4)
        >>> s.validate('123')
        >>> s.validate('too long')
        u'Must be less than 4 characters long'
        >>> s.validate('x')
        u'Must be at least 2 characters long'
    '''
    def __init__(self, min_length=None, max_length=None, **kwargs):
        super(String, self).__init__(**kwargs)

        if min_length and max_length:
            assert min_length <= max_length
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, value):
        if self.min_length and len(value) < self.min_length:
            return (u'Must be at least {0} characters long'.
                    format(self.min_length))
        elif self.max_length and len(value) > self.max_length:
            return (u'Must be less than {0} characters long'.
                    format(self.max_length))


class Integer(Field):
    '''An integer field. The integer conversion is done by the builtin method
    ``int()``. ``base`` is the number's base::

        >>> Integer().validate('123')
        >>> Integer().validate('bad number')
        u'Invalid number'
        >>> Integer().convert('123')
        123

    Note that you can use prefixes for the octal and hexadecimal bases::

        >>> Integer(base=8).convert('0123')
        83
        >>> Integer(base=16).convert('0x123')
        291


    ``min`` and ``max`` can be used to set the limits of the integer. Those
    parameters are inclusive. This means that ``max=100`` will accept 100 as a
    valid value::

        >>> Integer(max=10).validate('10')
        >>> Integer(max=10).validate('11')
        u'Must be less than 11'
    '''
    def __init__(self, base=10, min=None, max=None, **kwargs):
        super(Integer, self).__init__(**kwargs)
        self.base = base
        if min > max:
            raise ValueError('max must be greater than min')
        self.min = min
        self.max = max

    def validate(self, value):
        try:
            x = int(value, base=self.base)
        except ValueError:
            return u'Invalid number'

        if self.min and x < self.min:
            return u'Must be greater than {0}'.format(self.min - 1)
        if self.max and x > self.max:
            return u'Must be less than {0}'.format(self.max + 1)

    def convert(self, value):
        return int(value, base=self.base)


class Boolean(Field):
    def __init__(self, default=False, **kwargs):
        # FIXME
        if default is not False:
            raise ValueError('Boolean are always false when absent')
        super(Boolean, self).__init__(default=False, **kwargs)

    # No need for a validate method, a boolean value is True if it is present
    def convert(self, value):
        return bool(value)


class Choice(Field):
    def __init__(self, mapping, **kwargs):
        super(Choice, self).__init__(**kwargs)
        try:
            self.values = OrderedDict(mapping)
        except Exception:
            self.values = OrderedDict((x, x) for x in mapping)

    def validate(self, value):
        if value and value not in self.values:
            return u'Invalid choice'


class Email(Field):
    def validate(self, value):
        # Email validation is absurdly hard. Check test_emails.py for a list of
        # all the crazy things that are supposed to be valid email addresses.
        if value and '@' not in value[1:-1]:
            return u'Invalid email address'

    @staticmethod
    def convert(value):
        return value.strip()


_domain_name_regex = (
    r'''
    (
        [a-z0-9]
        ([a-z0-9]{,62}|([a-z0-9\-]*\-[a-z0-9]+))\.
    )+
    [a-z]{2,}
    ''')

class DomainName(Field):
    _compiled_regex = re.compile(r'(?ix)^' + _domain_name_regex + '$')

    def validate(self, value):
        if value and not self._compiled_regex.match(value.strip()):
            return u'Invalid domain name'


class URL(Field):
    # Regex shamelessly stolen from FormEncode
    _regex = ur'''(?ix)
        ^(?P<scheme>https?://)
        (?:[%:\w]*@)?           # authenticator
        ''' + _domain_name_regex + r'''
        (?::[0-9]+)?            # port

        # files/delims/etc
        (?P<path>/[a-z0-9\-\._~:/\?#\[\]@!%\$&\'\(\)\*\+,;=]*)?
        $'''
    _compiled_regex = re.compile(_regex)

    def __init__(self, add_http=True, **kwargs):
        super(URL, self).__init__(**kwargs)
        self._add_http = add_http

    def validate(self, value):
        if value and not self._compiled_regex.match(value.strip()):
            return u'Invalid URL'

    def convert(self, value):
        value = value.strip()

        if (not (value.startswith('http://') or
                 value.startswith('https://')) and
            self._add_http):
            return 'http://' + value
        else:
            return value


class Regex(String):
    def __init__(self, expression, error=u'Invalid', *args, **kwargs):
        super(Regex, self).__init__(*args, **kwargs)
        self._pattern = re.compile(expression)
        self._error = error

    def validate(self, value):
        if value and not self._pattern.match(value):
            return self._error


__all__ = ('Field', 'String', 'Integer', 'Boolean', 'Choice', 'Email', 'URL')
