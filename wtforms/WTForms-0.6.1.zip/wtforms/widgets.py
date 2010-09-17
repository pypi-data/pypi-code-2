from cgi import escape


__all__ = (
    'CheckboxInput', 'FileInput', 'HiddenInput', 'ListWidget', 'PasswordInput',
    'RadioInput', 'Select', 'SubmitInput', 'TableWidget', 'TextArea',
    'TextInput',
)


def html_params(**kwargs):
    """
    Generate HTML parameters from inputted keyword arguments.

    The output value is sorted by the passed keys, to provide consistent output
    each time this function is called with the same parameters.  Because of the
    frequent use of the normally reserved keywords `class` and `for`, suffixing
    these with an underscore will allow them to be used.

    >>> html_params(name='text1', id='f', class_='text')
    u'class="text" id="f" name="text1"'
    """
    params = []
    for k,v in sorted(kwargs.iteritems()):
        if k in ('class_', 'class__', 'for_'):
            k = k[:-1]
        params.append(u'%s="%s"' % (unicode(k), escape(unicode(v), quote=True)))
    return u' '.join(params)

class HTMLString(unicode):
    def __html__(self):
        return self


class ListWidget(object):
    """
    Renders a list of fields as a `ul` or `ol` list.

    This is used for fields which encapsulate many inner fields as subfields.
    The widget will try to iterate the field to get access to the subfields and
    call them to render them.

    If `prefix_label` is set, the subfield's label is printed before the field,
    otherwise afterwards. The latter is useful for iterating radios or
    checkboxes.
    """
    def __init__(self, html_tag='ul', prefix_label=True):
        assert html_tag in ('ol', 'ul')
        self.html_tag = html_tag
        self.prefix_label = prefix_label

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        html = [u'<%s %s>' % (self.html_tag, html_params(**kwargs))]
        for subfield in field:
            if self.prefix_label:
                html.append(u'<li>%s: %s</li>' % (subfield.label, subfield()))
            else:
                html.append(u'<li>%s %s</li>' % (subfield(), subfield.label))
        html.append(u'</%s>' % self.html_tag)
        return HTMLString(u''.join(html))


class TableWidget(object):
    """
    Renders a list of fields as a set of table rows with th/td pairs.

    If `with_table_tag` is True, then an enclosing <table> is placed around the
    rows.

    Hidden fields will not be displayed with a row, instead the field will be 
    pushed into a subsequent table row to ensure XHTML validity. Hidden fields
    at the end of the field list will appear outside the table.
    """
    def __init__(self, with_table_tag=True):
        self.with_table_tag = with_table_tag

    def __call__(self, field, **kwargs):
        html = []
        if self.with_table_tag:
            kwargs.setdefault('id', field.id)
            html.append(u'<table %s>' % html_params(**kwargs))
        hidden = u''
        for subfield in field:
            if subfield.type == 'HiddenField':
                hidden += unicode(subfield)
            else:
                html.append(u'<tr><th>%s</th><td>%s%s</td></tr>' % (unicode(subfield.label), hidden, unicode(subfield)))
                hidden = u''
        if self.with_table_tag:
            html.append(u'</table>')
        if hidden:
            html.append(hidden)
        return HTMLString(u''.join(html))


class Input(object):
    """
    Render a basic ``<input>`` field.

    This is used as the basis for most of the other input fields.

    By default, the `_value()` method will be called upon the associated field
    to provide the ``value=`` HTML attribute.
    """
    def __init__(self, input_type=None):
        if input_type is not None:
            self.input_type = input_type

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)
        if 'value' not in kwargs:
            kwargs['value'] = field._value()
        return HTMLString(u'<input %s />' % html_params(name=field.name, **kwargs))


class TextInput(Input):
    """
    Render a single-line text input.
    """
    input_type = 'text'


class PasswordInput(Input):
    """
    Render a password input.

    For security purposes, this field will not reproduce the value on a form
    submit by default. To have the value filled in, set `hide_value` to
    `False`.
    """
    input_type = 'password'

    def __init__(self, hide_value=True):
        self.hide_value = hide_value

    def __call__(self, field, **kwargs): 
        if self.hide_value:
            kwargs['value'] = ''
        return super(PasswordInput, self).__call__(field, **kwargs)


class HiddenInput(Input):
    """
    Render a hidden input.
    """
    input_type = 'hidden'


class CheckboxInput(Input):
    """
    Render a checkbox.

    The ``value=`` HTML attribute by default is 'y' unless otherwise specified
    by `value=` at rendering. The ``checked`` HTML attribute is set if the field's
    data is a non-false value.
    """
    input_type = 'checkbox'

    def __call__(self, field, **kwargs):
        if getattr(field, 'checked', field.data):
            kwargs['checked'] = u'checked'
        return super(CheckboxInput, self).__call__(field, **kwargs)


class RadioInput(Input):
    """
    Render a single radio button.

    This widget is most commonly used in conjunction with ListWidget or some
    other listing, as singular radio buttons are not very useful.
    """
    input_type = 'radio'

    def __call__(self, field, **kwargs):
        if field.checked:
            kwargs['checked'] = u'checked'
        return super(RadioInput, self).__call__(field, **kwargs)


class FileInput(Input):
    """
    Renders a file input chooser field.
    """
    input_type = 'file'


class SubmitInput(Input):
    """
    Renders a submit button.

    The field's label is used as the text of the submit button instead of the
    data on the field.
    """
    input_type = 'submit'

    def __call__(self, field, **kwargs): 
        kwargs.setdefault('value', field.label.text)
        return super(SubmitInput, self).__call__(field, **kwargs)


class TextArea(object):
    """
    Renders a multi-line text area.

    `rows` and `cols` ought to be passed as keyword args when rendering.
    """
    def __call__(self, field, **kwargs): 
        kwargs.setdefault('id', field.id)
        return HTMLString(u'<textarea %s>%s</textarea>' % (html_params(name=field.name, **kwargs), escape(unicode(field._value()))))

class Select(object):
    """
    Renders a select field.

    If `multiple` is True, then the `size` property should be specified on
    rendering to make the field useful.

    The field must provide an `iter_choices()` method which the widget will
    call on rendering; this method must yield tuples of 
    `(value, label, selected)`.
    """
    def __init__(self, multiple=False):
        self.multiple = multiple

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        if self.multiple:
            kwargs['multiple'] = 'multiple'
        html = [u'<select %s>' % html_params(name=field.name, **kwargs)]
        for val, label, selected in field.iter_choices():
            html.append(self.render_option(val, label, selected))
        html.append(u'</select>')
        return HTMLString(u''.join(html))

    @classmethod
    def render_option(cls, value, label, selected):
        options = {'value': value}
        if selected:
            options['selected'] = u'selected'
        return HTMLString(u'<option %s>%s</option>' % (html_params(**options), escape(unicode(label))))


class Option(object):
    """
    Renders the individual option from a select field. 
    
    This is just a convenience for various custom rendering situations, and an
    option by itself does not constitute an entire field.
    """
    def __call__(self, field, **kwargs):
        return Select.render_option(field._value(), field.label.text, field.checked)

