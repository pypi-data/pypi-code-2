#coding=utf-8
from uliweb.i18n import ugettext_lazy as _

def get_model_url(suffix, restful=False):
    def _f(action, id=None, suffix=suffix):
        if suffix.endswith('/'):
            suffix = suffix[:-1]
        if action in ('list', 'add'):
            return "%s/%s" % (suffix, action)
        elif action == 'view':
            def __f(id, url=suffix):
                if restful:
                    return "%s/%s" % (url, id)
                else:
                    return "%s/view/%s" % (url, id)
            return __f
        else:   #others will be direct output
            def __f(id, url=suffix, action=action):
                if restful:
                    return "%s/%s/%s" % (url, action, id)
                else:
                    return "%s/%s/%s" % (url, id, action)
            return __f
    return _f
    
#@expose('/generic/<model>/list')
def generic_model_list(model=None, get_model_url=get_model_url, layout=None, 
    template=None, key_field='id', add_button_text=None, view=None, data=None, json_result=False):
    from uliweb.utils.generic import ListView
    from uliweb import request, response, settings, json, error
    from uliweb.core.html import Tag
    from uliweb.orm import get_model
    
    if not view:
        def key(value, obj):
            url = get_model_url('view')(obj.id)
            return str(Tag('a', value, href="%s" % url))
       
        if not model: 
            model = request.GET.get('model', None)
        if not model or not get_model(model):
            return error("Can't find model [%s], please check it" % model)
        pageno = int(request.GET.get('pageno', 0))
        rows_per_page=settings.get_var('PARA/ROWS_PER_PAGE', 10)
        
        if json_result:
            pageno = int(request.values.get('page', 1)) - 1
            rows_per_page = int(request.values.get('rows', rows_per_page))
        fields_convert_map = {key_field:key}
        
        _id = '%s_table' % model
        view =  ListView(model, rows_per_page=rows_per_page, 
            pageno=pageno, id=_id, fields_convert_map=fields_convert_map)
    else:
        _id = view.id
    
    if 'data' in request.values:
        if json_result:
            return json(view.json())
        else:
            result = view.run(head=False, body=True)
            return json(result)
    else:
        result = view.run(head=True, body=False)
        if isinstance(result, dict):
            if not layout:
                layout = request.GET.get('layout', 'layout.html')
            if not template:
                template = request.GET.get('template', 'generic_model_list.html')
            response.template = template
            
            data = data or {}
            result['layout'] = layout
            result['get_model_url'] = get_model_url
            result['table_id'] = _id
            result['add_button_text'] = add_button_text or _('Click here to add new object')
            if json_result:
                result['table'] = view
            result.update(data)
        return result
    
def generic_model_add(model=None, get_model_url=get_model_url, layout=None, 
    template=None, title=None, view=None, data=None):
    from uliweb.utils.generic import AddView
    from uliweb import request, error, response
    from uliweb.orm import get_model
    
    if not view:
        if not model: 
            model = request.GET.get('model', None)
        if not model or not get_model(model):
            return error("Can't find model [%s], please check it" % model)
        
        view = AddView(model, get_model_url('view'))
        
    result = view.run()
    if isinstance(result, dict):
        if not layout:
            layout = request.GET.get('layout', 'layout.html')
        if not template:
            template = request.GET.get('template', 'generic_model_add.html')
        response.template = template
        if not title:
            title = _("Add %s") % model
        data = data or {}
        result['layout'] = layout
        result['get_model_url'] = get_model_url
        result['title'] = title
        result.update(data)
    return result
    
def generic_model_view(model=None, id=None, get_model_url=get_model_url, layout=None, 
    template=None, title=None, view=None, data=None):
    from uliweb.utils.generic import DetailView
    import uliweb.orm as orm
    from uliweb import request, error, response
    
    if not view:
        if not model: 
            model = request.GET.get('model', None)
        Model = orm.get_model(model)
        if not model or not Model:
            return error("Can't find model [%s], please check it" % model)

        condition = (Model.c.id == int(id))
        
        view = DetailView(model, condition=condition)
        
    result = view.run()
    if isinstance(result, dict):
        if not layout:
            layout = request.GET.get('layout', 'layout.html')
        if not template:
            template = request.GET.get('template', 'generic_model_view.html')
        response.template = template
        if not title:
            title = _("Edit %s(#%d)") % (model, id)
        data = data or {}
        result['layout'] = layout
        result['get_model_url'] = get_model_url
        result['title'] = title
        result['obj_id'] = id
        result.update(data)
    return result
    
def generic_model_edit(model=None, id=None, get_model_url=get_model_url, layout=None, 
    template=None, title=None, view=None, data=None):
    from uliweb.utils.generic import EditView
    from uliweb import orm
    from uliweb import request, error, response
    
    if not view:
        if not model: 
            model = request.GET.get('model', None)
        Model = orm.get_model(model)
        if not model or not Model:
            return error("Can't find model [%s], please check it" % model)
        
        obj = Model.get(Model.c.id == int(id))
        view = EditView(model, get_model_url('view')(id), obj=obj)
        
    result = view.run()
    if isinstance(result, dict):
        if not layout:
            layout = request.GET.get('layout', 'layout.html')
        if not template:
            template = request.GET.get('template', 'generic_model_edit.html')
        response.template = template
        data = data or {}
        result['layout'] = layout
        result['get_model_url'] = get_model_url
        result['title'] = title
        result['obj_id'] = id
        result.update(data)
    return result
    
def generic_model_delete(model=None, id=None, get_model_url=get_model_url, view=None):
    from uliweb.utils.generic import DeleteView
    from uliweb import orm
    from uliweb import request
    
    if not view:
        if not model: 
            model = request.GET.get('model', None)
        Model = orm.get_model(model)
        obj = Model.get(Model.c.id == int(id))
        
        view = DeleteView(Model, get_model_url('list'), obj=obj)
        
    result = view.run()
    return result
    
    