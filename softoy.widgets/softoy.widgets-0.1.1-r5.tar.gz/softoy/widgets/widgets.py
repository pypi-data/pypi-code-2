# -*- coding: utf-8 -*-
from softoy.htmltags.htmltags import Tag as T
import datetime
import formencode
from formencode import Invalid
from formencode.schema import SimpleFormValidator
from formencode.validators import FancyValidator as Fancy

def gether_required(e, **kw):
    if hasattr(e, 'required'):
        return e.required
    
def gether_script_code(e, **kw):
    if hasattr(e, 'script_code'):
        return e.script_code()
    
def istrue(e, **kw):
    if e:
        return True
        

class TravelBag(object):
    def __init__(self, asset=set([]), scripts=[]):
        self.asset = asset
        self.scripts = scripts
        
    def add_required(self, required):
        self.asset = self.asset.union(set(required))
        
    def add_script_code(self, script_code):
        self.scripts.append(script_code)
        
    def concrete(self):
        head_tags = []
        for elem in list(self.asset):
            if elem.split('.')[-1] == 'js':
                head_tags.append(T('script', attrs={'type':'text/javascript', 'src':elem}))
            elif elem.split('.')[-1] == 'css':
                head_tags.append(
                    T('link', attrs={'rel':'stylesheet', 'type':'text/css', 'href':elem})
                    )
        for code in self.scripts:
            head_tags.append(T('script', attrs={'type':'text/javascript'}, data=code))
        return head_tags
        
    def __repr__(self):
        return 'asset %s\nscripts %s' % (self.asset, self.scripts)
            


def display(format, objs):
    if objs is not None:
        return format % objs
    else:
        return ''

def dict_required(d, k, v):
    if k not in d:
        d[k] = v

class Widget(T): # TODO - bool_attr
    def __init__(self, tag, **kw):
        super(Widget, self).__init__(tag, **kw)
        self.travel_bag = TravelBag()
        #print 'class name of widget: %s' % self.__class__.__name__
        if hasattr(self, 'outsource') and self.outsource:
            #print 'class name of outsource: %s' % self.__class__.__name__
            self.fill_bag()

    def extend(self):
        return [self]

    def fill_bag(self):
        self.travel_bag = TravelBag()
        # asset
        L = self.visit2(applyer=gether_required)
        L = [x for x in L if x is not None]
        print 'L', L
        for x in L:
            self.travel_bag.add_required(x)
        # scripts
        L2 = self.visit2(applyer=gether_script_code, L=[])
        L2 = [x for x in L2 if x is not None]
        print 'L2', L2
        for x in L2:
            self.travel_bag.add_script_code(x)

    def set_head_tags(self, head):
        for t in self.travel_bag.concrete():
            head.append(t)

    # boolean attributes
    def battr_is_on(self, attr_name):
        return attr_name in self.attrs and self.attrs[attr_name]
            
    def battr_turn_on(self, attr_name):
        self.attrs[attr_name] = True
        
    def battr_turn_off(self, attr_name):
        if attr_name in self.attrs:
            del self.attrs[attr_name]
        

class A(Widget):
    def __init__(self, **kw):
        super(A, self).__init__('a', **kw)
        self.attrs['href'] = kw.get('url', '')

class Body(Widget):
    def __init__(self, **kw):
        super(Body, self).__init__('body', **kw)

class Br(Widget):
    def __init__(self, **kw):
        super(Br, self).__init__('br', **kw)

class Div(Widget):
    def __init__(self, **kw):
        super(Div, self).__init__('div', **kw)

class Head(Widget):
    def __init__(self, **kw):
        super(Head, self).__init__('head', **kw)

class Html(Widget):
    def __init__(self, **kw):
        super(Html, self).__init__('html', **kw)

class Li(Widget):
    def __init__(self, **kw):
        super(Li, self).__init__('li', **kw)
        if 'dojoType' in kw:
            self.attrs['dojoType'] = kw['dojoType']

class JavaScript(Widget):
    def __init__(self, **kw):
        super(JavaScript, self).__init__('script', **kw)
        self.attrs['type'] = 'text/javascript'
        url = kw.get('url', '')
        code = kw.get('code')
        if 'defer' in kw and kw['defer']:
            self.battr_turn_on('defer')
        if code:  # code first
            self.data = code
        elif url:
            self.attrs['scr'] = url


class Option(Widget):  # has valu attribute
    def __init__(self, **kw):
        super(Option, self).__init__('option', **kw)
        self.attrs['value'] = kw.get('value')
        if self.attrs['value']:
            self.data = self.attrs['value']
        
    def set_value(self, v):
        self.attrs['value'] = v
        self.data = v

    def get_value(self):
        return self.attrs['value']


class P(Widget):
    def __init__(self, **kw):
        super(P, self).__init__('p', **kw)


class Stylesheet(Widget):
    def __init__(self, **kw):
        super(Stylesheet, self).__init__('link', **kw)
        self.attrs['rel'] = 'stylesheet'
        self.attrs['type'] = 'text/css'
        url = kw.get('url')
        if url:
            self.attrs['href'] = url

class Ul(Widget):
    def __init__(self, **kw):
        super(Ul, self).__init__('ul', **kw)


class Field(Widget):
    def __init__(self, tag, **kw):
        super(Field, self).__init__(tag, **kw)
        self.validator = kw.get('validator', Fancy())
        self.label = kw.get('label')
        self.error = kw.get('error')
        self.colon = kw.get('colon', True)
        self.disabled=kw.get('disabled', False)
        self.default = kw.get('default')
        self.required = kw.get('required', False)
        self.unique = kw.get('unique', False)
        if self.name:
            self.attrs['name'] = self.name
        self.attrs['value'] = kw.get('value')
        self.exclude_label = kw.get('exclude_label', False)

    def clear(self):
        self.error = None
        self.attrs['value'] = None

    def bind_value(self, v):
        self.attrs['value'] = v

    def set_value(self, v):
        self.attrs['value'] = v

    def get_value(self):
        return self.attrs['value']

    def fill(self, formdict, errors={}):
        self.attrs['value'] = formdict.get(self.name)
        self.error = errors.get(self.name)

    def filled(self):
        return self.attrs['value']

    def validatable(self, o):
        if isinstance(o, Field) and hasattr(o, 'validator'):
            validator = getattr(o, 'validator')
            if validator:
                return validator

    def labeling(self, **kw):
        if self.label:
            e = T('label',**kw)
            e.data = self.label
            if self.colon:
                e.data += ':'
            return e
            
    def required_mark(self):
            e = T('span')
            if hasattr(self, 'required') and self.required:
                e.data = '*'
                e.style['class'] = 'required'
            else:
                e.data = ' '
            return e

    def error_format(self, s):
        return '* %s' % s

    def display_error(self, **kw):
        if self.error:
            e = T('span', **kw)
            e.data = self.error_format(self.error)
            return e

    def extend(self):
        return [self.required_mark(), self.labeling(), self,
            self.display_error(class_='error')]


class Input(Field):
    def __init__(self, **kw):
        super(Input, self).__init__('input', **kw)
        self.attrs['size'] = kw.get('size', '')
        """
        <input> size Attribute: integer,
        For <input type="text"> and <input type="password">,
            the size attribute defines the number of characters that
            should be visible.
        For all other input types, size defines the width of the input field
            in pixels.
        """


class Button(Input):
    def __init__(self, **kw):
        super(Button, self).__init__(**kw)
        self.attrs['type'] = 'button'

class Checkbox(Input):
    def __init__(self, **kw):
        super(Checkbox, self).__init__(**kw)
        self.attrs['type'] = 'checkbox'
        value = kw.get('value')
        if value is True:
            self.set_value(True)
        else:
            self.set_value(False)
            
    def set_value(self, v):
        if v is True:
            self.battr_turn_on('checked')
            
    def get_value(self):
        if self.battr_is_on('checked'):
            return True
        else:
            return False
            

class File(Input):
    def __init__(self, **kw):
        super(File, self).__init__(**kw)
        self.attrs['type'] = 'file'
        self.attrs['accept'] = kw.get('accept')

class Hidden(Input):
    def __init__(self, **kw):
        super(Hidden, self).__init__(**kw)
        self.attrs['type'] = 'hidden'

class Image(Input):
    def __init__(self, **kw):
        super(Image, self).__init__(**kw)
        self.attrs['type'] = 'image'
        self.attrs['src'] = kw.get('src')
        self.attrs['alt'] = kw.get('alt')

class Password(Input):
    def __init__(self, **kw):
        super(Password, self).__init__(**kw)
        self.attrs['type'] = 'password'
        self.attrs['maxlength'] = kw.get('maxlength')

class Radio(Input):
    def __init__(self, **kw):
        super(Radio, self).__init__(**kw)
        self.attrs['type'] = 'radio'
        self.checked=kw.get('checked', False)

class InputButton(Input):
    def __init__(self, **kw):
        super(InputButton, self).__init__(**kw)

class Reset(InputButton):
    def __init__(self, **kw):
        super(Reset, self).__init__(**kw)
        self.attrs['type'] = 'reset'

class Select(Field):
    def __init__(self, **kw):
        super(Select, self).__init__('select', **kw)
        options = kw.get('options', [])  # simple a value list
        self.update_options(options)

    def update_options(self, options):
        for opt in options:
            self.append(Option(value=opt, data=opt))
            
    def set_value(self, v):
        for e in self.subs:
            if e.get_value() == v:
                e.battr_turn_on('selected')
            else:
                e.battr_turn_off('selected')
                
    def get_value(self):
        for e in self.subs:
            if e.attrs['selected']:
                return e.get_value()

    def fill(self, formdict, errors={}):
        self.bind_value(formdict.get(self.name))
        self.error = errors.get(self.name)

    def filled(self):
        for e in self.subs:
            if hasattr(e.attrs, 'selected') and e.attrs['selected']:
                return e.attrs['value']


class SimpleSelect(Field):
    def __init__(self, **kw):
        super(SimpleSelect, self).__init__('select', **kw)
        self.options = kw.get('options')
        self.set_options()

    def set_options(self):
        for option in self.options:
            so = str(option)
            self.append(T('option', attrs={'value':so}, data=so))

    def bind_value(self, v):
        if v is not None:
            sel_opt = None
            for e in self.subs:
                if e.attrs['value'] == v:
                    e.attrs['selected'] = selected
                    sel_opt = e
                else:
                    if hasattr(e.attrs, 'selected'):
                        del e.attrs['selected']

    def fill(self, formdict, errors={}):
        self.bind_value(formdict.get(self.name))
        self.error = errors.get(self.name)

    def filled(self):
        for e in self.subs:
            if hasattr(e.attrs, 'selected') and e.attrs['selected']:
                return e.attrs['value']

    def extend(self):
        return super(SimpleSelect, self).extend()


# from list of pailist i.e. key-value tuple
def options_by_list(lst, key=None):  # key is the selected item's key
    if isinstance(lst[0], tuple) and len(lst[0]) == 2:
        option_list = lst
    else:
        option_list = zip(lst, lst)
    options = []
    for k, v in option_list:
        option = T('option', attrs={'value':k}, data=v)
        if key and k == key:
            option.attrs['selected'] = 'selected'
        options.append(option)
    return options


class Submit(InputButton):
    def __init__(self, **kw):
        dict_required(kw, 'name', 'b_submit')
        dict_required(kw, 'value', u'보내기')
        super(Submit, self).__init__(**kw)
        self.attrs['type'] = 'submit'


class Text(Input):
    def __init__(self, **kw):
        super(Text, self).__init__(**kw)
        self.attrs['type'] = 'text'
        self.attrs['maxlength'] = kw.get('maxlength')


class Textarea(Field):
    def __init__(self, **kw):
        super(Textarea, self).__init__('textarea', **kw)
        self.cols = kw.get('cols', '20')
        self.rows = kw.get('rows', 3)
        self.attrs['cols'] = self.cols
        self.attrs['rows'] = self.rows

    def bind_value(self, v):
        self.data = v

    def fill(self, formdict, errors={}):
        self.data = formdict.get(self.name)
        self.error = errors.get(self.name)

    def filled(self):
        return self.data



# Complex Widgets
    

class DatePicker(Field):
    def __init__(self, **kw):
        super(DatePicker, self).__init__('input', **kw)
        self.attrs['type'] = 'text'
        self.outsource = True

        self.required = [
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.8/themes/base/jquery-ui.css',
            'http://ajax.googleapis.com/ajax/libs/jquery/1.4/jquery.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.8/jquery-ui.min.js',
            #'static/js/ui/jquery.ui.core.js'
            #static/js/jquery.ui.datepicker.js'
            ]

    def script_code(self):
        return '''
            $(document).ready(function() {
                $("#%s").datepicker();
            });                
        ''' % (self.attrs['id'])



class Form(Field):
    def __init__(self, **kw):
        super(Form, self).__init__('form', **kw)
        self.attrs['method'] = kw.get('method', 'post')
        self.attrs['action'] = kw.get('action', '')

    def fill(self, formdict, errors={}):  # nested
        if formdict:
            for e in self.subs:
                if isinstance(e, Field) and not self.subs:
                    e.value = formdict.get(e.name)
                    e.error = errors.get(e.name)
                else:
                    if hasattr(e, 'fill'):
                        e.fill(formdict, errors=errors)

    def filled(self, formdict={}):  # nested
        for e in self.subs:
            if isinstance(e, Field) and not self.subs:
                formdict[e.name] = e.filled()
            else:
                fd = e.filled()
                formdict[e.name] = fd
        return formdict

    def validate(self, formdict):
        values = {}
        errors = {}
        for e in self.subs:
            if self.validatable(e):
                try:
                    value = e.validator.to_python(formdict.get(e.name), None)
                    values[e.name] = value
                except Invalid, error:
                    error_msg = error.unpack_errors()
                    errors[e.name] = error_msg
        return (values, errors)

    def refill(self, o):
        for e in self.subs:
            if e.name and hasattr(o, e.name):
                v = getattr(o, e.name)
                if self.validatable(e):
                    v = e.validator.from_python(v)
                e.attrs['value'] = v
        return self

    def listform(self, margin='5px'):
        self.style['text-align'] = 'left'
        for i in range(len(self.subs)):
            e = self.subs.pop(i)
            div = T('div')[e]
            self.subs.insert(i, div)
        return self

    def delete_buttons(self):
        indexes = [i for i in range(len(self.subs)) if isinstance(self.subs[i], InputButton)]
        indexes.reverse()
        for i in indexes:
            self.subs.pop(i)
        return self

    def show(self, o):
        self.refill(o)
        div = T('div')
        for e in self.subs:
            if isinstance(e, Field) and not isinstance(e, (InputButton, Hidden)):
                label = e.label
                if e.colon:
                    label += ':'
                div.append(T('span', data=label))
                div.append(T('span', data=e.attrs['value']))
                div.append(T('br'))
        return div

    def clear(self):
        for e in self.subs:
            if isinstance(e, Field):
                e.clear()


def radio_fieldset(name, label_value_pairs, legend=None, style={}):
    fieldset = T('fieldset')
    if legend:
        fieldset[T('legend', data=legend, style=style),]
    for item in label_value_pairs:
        if isinstance(item, T):  # label_value_pairs can have html_block tag
            fieldset.append(item)
        else:
            label = item[0]
            value = item[1]
            fieldset.append(T('label', data=label))
            fieldset.append(T('input', attrs=dict(type='radio', name=name, value=value)))
            fieldset.append(T('br'))
    return fieldset

def label_input_row(label_text, *args):
    td2 = T('td', children=args)
    row = T('tr')[
        T('td')[
            T('label', data=label_text, style={'font-weight':'bold'}),
            ],
            td2
        ]
    return row


class TableForm(Form):
    def __init__(self, **kw):
        self.values = kw.get('values', {})
        self.errors = kw.get('errors', {})
        self.buttons = kw.get('buttons')
        self.buttons_bar = None
        super(TableForm, self).__init__(**kw)
        self.schema = kw.get('schema')
        if self.schema:
            fmap = self.schema().fields_map()
            self.build(fmap)

    def build(self, children):
        rows = []
        for e in children.values():
            e.bind_value(self.values.get(e.name, ''))
            e.error = self.errors.get(e.name)
            tr = T('tr', id ='%s_tr' % e.name)[
                T('td')[
                    T('label', data=display('%s:', e.label))
                ],
                T('td')[e],
                T('td', data=display('* %s', e.error), class_='error')
                ]
            rows.append(tr)
        if self.buttons:
            self.buttons_bar = ToolBar(tooltips=self.buttons)
        else:
            self.buttons_bar = ToolBar(tooltips=[Submit()])
        rows.append(self.buttons_bar)
        table = T('table', children=rows)
        self[table]

    def validate(self, params):
        availables = [
            e for e in self.schema().fields_map().values() if hasattr(e, 'validator')]
        values = {}
        errors = {}
        for e in availables:
            try:
                value = e.validator.to_python(params.get(e.name), None)
                values[e.name] = value
            except Invalid, error:
                error_msg = error.unpack_errors()
                errors[e.name] = error_msg
        return (values, errors)

    def fill(self, values, what='value'):  # "what" is value or "error"
        for s in self.children:
            if s.name in values:
                if what == 'value':
                    s.attrs[what] = values[s.name]
                else:  # "error"
                    L = self.selector(id='%s_tr' % s.name)
                    for e in L:
                        idx = e.my_index()
                        if idx:
                            e.sup.insert(idx + 1,
                                T('tr', class_='error_row')[T('td'),
                                    T('td', data=values[s.name], class_='error')
                                    ]
                                )

    def del_error_messages(self):
        L = self.selector(class_='error_row')
        deleter = lambda x: x.apart()
        map(deleter, L)



