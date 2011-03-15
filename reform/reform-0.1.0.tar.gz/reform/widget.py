from functools import partial

from markupsafe import Markup

try:
    from collections import OrderedDict
except ImportError:
    from _ordered_dict import OrderedDict

def _flatten_mappings(args, kwargs):
    if args:
        d = OrderedDict()

        for arg in args:
            d.update(arg)
        d.update(kwargs)

        return d
    else:
        return kwargs

class Attribute(object):
    '''Mock form._FieldAttribute. Used for testing:

        >>> a = Attribute(name='name', data='value')
        >>> a.name
        'name'
        >>> a.data
        'value'
        >>> a.id()
        'name'
        >>> a.label()
        'Name'

        >>> a = Attribute(id='id', label='Label')
        >>> a.id()
        'id'
        >>> a.label()
        'Label'
    '''
    def __init__(self, **kwargs):
        self._id = kwargs.pop('id', '')
        self._label = kwargs.pop('label', '')
        self.__dict__.update(kwargs)

    def id(self):
        if self._id or self._id is None:
            return self._id
        else:
            return self.name

    def label(self):
        if self._label or self._label is None:
            return self._label
        else:
            return self.name.replace('_', ' ').title()


def xml_attrs(*args, **kwargs):
    r'''Convert the mapping `kwargs` into XML style attributes. It returns a
    `Markup` object thats convertible to an `unicode` string or a regular `str`
    string:

        >>> s = xml_attrs(attribute='my attribute')
        >>> s
        Markup(u"attribute='my attribute'")
        >>> unicode(s)
        u"attribute='my attribute'"
        >>> str(s)
        "attribute='my attribute'"

    There's no need to escape specials characters before calling `xml_attrs`:

        >>> xml_attrs(attribute="'';!--\"<XSS>=&{()}")
        Markup(u"attribute='&#39;&#39;;!--&#34;&lt;XSS&gt;=&amp;{()}'")

    If you need to have attributes in order, you can pass a list of 2-tuples:

        >>> xml_attrs([('one', 1), ('two', 'II'), ('three', 'thr33')])
        Markup(u"one='1' two='II' three='thr33'")

    You can mix both methods, the keyword arguments will be at the end:
        >>> xml_attrs([('first', 1)], second=2)
        Markup(u"first='1' second='2'")

    If a value is `True`, its name is used as value:

        >>> xml_attrs(checked=True)
        Markup(u"checked='checked'")

    If a value is `None` or `False`, the attribute is ignored:

        >>> xml_attrs(foo=None, bar=False)
        Markup(u'')

    If an attribute is specified twice, only the last value will be kept:

        >>> xml_attrs([('foo', 'ignored'), ('foo', 'kept')])
        Markup(u"foo='kept'")

        >>> xml_attrs([('foo', 'ignored'), ('foo', 'ignored too')],
        ...           foo='kept')
        Markup(u"foo='kept'")
    '''
    def attr(key, value):
        # If value is None or False, this function wont be called
        if value is True:
            value = key
        if key in ('class_', 'for_'):
            key = key.rstrip('_')
        return Markup("{0}='{1}'").format(key, value)

    attrs = _flatten_mappings(args, kwargs)

    return Markup(u' ').join(attr(k, v)
                             for k, v in attrs.iteritems()
                             if v not in (None, False))

def tag(name, content=None, *args, **kwargs):
    '''FIXME'''
    x = Markup(u'<' + name)
    attributes = xml_attrs(*args, **kwargs)
    if attributes:
        x += ' ' + attributes
    if content is None:
        return x + Markup('/>')
    else:
        return x + Markup('>') + content + Markup('</' + name + '>')

def input(attribute, *args, **kwargs):
    '''Return a generic input tag:

        >>> input(Attribute(name='my name', data='my data'))
        Markup(u"<input id='my name' name='my name' value='my data'/>")

    By default `input` add an attribute `id` to the tag. If you want to
    override it pass the keyword argument `id`:

        >>> input(Attribute(name='my name', data='my data'), id=None)
        Markup(u"<input name='my name' value='my data'/>")
        >>> input(Attribute(name='my name', data='my data'), id='my id')
        Markup(u"<input id='my id' name='my name' value='my data'/>")

    Use keywords arguments to add more attributes to the input:

        >>> input(Attribute(name='my name', data='my data'), type='hidden')
        Markup(u"<input id='my name' name='my name' value='my data' type='hidden'/>")

    `class` is a python keyword, which mean you can't use it as a keyword
    argument. To specify the class of an input, use `class_`:

        >>> input(Attribute(name='my name', data='my data'), class_='x')
        Markup(u"<input id='my name' name='my name' value='my data' class='x'/>")
    '''
    od = OrderedDict([('id', attribute.id()),
                      ('name', attribute.name),
                      ('value', attribute.data)])
    od.update(_flatten_mappings(args, kwargs))

    return tag('input', None, od)

def checkbox(attribute, *args, **kwargs):
    '''Return an input of type `checkbox`. It uses `attribute.value` to
    determine if the checkbox is checked. You can override this by passing
    the parameter `checked` with a boolean:

        checkbox(..., checked=True) or checkbox(..., checked=False)

    Note that the returned tag wont have any value attribute, since it is
    irrelevant in checkboxes.
    '''
    od = OrderedDict([
        # FIXME value seems to be useless for checkboxes. Need to
        # learn more about that.
        ('value', None),
        ('type', 'checkbox'),
        ('checked', bool(attribute.data)),
    ])

    od.update(_flatten_mappings(args, kwargs))

    return input(attribute, od)

def label(attribute, *args, **kwargs):
    od = OrderedDict(for_=attribute.id(), label=attribute.label())
    od.update(_flatten_mappings(args, kwargs))

    label = od.pop('label')

    return tag('label', label, od)

def textarea(attribute, *args, **kwargs):
    od = OrderedDict([('id', attribute.id()), ('name', attribute.name)])
    od.update(_flatten_mappings(args, kwargs))

    return tag('textarea', attribute.data, od)

def select(attribute, *args, **kwargs):
    if not hasattr(attribute.field, 'values'):
        raise ValueError('attribute.field.values is absent')

    options = (tag('option', text,
                   [('value', value), ('selected', (value == attribute.data))])
               for value, text in attribute.field.values.iteritems())
    indent = Markup('\n' + ' ' * 4)
    options = indent + indent.join(options) + '\n'

    od = OrderedDict([('id', attribute.id()), ('name', attribute.name)])
    od.update(_flatten_mappings(args, kwargs))

    return tag('select', options, od)

# Create helper functions so there's no need to specify the type of input each
# time. For example instead of `input(..., type='password')` use `password(...)`.
_input_types = ('text', 'password', 'checkbox', 'radio', 'button', 'submit',
                'reset', 'file', 'hidden', 'image', 'datetime',
                'datetime-local', 'date', 'month', 'time', 'week', 'number',
                'range', 'email', 'url', 'search', 'tel', 'color')

# FIXME the buildin function range() will be overiden. Keep this at the bottom
# of the source file.
jinja_filters = dict(xml_attrs=xml_attrs,
                     input=input,
                     checkbox=checkbox,
                     label=label,
                     textarea=textarea,
                     select=select)

_globals = globals()

for t in _input_types:
    function_name = t.replace('-', '_')

    if function_name in _globals: # If the function is already defined, skip it.
        continue

    _input = partial(input, type=t)
    _input.__name__ = function_name
    _input.__doc__ = '''Return an input of type `{type}`'''.format(type=t)

    _globals[function_name] = _input
    jinja_filters[function_name] = _input

__all__ = (('jinja_filters',) + tuple(jinja_filters.iterkeys()))

if __name__ == '__main__': # pragma: nocover
    for t in _input_types:
        f = globals()[t.replace('-', '_')]
        print f(Attribute(name='name', data='value'))

    print text(Attribute(name='name', data='value'))
    print password(Attribute(name='name', data='value'))
    print checkbox(Attribute(name='name', data='value'), checked=True)
    print checkbox(Attribute(name='name', data='value'), checked=False)
