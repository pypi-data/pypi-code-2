from collections import defaultdict, Callable

import field
from field import StopValidation

def _add_error(errors, x):
    if isinstance(x, tuple):
        errors.extend(x)
    elif x is not None:
        errors.append(x)

class FieldAttribute(object):
    def __init__(self, form, name):
        self.form = form
        self.name = name
        self.field = self.form.fields[name]

        self.reset()

    def id(self):
        return self.field.id or self.name

    def label(self):
        return self.field.label or self.name.replace('_', ' ').title()

    def reset(self, initial=u''):
        self.value = self.field.default
        self.data = initial
        self.errors = list()

    def validate(self, value):
        self.value = None
        self.data = value

        if value or self.field.default is None:
            for cls in reversed(self.field.__class__.__mro__):
                # Stop if there was an error
                if getattr(cls, 'stop_on_error', False) and self.errors:
                    break

                if 'validate' in cls.__dict__:
                    try:
                        _add_error(self.errors, cls.validate(self.field, value))
                    except StopValidation as e:
                        self.errors.extend(e.args)
                        break

            if self.errors:
                return False
            else:
                self.value = self.field.convert(value)
        else:
            self.value = self.field.default

        return True


class Form(object):
    '''
    The base class of all forms. To create a new form, simply derive it from
    :class:`Form`::

        class MyForm(Form):
            my_string = String()

    You can initialize the values in the form by passing a mapping or using
    keyword arguments. Both ways are equivalent::

        my_form = MyForm({'my_string': 'some text'})
        my_form = MyForm(my_string='some text'})

    Then call :meth:`Form.validate` to validate the data::

        if my_form.validate({'my_string': 'What I write'}):
            print 'Valid'
        else:
            print 'Invalid'
    '''
    def _setup_class(self):
        self.fields = dict()
        self.validators = defaultdict(list)
        self.context_validators = list()

        for cls in reversed(self.__class__.__mro__):
            for key, value in cls.__dict__.iteritems():
                if isinstance(value, field.Field):
                    # We store all the fiels in self.fields. We're going to
                    # override them with FieldAttributes later on.
                    self.fields[key] = value

                elif (key.startswith('validate_') and
                      isinstance(value, Callable)):
                    self.validators[key[len('validate_'):]].append(value)

                elif key == 'context_validate':
                    self.context_validators.append(value)

    def __init__(self, *args, **kwargs):
        self._setup_class()

        self.attributes = dict()
        for name in self.fields:
            fa = FieldAttribute(self, name)
            self.attributes[name] = fa
            setattr(self, name, fa)

        self.initial = dict()
        for x in args:
            self.initial.update(x)
        self.initial.update(kwargs)

        self.reset()

    def reset(self):
        '''Set the fields' values back to their initial values. This allows you
        to reuse forms::

            >>> class MyForm(Form):
            ...     my_string = field.String()
            >>> my_form = MyForm(my_string='initial')
            >>> my_form.my_string.data
            'initial'

            >>> my_form.validate({'my_string': 'something'})
            True
            >>> my_form.my_string.data
            'something'
            >>> my_form.reset()
            >>> my_form.my_string.data
            'initial'
        '''
        self.errors = defaultdict(list)
        for name, attribute in self.attributes.iteritems():
            attribute.reset(self.initial.get(name, u''))
            self.errors[name] = attribute.errors

    def valid(self):
        '''Return `True` if the form is valid. A form is valid if there was no
        errors during the previous validation. This means that when a form is
        created it is automatically considered valid::

            >>> class MyForm(Form):
            ...    x = field.String(required=True)
            >>> my = MyForm()
            >>> my.valid()
            True
            >>> my.validate({})
            False
            >>> my.valid()
            False
        '''
        return all(not x for x in self.errors.itervalues())

    def __repr__(self):
        x = ', '.join('{0}={1!r}'.format(k, v.value)
                      for k, v in self.attributes.iteritems())
        return '<{0}({1})>'.format(self.__class__.__name__, x)

    def validate(self, data):
        '''
        ``data`` must be a dictionnary-like object. Return `True` if the form
        is valid.
        '''
        self.reset()

        for name, attr in self.attributes.iteritems():
            value = data.get(name, unicode())
            if attr.validate(value):
                for validator in self.validators[name]:
                    try:
                        _add_error(self.errors[name],
                                   validator(self, attr.value))
                    except StopValidation as e:
                        self.errors[name].extend(e.args)
                        break

        if self.valid():
            for cv in self.context_validators:
                try:
                    cv(self)
                except StopValidation:
                    break
            return self.valid()
        else:
            return False

