from inspect import isclass

from dateutil.tz import tzlocal
from tw import forms
from tw.api import lazystring as _
from rum import ViewFactory, fields, app, validators
from rum.basefactory import cache_call
from rum.genericfunctions import around
from rum.exceptions import NoApplicableMethods
from tw.forms.datagrid import Column
from tw.forms.fields import FileField, PasswordField
from tw.rum import widgets
from tw.rum.paginator import Paginator
from tw.rum.querybuilder import QueryBuilder
from tw.rum.autocompletion import AutoCompletion
from tw.rum.contextlinks import ContextLinks
from rum.genericfunctions import generic
from tw.api import Widget

__all__ = ["WidgetFactory"]

import logging
log = logging.getLogger(__name__)

get = ViewFactory.get.im_func

def NoWidget(*args, **kw):
    return None


new_actions = frozenset(['new', 'create'])
edit_actions = frozenset(['edit', 'update'])
input_actions = new_actions.union(edit_actions)
inline_actions = frozenset(['inline_index', 'inline_show', 'inline_preview'])
mangle_on = input_actions.union(set(['confirm_delete']))

def to_field_normal(field,widget, resource ):
    link_to_function = None
    if isinstance(field, fields.List):
        def link_to_function(value):
            return app.url_for(parent_obj=value, 
                parent=resource,
                remote_name=field.name, action='index')
    return (field.label,widget, link_to_function)
def to_column(field,widget):

    return Column(name=field.name,
        title=field.label,getter=widget, 
        options=dict(field=field))


class WidgetFactory(ViewFactory):
    # Note that these are used at import time by register_widget. Modifying
    # them won't have an effect. Use register_widget to override them with
    # A higher priority than the default (-1)
    
    inline_field_map = {
        fields.InternalField:           None,
        fields.Image:                   widgets.ImagePreview,
        fields.String:                  widgets.ExpandableSpan,
        fields.PreformattedText:        widgets.Pre,
        fields.Binary:                  widgets.BinaryLink,
        fields.Relation:                widgets.RelationLink,
        fields.Password:                widgets.PasswordSpan,
        fields.Collection:              widgets.CollectionLinks,
        fields.Field:                   widgets.Span,
        fields.Url:                     widgets.Url,
    }
    
    
    input_field_map = {
        fields.String:      forms.TextField,
        fields.Integer:     forms.TextField,
        fields.Decimal:     forms.TextField,
        fields.DateTime:    widgets.RumCalendarDateTimePicker,
        fields.Date:        widgets.RumCalendarDatePicker, 
        fields.Time:        widgets.RumCalendarTimePicker,
        fields.Boolean:     widgets.CheckBox,
        fields.Text:        forms.TextArea,

        fields.UnicodeText: forms.TextArea,
        fields.Unicode:     forms.TextField,
        fields.Relation:    widgets.SingleSelectField,
        fields.Collection:  forms.MultipleSelectField,
        fields.VersionID:   forms.HiddenField, 
        fields.Binary:      None,
        #XXX: Need to add more metadata to fields since a CBT here almost never makes sense 
        fields.List:        forms.MultipleSelectField, 
        fields.InternalField:    None, 
    }
    
   

    # These are looked up dynamically, modifying this class attribute will
    # have an effect on all instances of this factory
    action_map = {
        'index': widgets.RumDataGrid,
        'edit':  widgets.ListForm,
        'new':  widgets.ListForm,
        'update':  widgets.ListForm,
        'create':  widgets.ListForm,
        'confirm_delete':  widgets.ListForm,
        'delete':  widgets.ListForm,
        'show': widgets.BaseShowWidget,
        'preview': widgets.BaseShowWidget,
    }

    def __init__(self, text_field_size=50):
        self.text_field_size = text_field_size
        self._cache = {}
        super(WidgetFactory, self).__init__()
        self.default_index_fields=dict()
        rum_widgets = app.config['widgets']
        rum_widgets.setdefault('paginator', Paginator())
        rum_widgets.setdefault('querybuilder', QueryBuilder())
        rum_widgets.setdefault('csvlink', widgets.CSVLink())
        rum_widgets.setdefault('xlslink', widgets.XLSLink())
        rum_widgets.setdefault('context_links', ContextLinks())
        
    @generic
    def __call__(self, resource, parent=None, remote_name=None, attr=None,
                 action=None, fields=tuple()):
        """Override to remove extraneous arguments Widgets won't like"""
    
    @__call__.when()
    def __call_default_implemenation(self, resource, parent=None, remote_name=None, attr=None,
                 action=None, fields=tuple()):
        """Override to remove extraneous arguments Widgets won't like"""
        args = {'resource_fields': fields}
        widget = self.get(resource, parent, remote_name, attr, action, args)
        if widget and isclass(widget):
            return widget(**args)
        else:
            return widget
        
    # Cache generated forms in factory instance
    around(__call__, "isinstance(attr, basestring)")(cache_call)
    #caching plays evil with policies
    #policy is checks, whether to generate the widget for a field.
    #after that we can cache the call

    @classmethod
    def register_widget(cls, widget, field, actions, _prio=0, **defaults):
        if 'prio' in defaults:
            import warnings
            warnings.warn(
                "prio is deprecated, please pass it as the _prio argument"
                )
            _prio = kw.pop('prio')
        cls.register(
            widget, pred="isinstance(attr, field) and action in actions",
            _prio=_prio, defaults=defaults
            )

    @staticmethod
    def add_validator(validator, args):
        if 'validator' in args:
            args['validator'] = validators.All(args['validator'], validator)
        else:
            args['validator'] = validator
    
    
    @staticmethod
    def prepend_validator(validator, args):
        if 'validator' in args:
            args['validator'] = validators.All(validator, args['validator'])
        else:
            args['validator'] = validator
    

    @get.after("'id' not in args")
    def _generate_id(self, resource, parent, remote_name, attr, action, args):
        if 'id' not in args:
            args['id'] = self.next_id()


    @get.around("attr is None and action in mangle_on")
    def _mangle_form(next_method, self, resource, parent, remote_name, attr,
                     action, args):
        form = next_method(self, resource, parent, remote_name, attr, action,
                           args)
        if not widgets.is_mangled(form):
            form = widgets.mangle_form(form, self.Missing)
        return form

    @get.around("isinstance(attr, fields.InternalField)")
    def _extend_args(next_method, self, resource, parent, remote_name, attr,
                     action, args):
        # extend args with args that would have been generated for the wrapped
        # type
        self.get(resource, parent, remote_name, attr.type, action, args)
        return next_method(self, resource, parent, remote_name, attr, action, args)

    #
    # before rules: These are used to add arguments to the widget
    #
    @get.before("isinstance(attr, fields.String)")
    def _set_size(self, resource, parent, remote_name, attr, action, args):
        args.setdefault('size', self.text_field_size)

    @get.before("isinstance(attr, fields.String) and attr.length is not None")
    def _set_length(self, resource, parent, remote_name, attr, action, args):
        l = attr.length
        if l < self.text_field_size:
            args['size'] = l
        args.setdefault('max_size', l)
        v = validators.MaxLength(l)
        self.add_validator(v, args)

    
    @get.when("isinstance(attr, fields.RelatedField)")
    def _switch_to_real_field(self, resource, parent, remote_name, attr, action, args):
        orig_field=args['field']
        args['field']= orig_field.real_field
        args['field_name']=orig_field.real_field.name
        lookup = orig_field.real_field
        if not isinstance(lookup, fields.RelatedField):
            lookup=lookup.name
        next_relation = orig_field.next_relation_in_chain()
        res= self(
            resource=next_relation.other,
            parent=resource,
            remote_name=next_relation.remote_name,
            attr=lookup,
            action=action)
        if res is not None:
            #not yet handled, use clone...
            return res.clone(field_name=orig_field.name, field=orig_field)
        else:
            return None
    
    @get.when("isinstance(attr, fields.RelatedField) and isinstance(attr.real_field, fields.Collection)")
    def _switch_to_real_field(self, resource, parent, remote_name, attr, action, args):
        #do not support that yet
        return None

    @get.before("isinstance(attr, fields.Time) and attr.has_timezone")
    def _set_tzinfo(self, resource, parent, remote_name, attr, action, args):
        #XXX: This should be dynamically configurable
        args['tzinfo'] = tzlocal()

    @get.before("isinstance(attr, fields.Field) and not attr.has_default and "
                "not attr.required")
    def _set_None_as_default(self, resource, parent, remote_name, attr, action,
                             args):
        args.setdefault('default', None)

    @get.before("isinstance(attr, (fields.Date,fields.Time)) and "
                "not attr.has_default and not attr.required")
    def _set_date_allow_empty(self, resource, parent, remote_name, attr, action,
                              args):
        args.setdefault('not_empty', False)

    @get.before("attr is None and action in input_actions")
    def _gen_input_widgets(
        self, resource, parent, remote_name, attr, action, args
        ):

        fields = args['resource_fields']
        widgets = []
        for field in fields:
            try:
                widgets.append(
                    self._construct_field_widget(resource, parent, remote_name, field, action)
                    )
            except NoApplicableMethods:
                pass
        args['fields'] = filter(None, widgets)

    @get.when("isinstance(attr, basestring)", prio=-1)
    def _gen_widget_by_attrname(
        self, resource, parent, remote_name, attr, action, args
        ):
        fields = self._allowed_fields_for_resource(resource, action=action)
        for field in fields:
            if field.name == attr:
                return self.get(
                    resource, parent, remote_name, field, action, args
                    )
        

    def _allowed_fields_for_resource(self, resource, action):
        log.debug("allowed field called for res %s and action %s"%(resource, action))
        if action is not None and action.startswith("inline_"):
            action=action[len("inline_"):]
        return [f for f in app.fields_for_resource(resource) if app.policy.has_permission(obj=resource, attr=f.name, action=action)]
    
    def _construct_field_widget(self, resource, parent, remote_name, f, field_action):
        res=self(resource, parent, remote_name, f.name, field_action)
        if res is not None:
            return res
        if isinstance(f, fields.RelatedField):
            return self(resource, parent, remote_name,f, field_action)
        return None
        
    @get.before(
        "attr is None and action in set(['index'])"
        )
    def _gen_fields(self, resource, parent, remote_name, attr, action, args):
        if action=="index":
            converter=to_column
        
        field_action = 'inline_' + action

        new_fields=[]
        
        for f in args['resource_fields']:
            
            widget = self._construct_field_widget(resource, parent, remote_name, f, field_action)
            if widget:
                new_fields.append(converter(f, widget))
        args['remote_name'] = remote_name
        args['parent_resource']      = parent
        args['resource']    = resource
        args['fields']=new_fields


    @get.before(
        "attr is None and action in set(['show', 'preview'])"
        )
    def _gen_fields(self, resource, parent, remote_name, attr, action, args):

        converter=to_field_normal

        fields=args['resource_fields']
        
        new_fields=[]
        
        for f in fields:
            widget = self._construct_field_widget(resource, parent, remote_name, f, 'inline_'+action)
            if widget:
                new_fields.append(converter(f, widget, resource))
        
        args['fields']=new_fields


    @get.before("isinstance(attr, fields.Relation) and "
                "not isinstance(attr, fields.Collection) and "
                "action in input_actions")
    def _add_args_for_relation(self, resource, parent, remote_name, attr,
                               action, args):
        v = validators.RelatedFetcher(attr.other)
        self.add_validator(v, args)
        def get_options():
            db_options=list(
                app.repositoryfactory(attr.other).select())
            db_options=sorted(db_options, key=unicode)
            if not getattr(attr, "required", False):
                return [(None, '-------------')] +\
                 db_options
            else:
                return db_options
        args['options'] = get_options
        from routes.util import RoutesException
        try:
            args['completion_url']=app.url_for(resource=attr.other,action="complete", format="json", id=None)
        except RoutesException:#some problems with the tests
            args['completion_url']='foo'
        #handles both autocompletion and singleselect fields
        args['resource']=attr.other
        
    @get.before("isinstance(attr, fields.Collection) and "
                "action in input_actions")
    def _add_args_for_collection(self, resource, parent, remote_name, attr,
                               action, args):
        v = validators.RelatedFetcher(attr.other)
        self.add_validator(v, args)
        def get_options():
            return list(app.repositoryfactory(attr.other).select())
        args['options'] = get_options


    @get.before(
        "isinstance(attr, fields.List) and action in input_actions"
        )
    def _add_args_for_related_list(self, resource, parent, remote_name, attr,
                                   action, args):
        v = validators.RelatedFetcher(attr.other)
        self.add_validator(v, args)
        def get_options():
            return list(app.repositoryfactory(attr.other).select())
        args['options'] = get_options


    @get.before("isinstance(attr, fields.PrimaryKey) "
                "and action in edit_actions")
    def _disable_field(self, resource, parent, remote_name, attr, action, args):
        """When an object is edited, we show the primary key in a disabled
        field and instruct the validator to return a special marker when the
        field is missing from PUT data.
        """
        args['disabled'] = True
        v = validators.UnicodeString(if_missing=self.Missing)
        self.add_validator(v, args)



    @get.before("isinstance(attr, fields.Integer) and action in input_actions")
    def _add_Int(self, resource, parent, remote_name, attr, action, args):
        (min_value, max_value)=attr.range
        kwds=dict()
        if min_value:
            kwds["min"]=min_value
        if max_value:
            kwds["max"]=max_value
        v = validators.Int(**kwds)
        self.add_validator(v, args)

    @get.before(
        "isinstance(attr, fields.Field) and attr.required and "
        "not (isinstance(attr,fields.Boolean) or isinstance(attr,fields.Date)) "
        "and action in input_actions")
    def _add_NotEmpty(self, resource, parent, remote_name, attr, action, args):
        v = validators.NotEmpty
        self.add_validator(v, args)

    @get.before("isinstance(attr, fields.Field)")
    def _set_id_and_label(self, resource, parent, remote_name, attr, action,
                          args):
        args['id'] = attr.name
        args['label_text'] = attr.label

    @get.before("attr is None and action in new_actions")
    def _set_meth_on_create(self, resource, parent, remote_name, attr, action,
                            args):
        args['method'] = 'post'

    @get.before("attr is None and action in edit_actions")
    def _set_meth_on_update(self, resource, parent, remote_name, attr, action,
                            args):
        args['method'] = 'put'

    @get.before("attr is None and action in set(['confirm_delete', 'delete'])")
    def _set_meth_on_delete(self, resource, parent, remote_name, attr, action,
                            args):
        args['method'] = 'delete'
        args['submit_text'] = _('Delete')

    @get.before(
        "isinstance(attr, fields.HTMLText) and action in inline_actions",
        )
    def _set_escape_to_false(self, resource, parent, remote_name, attr, action,
                             args):
        args['escape'] = False


    #
    # Rules to return the widget class that'll be used to instantiate the
    # widget in ViewFactory.__call__
    # IMPORTANT: Don't forget to set a low prio so they can be overriden easily
    #


    # Don't render a widget for the parent when creating a child since the
    # controller will set it for us
    get.when("isinstance(attr, fields.Relation) and "
              "attr.remote_name == remote_name and "
              "parent  and action in new_actions",
              prio=-1)(NoWidget)

    @get.when(
        "isinstance(attr, fields.Field) and attr.read_only and "
        "action in input_actions"
        )
    def _no_widget_for_readonly_on_input(*args, **kw):
        return None

    @get.when("attr is None and action in self.action_map", prio=-1)
    def _get_wid_for_action(self, resource, parent, remote_name, attr, action,
                            args):
        return self.action_map[action]



    @get.when("isinstance(attr, fields.PrimaryKey) and not attr.auto "
              "and action in input_actions", prio=-1)
    def _widget_for_pk(self, resource, parent, remote_name, attr, action, args):
        return self.get(resource, parent, remote_name, attr.type, action, args)


    # @get.when("isinstance(attr, fields.Relation) and action in inline_actions "
    #     "and remote_name and attr.remote_name==remote_name "
    #     "and  (parent is not None) and attr.other is not None"
    #     "issubclass(parent, attr.other)", prio=-2)
    # def _dont_display_relation_widget_again_in_grid(self,
    #    resource, parent, remote_name, attr, action, args):
    #    return None
    
    @get.before("isinstance(attr, fields.Field)")
    def _set_field_name(self, resource, parent, remote_name, attr, action, args):
        args['field_name']=attr.name
        args["field"]=attr

    
    @get.when(
        "isinstance(attr, fields.PrimaryKey) and not attr.auto and "
        "action in inline_actions",
        prio=-2
        )
    def _widget_for_inline_non_auto_pk(
        self, resource, parent, remote_name, attr, action, args
        ):
        """
        Matches fields for primary keys when they're not autogenerated. In this
        case we assume they're not surrogate primary keys and actually carry
        useful information. Return the widget that would have been generated for
        the pk's type.
        """
        return self.get(resource, parent, remote_name, attr.type, action, {})

    

    

    @get.when(prio=-3)
    def _default_form(self, resource, parent, remote_name, attr, action, args):
        return widgets.mangle_form(forms.Form())
    
    @get.when("isinstance(attr, fields.Binary) and action in new_actions",
        prio=-1)
    def _gen_binary_upload_widget(self, resource, parent, remote_name, attr, action, args):
        return FileField



    
    
    

    
    @classmethod
    def add_validator_rule(cls, field, validator, actions=input_actions):
        @get.before("isinstance(self, cls) and isinstance(attr, field) and action in actions")
        def _validator_rule(
            self, resource, parent, remote_name, attr, action, args):
            self.add_validator(validator, args)
        
    # Render no fields for auto pks when creating stuff
    get.when("isinstance(attr, fields.PrimaryKey) and attr.auto "
             "and action in new_actions", prio=-1)(NoWidget)

    # No polymorphic discriminators yet. A future enhancement might be to
    # Show a drop-down menu that updated the fields on the fly to deal with
    # the different fields of each polymorphic class
    get.when("isinstance(attr, fields.PolymorphicDiscriminator) and "
             "action != 'inline_index'", prio=-1)(NoWidget)

call_widget_factory = WidgetFactory.__call__.im_func



class BinaryValueValidator(validators.FancyValidator):
    def _to_python(self, value, state):
        if value is not None:
            return value.value
        else:
            return None
   
for field, validator in {
    fields.Email: validators.Email(),
    fields.String: validators.String(if_missing=WidgetFactory.Missing),
    fields.Unicode: validators.UnicodeString(if_missing=WidgetFactory.Missing),
    
}.iteritems():
    WidgetFactory.add_validator_rule(field, validator)

WidgetFactory.add_validator_rule(
    fields.Binary, 
    BinaryValueValidator(), actions=new_actions)

    
WidgetFactory.register_widget(widgets.EditPasswordField, fields.Password, edit_actions, _prio=-2)
WidgetFactory.register_widget(PasswordField, fields.Password, new_actions, _prio=-2)

for field, widget in WidgetFactory.input_field_map.iteritems():
    WidgetFactory.register_widget(widget, field, input_actions, _prio=-2)
for field, widget in WidgetFactory.inline_field_map.iteritems():
    WidgetFactory.register_widget(widget, field, inline_actions, _prio=-2)
# Try to register TinyMCE to render rich HTMLText fields
try:
    from tw import tinymce
except ImportError:
    pass
else:
    class TinyMCE(tinymce.TinyMCE):
        mce_options=dict(
            theme_advanced_path=False,
            preformatted=False
            )
    WidgetFactory.register_widget(
        TinyMCE, fields.HTMLText,  input_actions, _prio=-2,
        locale = lambda: app.locale
        )
