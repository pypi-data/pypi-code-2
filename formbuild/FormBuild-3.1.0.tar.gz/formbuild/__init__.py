# -*- coding: utf-8 -*-

"""\
Build HTML forms
"""

import logging
from cgi import escape
import re

from bn import HTMLFragment
from formbuild.internal import html_open, html_close, \
   check_attributes, handle_input, group, _checkable, _select, _split

log = logging.getLogger(__name__)

class Form(object):
    def __init__(
        self, 
        value=None, 
        error=None, 
        bag=None, 
        option=None, 
        checked=None, 
        table_class='formbuild'
    ):
        """
        ``options``
            an iterable of ``(value, label)`` pairs. The value is what's returned to
            the application if this option is chosen; the label is what's shown in the 
            form. You can also pass an iterable of strings in which case the labels will
            be identical to the values.
        """
        if value is None:
            self.value = {}
        else:
            self.value = value
            #for k in self.value:
            #    if not isinstance(self.value[k], unicode):
            #        raise Exception('Form values must always be a unicode string, the key %r is %r'%(k, self.value[k]))
        if error is None:
            self.error = {}
        else:
            self.error = error
            #for k in self.error:
            #    if not isinstance(self.error[k], unicode):
            #        raise Exception('Error messages must always be a unicode string, the key %r is %r'%(k, self.error[k]))
        if option is None:
            self.option = {}
        else:
            self.option = option
        if bag is None:
            self.bag = {}
        else:
            self.bag = bag
        if checked is None:
            self.checked = {}
        else:
           self.checked = checked
        self.table_class = table_class

    #
    # Form Methods
    #

    def start(self, action="", method="post", enctype=None, attributes=None):
        """\
        Open a form tag which submits via the POST method. You must close the
        form yourself.
        
        ``action`` 
            The URL the form will submit to. Defaults to ``''`` so that the 
            form submits to the current URL

        ``method``
            Can be ``post`` or ``get`` and affects the HTTP method used to
            submit the form.

        ``enctype``
            The encoding type, only usually set if your form contains fields 
            for uploading a file.

        ``attributes``
            A dictionary containing other HTML attributes (apart from 
            ``action``, ``method`` and ``enctype``)
 
        Here are some examples:
    
        >>> from formbuild import Form
        >>> form = Form()
        >>> print form.start("/submit")
        <form action="/submit" method="post">
        >>> print form.start("/submit", method="get")
        <form action="/submit" method="get">


        If your form contains file fields you must use ``method='post`` (the
        default) and also set the ``enctype`` attribute to contain the value
        ``"multipart/form-data"`` otherwise your browser will submit the 
        filename instead of the file content. Here's an example:

        >>> print form.start(
        ...     "/submit",
        ...     "post", 
        ...     enctype="multipart/form-data",
        ... )
        <form action="/submit" method="post" enctype="multipart/form-data">
        """                                         
        attributes = check_attributes(attributes, ['method', 'enctype', 'action'])
        if method.lower() in ['post', 'get']:
            attributes['method'] = method
        if enctype is not None:
            attributes['enctype'] = enctype
        attributes["action"] = action
        return html_open('form', False, attributes or {})

    def end(self, hidden_field_names=None):
        """\
        End a form, adding hidden fields for any values with names in the 
        ``hidden_field_names`` list.

        >>> form = Form()
        >>> print form.end()
        </form>
        >>> form = Form(value={'firstname': 'james', 'surname': 'garnder'})
        >>> print form.end(hidden_field_names=['firstname', 'surname'])
        <input type="hidden" name="firstname" value="james" />
        <input type="hidden" name="surname" value="garnder" />
        </form>
        """
        if hidden_field_names:
            return '\n'.join([
                '<input type="hidden" name="'+field+'" value="'+self.value.get(field, '')+'" />' for field in hidden_field_names
            ])+u'\n</form>'
        else:
            return u'</form>'

   #
   # Layout Methods
   #

    def start_layout(self, table_class=None):
        """\
        Start a layout without adding the form tag

        >>> form=Form()
        >>> print form.start_layout()
        <table>
        >>> print form.start_layout(table_class='form')
        <table class="form">
        """
        if table_class is None:
            return u'<table>'
        else:
            return u'<table class="%s">'%(escape(table_class))

    def end_layout(self):
        """\
        End a layout without adding the end form tag

        >>> form = Form()
        >>> print form.end_layout()
        </table>
        """
        return u'</table>'

    def start_with_layout(
        self,
        action='', 
        method="post", 
        enctype=None, 
        table_class=None, 
        attributes=None
    ):
        """\
        Start a form the way you would with ``start_form()`` but include the 
        HTML necessary for the use of the ``fields()`` helper. 
        
        >>> form=Form()
        >>> print form.start_with_layout('/action', method='post')
        <form action="/action" method="post"><table class="formbuild">
        >>> print form.start_with_layout('/action', method='post', table_class='form')
        <form action="/action" method="post"><table class="form">
        """
        attributes = check_attributes(attributes, ['method', 'enctype', 'action'])
        if method.lower() in ['post', 'get']:
            attributes['method'] = method
        if enctype is not None:
            attributes['enctype'] = enctype
        attributes["action"] = action
        html = html_open('form', False, attributes or {})
        if table_class is None and self.table_class is None:
            return html + u'<table>'
        else:
            return html + u'<table class="%s">'%(escape(table_class or self.table_class))

    def end_with_layout(self, hidden_field_names=None):
        """\
        End a form started with ``start_with_layout()``

        >>> form = Form()
        >>> print form.end_with_layout()
        </table></form>
        """
        html = ''
        html += '</table>'
        if hidden_field_names:
            html += '\n'.join([
                '<input type="hidden" name="'+field+'" value="'+self.value.get(field, '')+'" />' for field in hidden_field_names
            ])+u'\n</form>'
        else:
            html += u'</form>'
        return html

    def action_bar(self, escaped_html):
        """\
        Enter some HTML into the form layout starting at the same level as the
        fields.

        This is useful for generating an action bar containing submit buttons.

        ``escaped_html``
            An HTML string, properly escaped, containing all the fields to 
            appear in the action bar

        >>> form = Form()
        >>> print form.action_bar(
        ...     '\\n    '.join([
        ...         form.submit('submit', '< Back'),
        ...         form.submit('submit', 'Forward >')
        ...     ])
        ... )
        <tr>
          <td></td>
          <td colspan="2">
            <input type="submit" name="submit" value="&lt; Back" />
            <input type="submit" name="submit" value="Forward &gt;" />
          </td>
        </tr>
        """
        if isinstance(escaped_html, (list, tuple)):
            escaped_html = '\n'.join(escaped_html)
        return u'<tr>\n  <td></td>\n  <td colspan="2">\n    %s\n  </td>\n</tr>'%(
            escaped_html,
        )

    def row(self, escaped_html):
        """\
        Enter some HTML into the form layout as a new row.

        This is useful for form sections. For example:

        >>> form = Form()
        >>> print form.row('<h2>Extra Fields</h2>')
        <tr><td colspan="3"><h2>Extra Fields</h2></td></tr>
        """
        return '<tr><td colspan="3">'+escaped_html+'</td></tr>'

    def field(
        self,
        name, 
        type,
        label='',
        required=False, 
        label_desc='', 
        field_desc='',
        help='',
        field_pre='',
        attributes=None,
        args=None,
        side=True,
        colon=True,
        required_position='before',
    ):
        """\
        Format a field with a label. 
    
        ``label``
            The label for the field
    
        ``field``
            The HTML representing the field, wrapped in ``literal()``
    
        ``required``
             Can be ``True`` or ``False`` depending on whether the label 
             should be formatted as required or not. By default required 
             fields have an asterix.
    
        ``label_desc``
            Any text to appear underneath the label, level with ``field_desc``
    
        ``field_desc``
            Any text to appear underneath the field
    
        ``help``
            Any HTML or JavaScript to appear imediately to the right of the
            field which could be used to implement a help system on the form
    
        ``field_pre``
            Any HTML to appear immediately above the field.
    
        ``side``
            Whether the label goes at the side of the field or above it. 
            Defaults to ``True``, putting the label at the side.

        TIP: For future compatibility, always specify arguments explicitly 
        and do not rely on their order in the function definition.
    
        Here are some examples:
   
        >>> form = Form(value=dict(test=''))
        >>> print form.start_with_layout()
        <form action="" method="post"><table class="formbuild">
        >>> print form.field('test', 'text', 'email >', required=True)
        <tr class="field">
          <td class="label" valign="top" height="10">
            <span class="required">*</span><label for="test">email &gt;:</label>
          </td>
          <td class="field" valign="top">
            <input type="text" name="test" value="" />
          </td>
          <td rowspan="2" valign="top"></td>
        </tr>
        >>> print form.field(
        ...     'test',
        ...     'text',
        ...     label='email >',
        ...     label_desc='including the @ sign',
        ...     field_desc='Please type your email carefully',
        ...     help = 'No help available for this field',
        ...     required=True,
        ... )
        ...
        <tr class="field">
          <td class="label" valign="top" height="10">
            <span class="required">*</span><label for="test">email &gt;:</label>
          </td>
          <td class="field" valign="top">
            <input type="text" name="test" value="" />
          </td>
          <td rowspan="2" valign="top">No help available for this field
            </td>
        </tr>
        <tr class="description">
          <td class="label_desc" valign="top">
            <span class="small">including the @ sign</span>
          </td>
          <td class="field_desc" valign="top">
            <span class="small">Please type your email carefully</span>
          </td>
        </tr>
        >>> print form.end_with_layout()
        </table></form>

        An appropriate stylesheet to use to style forms generated with field() when
        the table class is specified as "formbuild" would be::
    
            table.formbuild span.error-message, table.formbuild div.error, table.formbuild span.required {
                font-weight: bold;
                color: #f00;
            }
            table.formbuild span.small {
                font-size: 85%;
            }
            table.formbuild form {
                margin-top: 20px;
            }
            table.formbuild form table td {
                padding-bottom: 3px;
            }
    
        """
        if type in ['checkbox_group', 'radio_group']:
            field_html = getattr(self, type)(
                name, 
                **(args or {})
            )
        else:
            field_html = getattr(self, type)(
                name, 
                attributes=attributes,
                **(args or {})
            )
        error = self.error.get(name)
        error_html = error and u'<div class="error">'+escape(error)+'</div>\n' or u''
        if side == True:
            html = """\
<tr class="field">
  <td class="label" valign="top" height="10">
    %(required_html_before)s<label for="%(label_for)s">%(label_html)s%(colon)s</label>%(required_html_after)s
  </td>
  <td class="field" valign="top">
    %(field_pre_html)s%(error_html)s%(field_html)s
  </td>
  <td rowspan="2" valign="top">%(help_html)s</td>
</tr>"""     %dict(
                required_html_after = required_position == 'after' and (required and u'<span class="required">*</span>' \
                   or u'<span style="visibility: hidden">*</span>') or '',
                required_html_before = required_position == 'before' and (required and u'<span class="required">*</span>' \
                   or u'<span style="visibility: hidden">*</span>') or '',
                label_for = name,
                label_html = escape(label),
                error_html = error_html,
                field_html = field_html,
                help_html = help and escape(help)+'\n    ' or '',
                field_pre_html = field_pre and escape(field_pre) or '',
                colon = colon and ":" or "",
            )
            if label_desc or field_desc:
                html += """
<tr class="description">
  <td class="label_desc" valign="top">
    <span class="small">%(label_desc_html)s</span>
  </td>
  <td class="field_desc" valign="top">
    <span class="small">%(field_desc_html)s</span>
  </td>
</tr>"""         %dict(
                    label_desc_html = label_desc,
                    field_desc_html = field_desc,
                )
        else:
            html = """\
<tr><td></td>
  <td valign="top">
     <table border="0">
        <tr>
          <td><label for="%(label_for)s">%(label_html)s%(colon)s</label></td><td>%(required_html)s</td><td><span class="small label_desc">%(label_desc_html)s</span></td>
        </tr>
     </table>
  </td>
  <td valign="top" rowspan="3">%(help_html)s</td>
</tr>
<tr><td></td>
  <td valign="top">%(field_pre_html)s%(error_html)s%(field_html)s</td>
</tr>
<tr><td></td>
  <td class="small field_desc" valign="top">%(field_desc_html)s</td>
</tr>"""%   dict(
                label_for = name,
                label_html = escape(label),
                help_html = help and escape(help)+'\n    ' or '',
                required_html = required and u'<span class="required">*</span>' \
                   or u'<span style="visibility: hidden">*</span>',
                error_html = error_html,
                field_html = field_html,
                field_pre_html = field_pre and escape(field_pre) or '',
                label_desc_html = label_desc,
                field_desc_html = field_desc,
                colon = colon and ":" or "",
            )
        return html

    #
    # Zero Value fields
    #

    def static(self, name):
        """\
        Return the static value instead of an HTML field.

        >>> form = Form(value=dict(name='James>'))
        >>> print form.static('name')
        James&gt;
        """
        value = self.value.get(name)
        return escape(unicode(value))

    def file(self, name, attributes=None):
        """\
        Creates a file upload field.
        
        If you are using file uploads then you will also need to set the 
        form's ``enctype`` attribute to ``"multipart/form-data"``

        Example:

        >>> form = Form()
        >>> print form.file('myfile')
        <input type="file" name="myfile" />

        Note: File fields cannot have a ``value`` attribute.
        """
        return handle_input(
            'file', 
            name, 
            None,
            attributes,
        )
    
    #
    # Single value fields
    #

    def password(self, name=u"password", attributes=None):
        """\
        Creates a password field

        ``name``
            Defaults to ``password``.

        >>> form = Form(value=dict(name='James>'))
        >>> print form.password('name')
        <input type="password" name="name" value="James&gt;" />
        """
        return handle_input(
            'password', 
            name, 
            self.value.get(name),
            attributes,
        )

    def hidden(self, name, attributes=None):
        """\
        Creates a hidden field.

        Note: You can also add hidden fields to a form in the ``end()`` or
        ``end_with_layout()`` fields by specifying the names of the all the 
        hidden fields you want added.
        """
        return handle_input(
            'hidden',
            name, 
            self.value.get(name),
            attributes,
        )

    def text(self, name, attributes=None):
        """\
        Create a text input field.
        
        >>> form = Form()
        >>> print form.text('name')
        <input type="text" name="name" />
        >>> form = Form(value=dict(name='James>'))
        >>> print form.text('name')
        <input type="text" name="name" value="James&gt;" />
        """
        return handle_input(
            'text',
            name, 
            self.value.get(name),
            attributes,
        )

    def textarea(self, name, attributes=None):
        """\
        Creates a textarea field.

        >>> form = Form(value=dict(name='James>'))
        >>> print form.textarea('name')
        <textarea name="name">James&gt;</textarea>
        """
        attributes = check_attributes(attributes, ['name'])
        attributes["name"] = name
        return html_open('textarea', False, attributes)+\
           escape(self.value.get(name) or u'')+u'</textarea>'
    
    #
    # Single value fields with read-only values set at desgin time
    #

    def image_button(self, name, value, src, alt=None, attributes=None):
        """\
        Create a submit button with an image background

        ``value``
            The value of the field. Also used as the ``alt`` text if ``alt``
            is not also specified.

        ``src``
            The URL of the image to use as the button

        ``alt``
            The text to use as the alt text

        >>> form = Form()
        >>> print form.image_button('go', 'Next', '../go.png', alt='Go')
        <input src="../go.png" alt="Go" type="image" name="go" value="Next" />
        """
        if alt is None:
            alt=value
        attributes = check_attributes(
            attributes, 
            ['type', 'name', 'value', 'src', 'alt']
        )
        attributes.update(
            dict(
                type='image',
                name=name, 
                value=value,
                src=src,
                alt=alt,
            )
        )
        return html_open('input', True, attributes)

    def submit(self, name='sumbit', value='Submit', attributes=None):
        """\
        Creates a submit button with the text ``<tt>value</tt>`` as the 
        caption.

        >>> form = Form()
        >>> print form.submit('name', 'Submit >')
        <input type="submit" name="name" value="Submit &gt;" />
        """
        return handle_input(
            'submit',
            name, 
            value,
            attributes,
        )

    #
    # Single value fields which can submit no name or value but whose value
    # should not be allowed to change
    #
    
    def checkbox(self, name, value, attributes=None):
        """\
        Creates a check box.

        >>> form = Form()
        >>> print form.checkbox('name', 'James >')
        <input type="checkbox" name="name" value="James &gt;" />
        >>> form = Form(value={'name': 'Set at runtime'})
        >>> print form.checkbox('name', 'Set at design time')
        <input type="checkbox" name="name" value="Set at design time" />
        >>> form = Form(checked={'name': True})
        >>> print form.checkbox('name', 'J>')
        <input checked="checked" type="checkbox" name="name" value="J&gt;" />
        """
        return _checkable(self.checked, 'checkbox', name, value, attributes)

    def radio(self, name, value, attributes=None):
        """\
        Creates a radio button.

        >>> form = Form()
        >>> print form.radio('name', 'James >')
        <input type="radio" name="name" value="James &gt;" />
        >>> form = Form(value={'name': 'Set at runtime'})
        >>> print form.radio('name', 'Set at design time')
        <input type="radio" name="name" value="Set at design time" />
        >>> form = Form(checked={'name': True})
        >>> print form.radio('name', 'J>')
        <input checked="checked" type="radio" name="name" value="J&gt;" />
        """
        return _checkable(self.checked, 'radio', name, value, attributes)
   
    #
    # Single value fields with options
    #

    def dropdown(self, name, option=None, attributes=None, get_option_attributes=None):
        """\
        Create a single-valued <select> field
        
        >>> form = Form(
        ...     value={'fruit': u'1'}, 
        ...     option={
        ...         'fruit': [
        ...             ('1', 'Bananas'), 
        ...             ('2>', 'Apples <>'),
        ...             ('3', 'Pears'),
        ...         ]
        ...     }
        ... )
        >>> print form.dropdown('fruit')
        <select name="fruit">
        <option selected="selected" value="1">Bananas</option>
        <option value="2&gt;">Apples &lt;&gt;</option>
        <option value="3">Pears</option>
        </select>
        
        If not options for the select field are specified in the form
        constructor, no options will be rendered:
        
        >>> form = Form(
        ...     value={'fruit': u'1'}, 
        ...     option={}
        ... )
        >>> print form.dropdown('fruit')
        <select name="fruit">
        </select>
           
        Create a single-valued <select> field from nested data with shared options
           
        >>> form = Form(
        ...     value={'fruit[0].id': u'1', 'fruit[1].id': u'3'}, 
        ...     option={
        ...         'fruit[*].id': [
        ...             ('1', 'Bananas'), 
        ...             ('2>', 'Apples <>'),
        ...             ('3', 'Pears'),
        ...         ]
        ...     }
        ... )
        >>> print form.dropdown('fruit[0].id')
        <select name="fruit[0].id">
        <option selected="selected" value="1">Bananas</option>
        <option value="2&gt;">Apples &lt;&gt;</option>
        <option value="3">Pears</option>
        </select>
        >>> print form.dropdown('fruit[1].id')
        <select name="fruit[1].id">
        <option value="1">Bananas</option>
        <option value="2&gt;">Apples &lt;&gt;</option>
        <option selected="selected" value="3">Pears</option>
        </select>
        """
        value = self.value.get(name, u'')
        if '.' in name or '[' in name:
            parts = name.split('.')
            name_ = '.'.join(parts[:-1])
            sub_name = parts[-1]
            real_option = _get_option(self, option, name_, sub_name=sub_name)
        else:
            real_option = self.option.get(name, [])
        if not isinstance(value, (str, unicode)):
            raise Exception(
                'The value for a dropdown should be a unicode '
                'string, not %r'%(
                    type(value),
                )
            )
        return _select(self.value.get(name, []), real_option, False, name, attributes, get_option_attributes, self)
     
    def radio_group(self, name, option=None, align='horiz', cols=4, sub_name=None):
        """Radio Group Field.
    
        ``value``
            The value of the selected option, or ``None`` if no radio button
            is selected
    
        ``align``
            can be ``'horiz'`` (default), ``'vert'`` or ``table``. If table layout is 
            chosen then you can also use the ``cols`` argument to specify the number
            of columns in the table, the default is 4.
    
        Examples (deliberately including some '>' characters to check they are properly escaped)
  
        >>> form = Form(
        ...     value={'fruit': '1'}, 
        ...     option={
        ...         'fruit': [
        ...             ('1', 'Bananas'), 
        ...             ('2>', 'Apples <>'),
        ...             ('3', 'Pears'),
        ...         ]
        ...     }
        ... )
        >>> print form.radio_group('fruit')
        <input type="radio" name="fruit" value="1" checked="checked" /> Bananas
        <input type="radio" name="fruit" value="2&gt;" /> Apples &lt;&gt;
        <input type="radio" name="fruit" value="3" /> Pears
        >>> print form.radio_group('fruit', align='vert')
        <input type="radio" name="fruit" value="1" checked="checked" /> Bananas<br />
        <input type="radio" name="fruit" value="2&gt;" /> Apples &lt;&gt;<br />
        <input type="radio" name="fruit" value="3" /> Pears<br />
        >>> print form.radio_group('fruit', align='table', cols=2)
        <table border="0" width="100%" cellpadding="0" cellspacing="0">
            <tr>
              <td><input type="radio" name="fruit" value="1" checked="checked" /> Bananas</td>
              <td>&nbsp;&nbsp;&nbsp;&nbsp;</td>
              <td><input type="radio" name="fruit" value="2&gt;" /> Apples &lt;&gt;</td>
              <td>&nbsp;&nbsp;&nbsp;&nbsp;</td>
            </tr>
            <tr>
              <td><input type="radio" name="fruit" value="3" /> Pears</td>
              <td>&nbsp;&nbsp;&nbsp;&nbsp;</td>
              <td></td>
              <td>&nbsp;&nbsp;&nbsp;&nbsp;</td>
            </tr>
        </table>

        If no options are present in the form constructor, none will be
        rendered:

        >>> form = Form(
        ...     value={'fruit': '1'}, 
        ...     option={}
        ... )
        >>> form.radio_group('fruit')
        u''
        >>> form.radio_group('fruit', align='table')
        u''
         
        Here's an example with nested variables:
        
        >>> form = Form(
        ...     value={'fruit[0].id': '1'}, 
        ...     option={
        ...         'fruit[*].id': [
        ...             ('1', 'Bananas'), 
        ...             ('2>', 'Apples <>'),
        ...             ('3', 'Pears'),
        ...         ]
        ...     }
        ... )
        >>> print form.radio_group('fruit[0].id')
        <input type="radio" name="fruit[0].id" value="1" checked="checked" /> Bananas
        <input type="radio" name="fruit[1].id" value="2&gt;" /> Apples &lt;&gt;
        <input type="radio" name="fruit[2].id" value="3" /> Pears
        """
        if '.' in name or '[' in name:
            parts = name.split('.')
            name_ = '['.join('.'.join(parts[:-1]).split('[')[:-1])
            sub_name = parts[-1]
            real_option = _get_option(self, option, name_, sub_name=sub_name)
        else:
            name_ = name
            real_option = self.option.get(name, [])
        if self.value.get(name, []):
            selected_values = [self.value[name]]
        else:
            selected_values = []
        return group( 
            name_, 
            selected_values,
            real_option,
            'radio',
            align,
            cols,
            sub_name
        )

    #
    # Multi-valued fields
    #

    def combo(self, name, attributes=None, get_option_attributes=None):
        """\
        Create a multi-valued <select> field
   
        >>> form = Form(
        ...     value={'fruit': ['1', '3']}, 
        ...     option={
        ...         'fruit': [
        ...             ('1', 'Bananas'), 
        ...             ('2>', 'Apples <>'),
        ...             ('3', 'Pears'),
        ...         ]}
        ... )
        >>> print form.combo('fruit')
        <select multiple="multiple" name="fruit">
        <option selected="selected" value="1">Bananas</option>
        <option value="2&gt;">Apples &lt;&gt;</option>
        <option selected="selected" value="3">Pears</option>
        </select>

        If not options for the select field are specified in the form
        constructor, no options will be rendered:

        >>> form = Form(
        ...     value={'fruit': u'1'}, 
        ...     option={}
        ... )
        >>> print form.combo('fruit')
        <select multiple="multiple" name="fruit">
        </select>
        """
        return _select(self.value.get(name, []), self.option.get(name, []), True, name, attributes, get_option_attributes, self)
        
    def checkbox_group(self, name, option=None, align='horiz', cols=4, sub_name=None):
        """Check Box Group Field.
    
        ``align``
            can be ``'horiz'`` (default), ``'vert'`` or ``table``. If table layout is 
            chosen then you can also use the ``cols`` argument to specify the number
            of columns in the table, the default is 4.
    
        Examples (deliberately including some '>' characters to check they are properly escaped)
   
        >>> form = Form(
        ...     value={'fruit': ['1', '3']}, 
        ...     option={
        ...         'fruit': [
        ...             ('1', 'Bananas'), 
        ...             ('2>', 'Apples <>'),
        ...             ('3', 'Pears'),
        ...         ]
        ...     }
        ... )
        >>> print form.checkbox_group('fruit')
        <input type="checkbox" name="fruit" value="1" checked="checked" /> Bananas
        <input type="checkbox" name="fruit" value="2&gt;" /> Apples &lt;&gt;
        <input type="checkbox" name="fruit" value="3" checked="checked" /> Pears
        >>> print form.checkbox_group('fruit', align='vert')
        <input type="checkbox" name="fruit" value="1" checked="checked" /> Bananas<br />
        <input type="checkbox" name="fruit" value="2&gt;" /> Apples &lt;&gt;<br />
        <input type="checkbox" name="fruit" value="3" checked="checked" /> Pears<br />
        >>> print form.checkbox_group('fruit', align='table', cols=2)
        <table border="0" width="100%" cellpadding="0" cellspacing="0">
            <tr>
              <td><input type="checkbox" name="fruit" value="1" checked="checked" /> Bananas</td>
              <td>&nbsp;&nbsp;&nbsp;&nbsp;</td>
              <td><input type="checkbox" name="fruit" value="2&gt;" /> Apples &lt;&gt;</td>
              <td>&nbsp;&nbsp;&nbsp;&nbsp;</td>
            </tr>
            <tr>
              <td><input type="checkbox" name="fruit" value="3" checked="checked" /> Pears</td>
              <td>&nbsp;&nbsp;&nbsp;&nbsp;</td>
              <td></td>
              <td>&nbsp;&nbsp;&nbsp;&nbsp;</td>
            </tr>
        </table>

        If no options are present in the form constructor, none will be
        rendered:

        >>> form = Form(
        ...     value={'fruit': '1'}, 
        ...     option={}
        ... )
        >>> form.checkbox_group('fruit')
        u''
        >>> form.checkbox_group('fruit', align='table')
        u''

        You can also have sub_name options

        >>> form = Form(
        ...     value={
        ...         'fruit[0].id': '1',
        ...         'fruit[1].id': '3',
        ...     }, 
        ...     option={
        ...         'fruit[0].id': [
        ...             ('1', 'Bananas'), 
        ...             ('2>', 'Apples <>'),
        ...             ('3', 'Pears'),
        ...         ]
        ...     }
        ... )
        >>> print form.checkbox_group('fruit', sub_name='id')
        <input type="checkbox" name="fruit[0].id" value="1" checked="checked" /> Bananas
        <input type="checkbox" name="fruit[1].id" value="2&gt;" /> Apples &lt;&gt;
        <input type="checkbox" name="fruit[2].id" value="3" checked="checked" /> Pears
        >>> form = Form(
        ...     value={
        ...         'person[0].fruit[0].id': '1',
        ...         'person[0].fruit[1].id': '3',
        ...     }, 
        ...     option={
        ...         'person[*].fruit[*].id': [
        ...             ('1', 'Bananas'), 
        ...             ('2>', 'Apples <>'),
        ...             ('3', 'Pears'),
        ...         ]
        ...     }
        ... )
        >>> print form.checkbox_group('person[0].fruit', sub_name='id')
        <input type="checkbox" name="person[0].fruit[0].id" value="1" checked="checked" /> Bananas
        <input type="checkbox" name="person[0].fruit[1].id" value="2&gt;" /> Apples &lt;&gt;
        <input type="checkbox" name="person[0].fruit[2].id" value="3" checked="checked" /> Pears
        """
        if name.endswith(']') and sub_name:
            raise Exception('The name should not end with %r when using sub_name'%name[name.rfind('['):])
        # Format the selected values into the correct flattened structure
        if sub_name:
            selected_values = []
            for k, v in self.value.items():
                if k.startswith(name+'[') and k.endswith('].'+sub_name):
                    selected_values.append(v)
        else:
            selected_values = self.value.get(name)

        return group( 
            name, 
            selected_values, 
            _get_option(self, option, name, sub_name),
            'checkbox',
            align,
            cols,
            sub_name
        )

def _get_option(form, option, name, sub_name=None):
    if option is None:
        if not sub_name:
            real_options = form.option.get(name, [])
        else:
            # First see if there is an exact match for this key
            real_options = None
            for option in form.option:
                if option == name+'.'+sub_name:
                    real_options = form.option[option]
            # Otherwise treat all the keys as regexes and merge the options
            # of any matching keys
            found = []
            if real_options is None:
                for option in form.option:
                    key = name+'.'+sub_name
                    match = re.match(option.replace('[', '\[').replace(']', '\]'), key)
                    if match is None:
                        if found:
                            raise Exception('The option keys %r and %r both match this checkbox group %r'%(found[0], option, key))
                        else:
                            found.append(option)
            if found:
                real_options = form.option[found[0]]
    else:
        real_options = option
    return real_options
