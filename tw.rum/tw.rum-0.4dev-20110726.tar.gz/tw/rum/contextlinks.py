from tw.api import Widget, CSSLink, lazystring as _

from rum import app
from rum.genericfunctions import generic

class Link(object):
    """docstring for Link"""
    def __init__(self, name, label, url):
        super(Link, self).__init__()
        self.name = name
        self.label = label
        self.url = url
    def __unicode__(self):
        return url
        
class ContextLinks(Widget):
    params = ['routes']
    def _resource_name(self, routes):
         r_names, r_namep = app.names_for_resource(routes['resource'])
         return  app.translator.ugettext(r_names)
    @generic
    def gen_links(self, routes):
        pass
    @gen_links.when()
    def _gen_links_default(self, routes):
        return []
    def std_link(self, routes, name, new_name=None, resource_action=True):
        if new_name is None:
            new_name=name[:1].upper()+name[1:]
        args=dict(resource=routes['resource'], action=name)
        for k in ['parent_id', 'parent_obj', 'parent','remote_name','prefix','id']:
            v=routes.get(k, None)
            if v is not None:
                args[k]=v
        parent_id=routes.get('parent_id', None)
        parent=routes.get('parent', None)
        
        if resource_action:
            args.pop("id", None)

        return Link(name, _(new_name), app.url_for(**args))

    def index_link(self, routes):
        return self.std_link(routes, "index")

    def edit_link(self, routes):
        return self.std_link(routes, "edit", resource_action=False)

    def show_link(self, routes):
        return self.std_link(routes, "show", resource_action=False)

    def new_link(self, routes):
        return self.std_link(routes, "new", resource_action=True)

    @gen_links.when("routes['resource'] is not None")
    def _gen_links_res(self, routes):
        return [
            self.index_link(routes),
            self.new_link(routes)
        ]
    
    def delete_link(self, routes):
        return self.std_link(routes, 'confirm_delete',new_name='Delete', resource_action=False)
    
    @gen_links.when("routes['resource'] is not None and routes.get('id',None) is not None")
    def _gen_links_obj(self, routes):
        return [
                self.edit_link(routes),
                self.show_link(routes),
                self.index_link(routes),
                self.new_link(routes),
                self.delete_link(routes)
                ]
    
    def update_params(self, d):
        super(ContextLinks, self).update_params(d)
        routes = d.routes
        current_action=routes['action']
        d.links=[(l.label, l.url) 
            for l in 
            self.gen_links(routes) 
            if l.name!=current_action]
    template="genshi:tw.rum.templates.context_links"
    css=[CSSLink(modname="tw.rum", filename='static/context_links.css')]