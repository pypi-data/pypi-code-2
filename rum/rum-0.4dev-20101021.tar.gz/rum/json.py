from turbojson.jsonify import jsonify, GenericJSON
from rum.i18n import LazyString
from rum import fields, app, Query
from rum.genericfunctions import generic, when, before, around
@jsonify.when((fields.Field,))
def jsonify_field(obj):
    """
    >>> jsonify_field(fields.Integer("foo"))
    {'read_only': False, 'sortable': True, 'name': 'foo', 'searchable': True, 'default': NoDefault, 'required': False, 'label': 'Foo', 'range': (None, None), 'type': 'rum.fields.Integer'}
    """
    attrs = dict(obj.attrs)
    attrs['type'] = obj.field_type
    return attrs

@jsonify.when((LazyString, ))
def jsonify_lazy_string(obj):
    return obj.eval()

@jsonify.when((fields.Relation,))
def jsonify_relation(obj):
    attrs = dict(obj.attrs)
    attrs['other'] = app.url_for(attrs['other'], action='_meta')
    attrs['type'] = obj.field_type
    return attrs

@jsonify.when((Query,))
def jsonify_query(obj):
    """
    >>> from rum.query import Query, and_, eq, or_, gt, lt, desc
    >>> q = Query(and_([eq('name', 'Alberto'), or_([gt('age', 20), lt('age', 30)])]), [desc('join_date')], 10, 10)
    >>> jsonify_query(q)
    {'q': {'a': None, 'c': [{'a': 'Alberto', 'c': 'name', 'o': 'eq'}, {'a': None, 'c': [{'a': 20, 'c': 'age', 'o': 'gt'}, {'a': 30, 'c': 'age', 'o': 'lt'}], 'o': 'or'}], 'o': 'and'}, 'sort': [{'c': 'join_date', 'dir': 'desc'}], 'limit': 10, 'count': None, 'offset': 10}
    """
    d = obj.as_dict()
    d['count'] = obj.count
    return d


class JsonificationPreparer(object):
    def __init__(self, app):
        self.app=app
    @generic
    def jsonify_property(self, res, item, field):
        """jsonify attribute field.name of item"""
        pass
    
    @jsonify_property.when("isinstance(field, fields.Relation)")
    def __default_jsonify_property(self, res, item, field):
        """don't jsonify relation attributes"""
        pass
    
    @jsonify_property.when()
    def __default_jsonify_property(self, res, item, field):
        res[field.name]=getattr(item, field.name)
    def __call__(self, item):
        return self.prepare(item)
    @generic
    def prepare(self, item):
        """jsonify item"""
        pass
    prepare.when("isinstance(item, dict)")
    def _prepare_dict(self, item):
        return dict([(k,self(v)) for (k,v) in item.iteritems()])
    prepare.when("isinstance(item, list)")
    def _prepare_list(self, item):
        return [self(k) for k in item]
    prepare.when("not (self.app is  None) and item.__class__ in self.app.resources")
    def _prepare_res(self, item):
        dct = {}
        action=self.app.request.routes['action']
        res_fields =  self.app.fields_for_resource(item.__class__)
        if res_fields is not None:
            for field in res_fields:
                if self.app.policy.has_permission(obj=item,
                    attr=field.name,
                    action=action):
                    self.jsonify_property(dct, item, field)
        return dct
    prepare.when()
    def _prepare_default(self, item):
        return item
class JsonEncoder(object):
    generic_encoder=GenericJSON()
    def encode(self, item):
        encoder=JsonificationPreparer(app._current_obj())
        prepared=encoder(item)
        return self.generic_encoder.encode(prepared)