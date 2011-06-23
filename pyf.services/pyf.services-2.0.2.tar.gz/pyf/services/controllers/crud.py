# -*- coding: utf-8 -*-
"""Crud Controllers"""

from xml.sax.saxutils import escape

from tg import expose, url, redirect, request, response
from tg.decorators import (paginate, with_trailing_slash, Decoration,
                           without_trailing_slash)
from pylons import tmpl_context
from pylons.controllers.util import abort
from repoze.what import predicates

from tg.controllers import RestController

from pyf.services.model import DBSession
from pyf.services.versionning import get_repository

from tgext.crud.decorators import registered_validate, register_validators
from sprox.fillerbase import TableFiller
from genshi.template import MarkupTemplate

from sprox.widgets import SproxDataGrid
from sprox.providerselector import ProviderTypeSelector

from repoze.what.predicates import has_any_permission, NotAuthorizedError
from tg import require

from tg.flash import flash

from docutils.core import publish_parts

import operator

import pylons

from pyf.services.core.docs import trim

def has_model_permission(perm_name):
    def decor(fun):
#        deco = Decoration.get_decoration(fun)
        def decorated_function(self, *args, **kw):
            full_perm_name = "%s_%s" % (self.model.__name__.lower(), perm_name)
            new_fun = require(has_any_permission('manage', full_perm_name))(fun)
            
            return new_fun(self, *args, **kw)
            
        if hasattr(fun, 'decoration'):
            setattr(decorated_function, 'decoration', fun.decoration)
            
        return decorated_function
    return decor


class SecureCrudRestController(RestController):
    """ This is a copy of the crud rest controller with custom permission,
    save to versionning and flow support for large data sets """
    #allow_only = predicates.has_permission('manage')
    __order_by__ = None
    __desc__ = None
    
    __post_to_versionning__ = False
    
    def __init__(self, session):
        self.provider = ProviderTypeSelector().get_selector(self.model).get_provider(self.model, hint=session)

        self.session = session

        #this makes crc declarative
        check_types = ['new_form', 'edit_form', 'table', 'table_filler', 'edit_filler']
        for type_ in check_types:
            if not hasattr(self, type_) and hasattr(self, type_ + '_type'):
                setattr(self, type_, getattr(self, type_ + '_type')(self.session))

        if hasattr(self, 'new_form'):
            #register the validators since they are none from the parent class
            register_validators(self, 'post', self.new_form)
        if hasattr(self, 'edit_form'):
            register_validators(self, 'put', self.edit_form)
            
        #self.get_all = require()
        
    def check_model_permission(self, perm_name):
        full_perm_name = "%s_%s" % (self.model.__name__.lower(), perm_name)
        predicate = has_any_permission('manage', full_perm_name)
        try:
            predicate.check_authorization(request.environ)
        except NotAuthorizedError, e:
            reason = unicode(e)
            if request.environ.get('repoze.who.identity'):
                # The user is authenticated.
                code = 403
                status = 'error'
            else:
                # The user is not authenticated.
                status = 'warning'
                code = 401
            response.status = code
            
            flash(reason, status=status)
            abort(code, reason)
    
    def get_available_values(self, key_getter):
        """
        Returns all the availables values for a key in the model.
        WARNING: Don't use this function! Use get_available_values_for_column instead.
        """
        query = DBSession.query(self.model)
        out = []
        for x in query.all():
            value = key_getter(x)
            if value not in out:
                out.append(value)
        return out

    def get_available_values_for_column(self, column):
        """
        Returns all the availables values for a key in the model.
        """
        colobj = getattr(self.model, column)
        query = DBSession.query(colobj)
        query = query.group_by(colobj)
        return map(operator.itemgetter(0), query)
    
    @has_model_permission('view')
    @with_trailing_slash
    @paginate('value_list', items_per_page=20)
    @expose('pyf.services.templates.get_all')
    @expose('json')
    def get_all(self, *args, **kw):
        """Return all records.
           Pagination is done by offset/limit in the filler method.
           Returns an HTML page with the records if not json.
        """        
        query = DBSession.query(self.model)
        kw = kw.copy()
        if 'order_by' not in kw and self.__order_by__ is not None:
            kw['order_by'] = self.__order_by__
        if 'desc' not in kw and self.__desc__ is not None:
            kw['desc'] = self.__desc__
        
        if 'order_by' in kw and kw['order_by']:
            col = getattr(self.model, kw['order_by'])
            if 'desc' in kw and kw['desc'] and not kw['desc'] == 'False':
                col = col.desc()
            query = query.order_by(col)
        
        if pylons.request.response_type == 'application/json':
            count = query.count()
            values = query.all()
            return dict(value_list=values, count=count)
        
        tmpl_context.widget = self.table
        return dict(model=self.model.__name__, value_list=query,
                    line_formater=self.table_filler.get_value_item,
                    kw=kw)
    
#    @has_model_permission('view')
#    @expose('tgext.crud.templates.get_one')
    @without_trailing_slash
    @expose()
    @expose('json')
    def get_one(self, *args, **kw):
        """get one record, returns HTML or json"""
        #this would probably only be realized as a json stream
        if pylons.request.response_type == 'application/json':
            tmpl_context.widget = self.edit_form
            pks = self.provider.get_primary_fields(self.model)
            kw = {}
            for i, pk in  enumerate(pks):
                kw[pk] = args[i]
            value = self.edit_filler.get_value(kw)
        
            return dict(value=value)
        else:
            flash('No view for %s' % self.model.__name__)
            redirect('../')
    
    @without_trailing_slash
    @has_model_permission('edit')
    @expose('pyf.services.templates.edit')
    def edit(self, *args, **kw):
        if self.__post_to_versionning__:
            item = DBSession.query(self.model).get(int(args[0]))
            get_repository().check_item(item)
        return self.__edit(*args, **kw)
    
    def __edit(self, *args, **kw):
        """Display a page to edit the record."""
        tmpl_context.widget = self.edit_form
        pks = self.provider.get_primary_fields(self.model)
        kw = {}
        for i, pk in  enumerate(pks):
            kw[pk] = args[i]
        value = self.edit_filler.get_value(kw)
        value['_method'] = 'PUT'
        return dict(value=value, model=self.model.__name__)
    
    @without_trailing_slash
    @expose('pyf.services.templates.edit')
    def new(self, *args, **kw):
        self.check_model_permission('create')
        tmpl_context.widget = self.new_form
        return dict(value=kw, model=self.model.__name__)
    
    @without_trailing_slash
    @expose()
    @expose('json')
    @registered_validate(error_handler=edit)
    def put(self, *args, **kw):
        """update"""
        self.check_model_permission('edit')
        
        pks = self.provider.get_primary_fields(self.model)
        for i, pk in enumerate(pks):
            if pk not in kw and i < len(args):
                kw[pk] = args[i]
        c = self.provider.update(self.model, params=kw)
        if self.__post_to_versionning__:
            get_repository().store_item(c, user=request.identity['user'].user_name)
        
        if pylons.request.response_type == 'application/json':
            return dict(value=c)
        
        redirect('../')
    
    @expose()
    @expose('json')
    @registered_validate(error_handler=new)
    @without_trailing_slash
    def post(self, *args, **kw):
        """create"""
        self.check_model_permission('create')
        c = self.provider.create(self.model, params=kw)
        if self.__post_to_versionning__:
            get_repository().store_item(c, user=request.identity['user'].user_name)
        
        if pylons.request.response_type == 'application/json':
            return dict(value=c)
        
        raise redirect('./')
    
    @expose()
    def post_delete(self, *args, **kw):
        """This is the code that checks remove the record from versionning and
        calls the deleting code """
        if self.__post_to_versionning__:
            item = DBSession.query(self.model).get(int(args[0]))
            get_repository().delete_item(item, user=request.identity['user'].user_name)
            
        return self.__post_delete(*args, **kw)
    
    def __post_delete(self, *args, **kw):
        """This is the code that actually deletes the record"""
        pks = self.provider.get_primary_fields(self.model)
        d = {}
        for i, arg in enumerate(args):
            d[pks[i]] = arg
        self.provider.delete(self.model, d)
        redirect('./')

    @expose('tgext.crud.templates.get_delete')
    def get_delete(self, *args, **kw):
        """This is the code that creates a confirm_delete page"""
        return dict(args=args)
    
    @expose('pyf.services.templates.classdocs')
    def docs(self):        
        return dict(title=self.model.__name__,
                    description=publish_parts(trim(self.model.__doc__),
                                              writer_name="html")["html_body"],
                    contents=((key,
                               publish_parts(trim(value.__doc__),
                                             writer_name="html")["html_body"])\
                               for key, value\
                               in self.model.__dict__.iteritems()\
                               if not key.startswith('_')))
        
    
class FancyTableFiller(TableFiller):
    __base_url__ = ''
    __actions_size__ = '60px'
    __other_links__ = None
    
    def __actions__(self, obj):
        """Display standard delete and edit actions as clickable fam fam icons."""
        primary_fields = self.__provider__.get_primary_fields(self.__entity__)
        pklist = '/'.join(map(lambda x: str(getattr(obj, x)), primary_fields))
        entityname = str(obj.__class__).split('.')[-1][:-2]
        action_template = """\
        <div style="min-width:%s;min-height:16px">
            <div class="sproxactions">
                <form method="post" action="${base_url}${pklist}" class="button-to">
                    <input type="hidden" name="_method" value="DELETE" />
                    <input
                       class="delete-button"
                       onclick="return confirm('Delete ${item} #${itemid}?');"
                       value=""
                       type="submit"
                       style="background:url('/images/silk/${itype}_delete.png') no-repeat;"/>
                </form>
            </div>
            <div style="float:right;display:inline;">
                <a href="${base_url}${pklist}/edit" style="text-decoration:none"
                    ><img src="/images/silk/${itype}_edit.png" alt="edit" /></a>
                <a href="${base_url}${pklist}" style="text-decoration:none"
                    ><img src="/images/silk/${itype}_go.png" alt="view" /></a>%s
            </div>
        </div>""" % (self.__actions_size__, (self.__other_links__ or ""))
        return MarkupTemplate(action_template).generate(
                                                pklist=pklist,
                                                base_url=self.__base_url__,
                                                itype=itemize(entityname.lower()),
                                                item=entityname,
                                                itemid=obj.id)
    
    def get_value_item(self, obj, **kw):
        import inspect
        
        row = {}
        for field in self.__fields__:
            field_method = getattr(self, field, None)
            if inspect.ismethod(field_method):
                argspec = inspect.getargspec(field_method)
                if argspec and (len(argspec[0]) - 2 >= len(kw) or argspec[2]):
                    value = getattr(self, field)(obj, **kw)
                else:
                    value = getattr(self, field)(obj)
            else:
                value = getattr(obj, field)
                if 'password' in field.lower():
                    row[field] = '******'
                    continue
                elif isinstance(value, list):
                    value = self._get_list_data_value(field, value)
                elif self.__provider__.is_relation(self.__entity__, field) and value is not None:
                    value = self._get_relation_value(field, value)
                elif self.__provider__.is_binary(self.__entity__, field) and value is not None:
                    value = '&lt;file&gt;'
            row[field] = unicode(value)
        return row
    
    def get_values(self, values, **kw):
        for value in values:
            yield self.get_value_item(value, **kw)

def render_boolean(attr):
    def render_func(controller, obj):
        value = bool(getattr(obj, attr))
        img = ('cross.png', 'tick.png')[value]
        return '<img src="/images/silk/%(img)s" alt="%(value)s" />' % {
                    'img': img,
                    'value': value
                }
    return render_func

def render_link(base_url, url_attr='id', display_name_property='display_name'):
    def render_func(obj):
        url_ = url(base_url % str(getattr(obj, url_attr)))
        return '<a href="%s">%s</a>' % (url_, escape(getattr(obj, display_name_property)))
    return render_func
    
def render_link_field(base_url, property, order_by, is_list=True, url_attr='id',
                      display_name_property='display_name'):
    def render_func(controller, obj):
        get_link = render_link(base_url,
                               display_name_property=display_name_property)
        if is_list:
            objs = sorted(getattr(obj, property), key=operator.attrgetter(order_by))
            objs = ', '.join([get_link(o) for o in objs])
        else:
            objs = getattr(obj, property)
            if objs:
                objs = get_link(objs)
            else:
                objs = ""
                
        return objs.join(('<div>', '</div>'))
    
    return render_func

ITEM_TYPES = dict()

def itemize(ename):
    """
    Map a lower-cased entity name to a famfamfam icon.
    """
    return dict({
        'group':'group',
        'issue':'bug',
        'location':'map',
        'organisation':'brick',
        'permission':'key',
        'user':'user',
        'dispatch':'link',
        'tubelayer': 'brick',
        'descriptor': 'plugin',
        'clientprofile': 'transmit',
        'tube': 'cog',
        'tubetask': 'date'
    }.items() + ITEM_TYPES.items()).get(ename, 'page_white')
    

class DataGrid(SproxDataGrid):
    template = "genshi:sprox.widgets.templates.datagrid"
    xml_fields = ['actions'] 
    css_class = "datatable"
