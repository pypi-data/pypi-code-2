from inspect import isclass

from tw.forms import validators
from tw.forms import CheckBox, InputField
from tw.api import Widget, Link, lazystring as _, js_function, CSSLink
from tw import forms
from tw.api import CSSLink, JSLink
from rum import app, i18n

from tw.rum.grid import RumDataGrid
from tw.rum import util
from tw.dojo import dojo_js
from rum.fields import rum_getattr
from genshi import HTML, ParseError

__all__ = [
"Span",
#"ShortenedSpan",
"SingleSelectField",
"ExpandableSpan",
'RelationLink',
"PreformattedRelationLink",
"PreformattedCollectionLinks",
"BaseShowWidget",
"mangle_form",
"is_mangled",
"RumDataGrid",
"RumCalendarDateTimePicker",
"RumCalendarDatePicker",
"RumCalendarTimePicker"
]

modname = "tw.rum"

form_css = CSSLink(modname=modname, filename='static/form.css')

single_select_preview_js = JSLink(
    modname=modname,
    filename='static/single_select_preview.js',
    javascript=[dojo_js]
    )

class SingleSelectField(forms.SingleSelectField):
    template="genshi:tw.rum.templates.single_select"
    params=["resource"]
    javascript=[single_select_preview_js]
    def update_params(self, d):
        super(SingleSelectField, self).update_params(d)
        d.preview_base=app.url_for(resource=self.resource, _memory=False)
#
# IMPORTANT! Always pass _memory=False toi url_for when generating links
# inside an inline widget or else the current routing args will
# contaminate
#
class FieldWidget(Widget):
    params = ['field_name']
    def update_params(self, d):
        super(FieldWidget, self).update_params(d)
        d.row = d.value
        d.value = rum_getattr(d.value, d.field_name)
class Span(FieldWidget):
    params = ['escape','formatter']
    escape = True
    template = "genshi:tw.rum.templates.span"
    formatter = unicode
    
    def update_params(self, d):
        super(Span, self).update_params(d)
        d.unicode_value=d.formatter(d.value)
        
class Url(FieldWidget):
    template = "genshi:tw.rum.templates.link"

class Pre(Span):
    template = "genshi:tw.rum.templates.pre"
    css = [CSSLink(modname=modname,
    filename='static/pre.css'
    )]
class BinaryLink(Widget):
    params = ['field']
    template = "genshi:tw.rum.templates.binary_link"

    def update_params(self, d):
        super(BinaryLink, self).update_params(d)
        d.url=app.url_for(parent_obj=d.value,
            remote_name=d.field.name,_memory=False)


class ImagePreview(Widget):
    params = ['field']
    template = "genshi:tw.rum.templates.image_preview"

    def update_params(self, d):
        super(ImagePreview, self).update_params(d)
        d.real_url=app.url_for(parent_obj=d.value,
            remote_name=d.field.name,_memory=False)
        d.preview_url=app.url_for(parent_obj=d.value,
            remote_name=d.field.name,_memory=False,action="preview")


expandable_span_js = JSLink(
    modname=modname,
    filename='static/expandable_span.js',
    javascript=[dojo_js]
    )

expandable_span_css = CSSLink(
    modname=modname,
    filename='static/expandable_span.css'
    )

edit_passwd_js = JSLink(
    modname=modname,
    filename='static/editpassword.js',
    javascript=[dojo_js]
    )

def parse_and_summarize_value(value, max_inline_chars):
    try:
        return util.summarize_stream(HTML(value), max_inline_chars)
    except ParseError:
        return _("parse error")
class ExpandableSpan(Span):
    template="genshi:tw.rum.templates.expandable_span"
    params = ['max_inline_chars']
    max_inline_chars = 25
    javascript = [expandable_span_js]
    css = [expandable_span_css]

    def update_params(self, d):
        super(ExpandableSpan, self).update_params(d)
        d.expand, d.summary = None, d.unicode_value
        d.summarize_stream = util.summarize_stream
        d.parse_and_summarize_value=parse_and_summarize_value
        if d.value and self.escape:        
            try:
                d.summary, rest= util.cut_text(d.unicode_value,
                                                    d.max_inline_chars)
                if rest:
                    d.expand=d.unicode_value
            except TypeError:
                pass



class CollectionLinks(Widget):
    params = ['field', 'icons', 'actions', 'show_items', 'formatter']
    
    formatter=unicode
    actions = [
        ('index', _('Show all')),
        ('new', _('New')),
        ]
    show_items=False
    template = "genshi:tw.rum.templates.collection_links"
    icons = {
        'show': Link(modname=modname, filename="static/pencil_go.png"),
        }

    def update_params(self, d):
        super(CollectionLinks, self).update_params(d)
        actions=self.actions
        if d.field.read_only:
            actions=[(link, label) for (link, label) in actions if link!="new"]
        def url_for_item(i):
            return app.url_for(obj=i, _memory=False)
        d.url_for_item=url_for_item
        if d.show_items:
            actions=[(a,desc) for (a,desc) in actions if a!="index"]
            d.items=rum_getattr(d.value, d.field.name)
        d.links = []
        for action, title in actions:
            url = app.url_for(parent_obj=d.value, action=action,
                              resource=d.field.other,
                              remote_name=d.field.name,
                              _memory=False)
            d.links.append((url, title, title))

class PreformattedCollectionLinks(CollectionLinks):
    css = CollectionLinks.css + Pre.css
    template = "genshi:tw.rum.templates.pre_collection_links"

class LinkMixin(object):
    def update_params(self, d):
        super(LinkMixin, self).update_params(d)
        if d.value:
            d.url=app.url_for(obj=d.value, _memory=False)

class RelationLink(LinkMixin, ExpandableSpan):
    template = "genshi:tw.rum.templates.expandable_relation_link"

    def update_params(self, d):
        super(RelationLink, self).update_params(d)
        if not d.value:
            d.template = Span.template.split(':')[1]

class PreformattedRelationLink(LinkMixin, Span):
    template = "genshi:tw.rum.templates.pre_link"
    css = [
        CSSLink(modname=modname,
        filename='static/pre.css'
    )]

            
class BaseShowWidget(Widget):
    params = ["fields", "labels","link_to_functions"]
    fields = []
    link_to_functions = []
    template = "genshi:tw.rum.templates.default_show"

    def __init__(self, *args, **kw):
        super(BaseShowWidget, self).__init__(*args, **kw)
        self.labels = []
        self.link_to_functions = []
        for label, field, link_to_function in self.fields:
            self.labels.append(label)
            self.link_to_functions.append(link_to_function)
            self._append_child(field)

    def adapt_value(self, value):
        return value

class RumCalendarMixin(object):
    button_text = _("Choose")

    def calendar_lang(self):
        return app.locale
        
    
class RumCalendarDatePicker(forms.CalendarDatePicker, RumCalendarMixin):
    date_format = '%Y-%m-%d'

class RumCalendarTimePicker(forms.CalendarDateTimePicker, RumCalendarMixin):
    date_format = '%H:%M:%S'

class RumCalendarDateTimePicker(forms.CalendarDateTimePicker, RumCalendarMixin):
    date_format = '%Y-%m-%d %H:%M:%S'

class PasswordSpan(Span):
    def update_params(self, d):
        super(PasswordSpan, self).update_params(d)
        d.value = "********"

class EditPasswordField(forms.PasswordField):
    params = ['checkbox_label', 'value_when_disabled']
    checkbox_label = _("Change?")
    attrs = {'disabled':True}

    javascript = [edit_passwd_js]

    def __init__(self, *args, **kw):
        super(EditPasswordField, self).__init__(*args, **kw)
        self.validator = validators.UnicodeString(
            if_missing=self.value_when_disabled
            )

    def update_params(self, d):
        super(EditPasswordField, self).update_params(d)
        args = dict(checkbox_label=unicode(d.checkbox_label))
        self.add_call(js_function('new EditPasswordField')(args, self.id))
        d.value = '*********';



class ListForm(forms.ListForm):
    submit_text = _("Submit")
    css = [form_css]

class TableForm(forms.TableForm):
    submit_text = _("Submit")

class _NonMissing:
    """I'm just a placeholder to signal that mangle_forms default parameter has
    not been overriden"""

def mangle_form(cls, missing_placeholder=_NonMissing):
    """
    I create a subclass of ``cls`` which will have a hidden field named
    _method to work around the fact that most browsers don't support submitting
    forms with other HTTP methods than GET and POST.

    This field is populated which whatever the form's ``method`` parameter is.

    The resulting form will have the same name as ``cls`` and should behave
    the same way except that checks like ``type(obj) == cls`` and identity
    will fail. ``isinstance`` however will work fine.

    Example::

        >>> form = mangle_form(forms.Form)()
        >>> form # doctest: +ELLIPSIS
        Form(None, children=[SubmitButton('submit', children=[], **{'default': 'Submit', 'label_text': ''}), HiddenField('_method', children=[], **{'validator': <String object ... if_missing=None>}), HiddenField('_next_redirect', children=[], **{'validator': <String object ... if_missing=None>})
        >>> assert '_method' in form.render()
        >>> assert '_next_redirect' in form.render()
    
    Method is mangled since most browser's can't handle other than get & post::

        >>> assert 'post' in form.render(method='put')
        >>> assert 'get' in form.render(method='get')
    """
    if not isclass(cls):
        # handle form instances
        inst = cls
        cls = inst.__class__
    else:
        inst = None

    def post_init(self, *args, **kw):
        forms.HiddenField("_method", parent=self,
                          validator=forms.validators.String(if_missing=None))
        #XXX: Should not be using the request here
        forms.HiddenField("_form_action", parent=self,
                          validator=forms.validators.String(if_missing=None),
                          default=lambda: app.request.routes.get('action'))
        #XXX: Should not be using the request here
        forms.HiddenField("_next_redirect", parent=self,
                          validator=forms.validators.String(if_missing=None),
                          default=lambda: app.request.referer)
    

    def update_params(self, d):
        cls.update_params(self, d)
        # Most browsers don't support other http methods so we change it to
        # POST and store the real method in a hidden field that Routes will
        # use to mangle environ['HTTP_METHOD'] for us
        d.value['_method'] = d.method.upper()
        if 'next_redirect' in d:
            d.value['_next_redirect'] = d.next_redirect
        if d.method.lower() not in ['get','post']:
            d.method = 'post'
        d.value.update(app.request.GET.mixed())
        d.value.update(app.request.POST.mixed())
    


    def validate(self, value, state=None, use_request_local=True):
        """
        This validate pops the hidden '_method' and any placeholder left
        by validation when a field was missing from input and we expected it
        to be missing.

        Note that I won't be executed if this is a subform (a form nested in
        another form) since the outer form won't call us recursively when
        validating as the validator already validates recursively
        """
        if state is None:
            state = DummyState
        


        value = cls.validate(self, value, state, use_request_local)
        value.pop('_method')
        value.pop('_next_redirect')
        value.pop('_form_action')
        for k, v in value.items():
            if v is missing_placeholder:
                del value[k]
        return value
    
    validate.__doc__ = '\n'.join([cls.validate.__doc__, validate.__doc__])

    _is_mangled = True
    __module__ = cls.__module__
    cls_dct = locals()
    cls_dct.pop('cls')
    inst = cls_dct.pop('inst')
    new_cls = type(cls.__name__, (cls,), cls_dct)
    if inst:
        object.__setattr__(inst, '__class__', new_cls)
        return inst.clone() # return a clone so post_init is called
    return new_cls

def is_mangled(form):
    return getattr(form, '_is_mangled', False)

class DummyState:
    _ = staticmethod(i18n.ugettext)

class TableDataLink(Widget):
    template="genshi:tw.rum.templates.csv_link"
    params=["query", "memory", "resource", "format"]
    memory=True
    query=None
    format='csv'

    def update_params(self, d):
        super(TableDataLink, self).update_params(d)
        routes_kw=app.request.routes.get
        
        query=d.query
        memory=d.memory
        kwds=dict()
        kwds["format"]=d.format
        for k in "parent,parent_id,remote_name,resource".split(","):
            kwds[k]=routes_kw(k, None)
        if d.resource is not None:
            kwds["resource"]=d.resource
        if not query is None:
            kwds.update(
                query.clone(
                    limit=None, 
                    offset=None).as_flat_dict())
        d.link=app.url_for(**kwds)

class CSVLink(TableDataLink):
    format='csv'

class XLSLink(TableDataLink):
    format='xls'

class ObjectHiddenField(InputField):
    template="genshi:tw.rum.templates.object_hidden"
    type="hidden"
    def update_params(self, d):
        super(ObjectHiddenField, self).update_params(d)
        value=d.value
        d.obj_value=self.validator.to_python(value)
        if d.obj_value is not None:
            d.url=app.url_for(obj=d.obj_value, action='show', _memory=False)