# Todo: Make this switch between Django, Pylons, etc.
from dm.exceptions import WebkitError
from dm.dictionarywords import WEBKIT_NAME
from dm.ioc import RequiredFeature

dictionary = RequiredFeature('SystemDictionary')
webkitName = dictionary[WEBKIT_NAME]
webkitVersion = ''  # Inferred version.
webkitVersionFull = ''  # Actual, if available.
if not webkitName:
    pass
elif webkitName == 'django':
    import django
    import django.forms
    if hasattr(django.forms, 'BaseForm'): # Django 1.0
        webkitVersion = '1.0'  # ...and up. (Todo: Revisit version detection).
        webkitVersionFull = django.get_version()
        from django.forms.forms import BaseForm
        from django.forms.util import ValidationError
        from django.utils.html import escape as htmlescape
        from django.http import HttpRequest
        from django.http import HttpResponse
        from django.http import HttpResponseRedirect
        from django.template import Context
        if webkitVersionFull[1] >= 2:
            from django.template import RequestContext
        else:
            RequestContext = None
        from django.core import template_loader
        from django.forms import Field
        from django.forms import CharField
        from django.forms import BooleanField
        from django.forms import EmailField
        from django.forms import ChoiceField
        from django.forms import MultipleChoiceField
        from django.forms import DateTimeField
        from django.forms import TimeField
        from django.forms import DateField
        from django.forms import IntegerField
        from django.forms import ImageField
        from django.forms import URLField
        from django.forms import widgets
        from django.forms import fields
        from django.utils.datastructures import SortedDict
    else:                             # Django 0.96
        webkitVersion = '0.96'
        webkitVersionFull = ".".join([str(i) for i in django.VERSION[0:2]])
        from django.utils.html import escape as htmlescape
        from django.forms import validators
        from django.forms import Manipulator
        from django.forms import SelectField, SelectMultipleField, TextField
        from django.forms import TextField, LargeTextField
        from django.forms import PasswordField, IntegerField, SmallIntegerField
        from django.forms import PositiveIntegerField, URLField, CheckboxField
        from django.forms import DatetimeField, DateField, TimeField
        from django.forms import FileUploadField, EmailField, RadioSelectField
        from django.core.validators import ValidationError
        from django.template import Context
        from django.core import template_loader
        from django.http import HttpRequest
        from django.http import HttpResponse
        from django.http import HttpResponseRedirect

elif webkitName == 'pylons':
    import pylons
    from webhelpers import *
    from cgi import escape as htmlescape
    class Manipulator(object): pass
    SelectField = select
    SelectMultipleField = None
    TextField = text_field
    LargeTextField = text_area
    PasswordField = text_field
    IntegerField = text_field
    class URLField(object): pass
    class CheckboxField(object): pass
    class DatetimeField(object): pass
    class DateField(object): pass
    class FileUploadField(object): pass
    EmailField = text_field
    class ValidationError(object): pass
    class HttpRequest(object): pass
    class HttpResponse(object): pass
    class HttpResponseRedirect(object): pass
    class Context(object): pass
    class template_loader(object): pass

else:
    raise WebkitError, "No support available for '%s' webkit." % webkitName




if webkitName == 'django' and webkitVersion == '1.0':

    DATE_INPUT_FORMATS = (
        '%Y-%m-%d', '%d-%m-%Y', '%d-%m-%y', # '2006-10-25', '25-10-2006', '25-10-06'
        '%Y/%m/%d', '%d/%m/%Y', '%d/%m/%y', # '2006/10/25', '25/10/2006', '25/10/06'
        '%b %d %Y', '%b %d, %Y',            # 'Oct 25 2006', 'Oct 25, 2006'
        '%d %b %Y', '%d %b, %Y',            # '25 Oct 2006', '25 Oct, 2006'
        '%B %d %Y', '%B %d, %Y',            # 'October 25 2006', 'October 25, 2006'
        '%d %B %Y', '%d %B, %Y',            # '25 October 2006', '25 October, 2006'
    )

    class Manipulator(BaseForm):

        pass


    class ManipulatedField(Field):

        def __init__(self, manipulator=None, *args, **kwds):
            self.manipulator = manipulator
            super(ManipulatedField, self).__init__(*args, **kwds)


    class DateField(DateField):
        
        def __init__(self, input_formats=None, *args, **kwargs):
            input_formats = input_formats or DATE_INPUT_FORMATS
            super(DateField, self).__init__(input_formats=input_formats, *args, **kwargs)



elif webkitName == 'django' and webkitVersion == '0.96':

    import re
    _rdatere = r'((?:0?[1-9])|(?:[12][0-9])|(?:3[0-1]))-((?:0?[1-9])|(?:1[0-2]))-(19|2\d)\d{2}'
    ransi_date_re = re.compile('^%s$' % _rdatere)

    class RDateField(DateField):
        """Automatically converts its data to a datetime.date object.
        The data should be in the format DD-MM-YYYY"""
    
        def isValidDate(self, field_data, all_data):
            try:
                if not ransi_date_re.search(field_data):
                    raise ValidationError(
                        'Enter a valid date in DD-MM-YYYY format.'
                    )
            except ValidationError, e:
                raise validators.CriticalValidationError, e.messages
    
        def html2python(data):
            "Converts the field into a datetime.date object"
            import time, datetime
            try:
                t = time.strptime(data, '%d-%m-%Y')
                return datetime.date(t[0], t[1], t[2])
            except (ValueError, TypeError):
                return None
                
        html2python = staticmethod(html2python)

