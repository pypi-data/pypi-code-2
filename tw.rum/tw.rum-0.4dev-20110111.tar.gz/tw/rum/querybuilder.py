from tw.api import lazystring as _
from tw import forms
from tw.forms.validators import UnicodeString

from rum import app, fields
from rum.query import Query
from tw.rum.repeater import JSRepeater

from rum.genericfunctions import generic

@generic 
def query_fields(resource):
    "Get fields for query"

@query_fields.when()
def _default_fields(resource):
    try:
        return [(f.name, f.label)
                for f in app.request.environ['rum.fields']
                if getattr(f, 'searchable', False)]
    except:
        return []



def get_fields():
    
    return query_fields(resource=app.request.routes['resource'])


operators = [
    ("eq", _("is")),
    ("neq", _("is not")),
    ("contains", _("contains")),
    ("startswith", _("begins with")),
    ("endswith", _("ends with")),
    ("lt", _("<")),
    ("gt", _(">")),
    ("lte", _("<=")),
    ("gte", _(">=")),
    ("null", _("is empty")),
    ("notnull", _("is not empty")),
    ]

class ExpressionWidget(forms.FieldSet):
    css_class = "rum-querybuilder-expression"
    template = "genshi:tw.rum.templates.expression"
    fields = [
        forms.SingleSelectField("c", options=get_fields),
        forms.SingleSelectField("o", options=operators),
        forms.TextField("a", validator=UnicodeString),
        ]

class QueryWidget(forms.FieldSet):
    template = "genshi:tw.rum.templates.querybuilder"
    css_class = "rum-query-widget"
    fields = [
        forms.SingleSelectField("o",
            options=[("and", _("AND")), ("or", _("OR"))]
            ),
        JSRepeater("c", widget=ExpressionWidget(), extra=0,
                   add_text=_("Add criteria"), remove_text=_("Remove"))
        ]
    # def update_params(self, d):
    #     super(QueryWidget, self).update_params(d)
    #     fields = get_fields()
    #     child_args=d.child_args or {}
    #     for c in self.children:
    #         if c.name=='c':
    #             repeater=c
    #     for c in repeater.children:
    #         composite_name = 'c.' + c.name
    #         args=child_args.set_default(composite_name, {})
    #         args['options']=get_fields()

class QueryBuilder(forms.TableForm):
    method = "get"
    css_class = "rum-query-builder"
    submit_text = _("Filter records")
    fields = [
        QueryWidget("q", label_text=''),
        ]

    def adapt_value(self, value):
        if isinstance(value, Query):
            value = value.as_dict()
        return value
