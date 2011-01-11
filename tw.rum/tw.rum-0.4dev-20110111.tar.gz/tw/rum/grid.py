from genshi.input import HTML
from tw import framework
from tw.api import Link, CSSLink
from tw.forms import DataGrid
from tw.forms.datagrid import Column
from rum import app
from rum.query import asc, desc
from rum.fields import Number, ToOneRelation, RelatedField
from tw.dojo import dojo_js
from tw.api import JSLink
modname = "tw.rum"

grid_js = JSLink(
    modname=modname,
    filename='static/grid.js',
    javascript=[dojo_js]
)

class RumDataGrid(DataGrid):
    css_class = "rum-grid"
    css = [
        CSSLink(modname=modname, filename="static/grid.css"),
        CSSLink(modname=modname, filename="static/grid_print.css",
            media='print')
    ]
    javascript = [grid_js]
    actions = ["show", "edit", "confirm_delete"]
    params = ["actions", "icons", "query", "hidden_columns",
        "resource", "parent_resource", "remote_name", "parent_id"]
        
    #TODO use parent_id as param
    resource = None
    parent = None
    parent_id = None
    remote_name = None
    hidden_columns=[]
    icons = {
        'edit': Link(modname=modname, filename="static/pencil.png"),
        'show': Link(modname=modname, filename="static/pencil_go.png"),
        'confirm_delete': Link(modname=modname,
                               filename="static/pencil_delete.png"),
        }
    template="tw.rum.templates.datagrid"
    def __init__(self, *args, **kw):
        super(RumDataGrid, self).__init__(*args, **kw)
        self.fields.insert(0, (' ', self.row_links, dict(show_in_print=False)))

    def row_links(self, row):
        tpl = u'<a class="rum-grid-action rum-grid-%(action)s noprint" href="%(url)s" title="%(title)s">'\
              u'<img alt="%(title)s" src="%(src)s" /></a>'
        
        kw=app.request.routes.get
        # parent=self.parent_resource or kw('parent', None)
        # parent_id=self.parent_id or kw('parent_id', None)
        # remote_name=self.remote_name or kw('remote_name', None)
        
        parent=kw('parent', None)
        parent_id=kw('parent_id', None)
        remote_name=kw('remote_name', None)
        
        return HTML('<span class="rum-grid-action">' +''.join(tpl % {
            'url': app.url_for(
                obj=row, 
                parent_id=parent_id,
                parent=parent,
                remote_name=remote_name,
                action=action),
            'src': self.icons[action].link,
            'title': framework.translator(action),
            'action': action
            } for action in self.actions) +"</span>")



    
    def row_class(self, i, row):
        if i%2==1:
            return "odd"
        else:
            return "even"
    
    def update_params(self, d):
        super(RumDataGrid, self).update_params(d)
        query = d.query
        
        def add_column_classes(col, res):
            res.append(field_classifier(col))
            res.append(cell_visibility_class(col))
            res.append(column_print_class(col))
        
        def css_for_column_header(i, col):
            res=[]#["col_"+str(i)]
            if query and query.sort:
                first=query.sort[0]
                if first==asc(col.name):
                    res.append("rum-data-grid-asc")
                else:
                    if first==desc(col.name):
                        res.append("rum-data-grid-desc")
            add_column_classes(col, res)
            return " ".join(res)
        
        
        def joinable_column(col):
            if query is None:
                return False

            if not col.name in query.join:
                if 'field' in col.options:
                    col=col.options['field']
                    if isinstance(col, ToOneRelation) or\
                        (isinstance(col, RelatedField) and\
                        isinstance(col.real_field, ToOneRelation)):
                        return True
            return False
            
        def link_for_join(col):
            
            new_join=query.join+(col.name,)
            new_query = query.clone(join=new_join)
            kw=app.request.routes.get
            action=kw('action')
            resource=kw('resource')
            parent=kw('parent', None)
            parent_id=kw('parent_id', None)
            remote_name=kw('remote_name', None)
            return app.url_for(
                action=action,
                resource=resource,
                parent=parent,
                remote_name=remote_name,
                parent_id=parent_id,
                **new_query.as_flat_dict())
        def css_for_column_body(col):
            res=[]
            field=col.options.get("field", None)
            if isinstance(field, Number):
                data_class="number_field"
            else:
                data_class="normal_field"
            res.append(data_class)
            add_column_classes(col, res)
            return " ".join(res)
        def column_print_class(col):
            if not col.options.get('show_in_print', True):
                return "noprint"
            else:
                return ""
                
        def field_classifier(col):
            l=["named", "column", col.name]
            modifier=[]
            for r in [self.resource, self.parent_resource]:
                try:
                    modifier.append(r.__name__)
                except AttributeError:
                    pass
            if self.remote_name:
                modifier.append(self.remote_name)
            return "_".join(l)+"--"+"_".join(modifier)

                
        def link_for_sort_key(sort_key):
            if query.sort:
                old_sort=[c for c in query.sort if not c in [asc(sort_key),desc(sort_key)]]
            else:
                old_sort=[]
            prepend=asc(sort_key)
            if query.sort and query.sort[0]==asc(sort_key):
                prepend=desc(sort_key)
            new_sort=[prepend]+old_sort
            new_query = query.clone(sort=new_sort)
            kw=app.request.routes.get
            action=kw('action')
            resource=kw('resource')
            parent=kw('parent', None)
            parent_id=kw('parent_id', None)
            remote_name=kw('remote_name', None)
            return app.url_for(
                action=action,
                resource=resource,
                parent=parent,
                remote_name=remote_name,
                parent_id=parent_id,
                **new_query.as_flat_dict())
            
        def sortable_column(col, query):
            if query is None:
                return False
            if "field" in col.options:
                field=col.options["field"]
                return getattr(field, "sortable", False) 
            else:
                return False
        def shower_visibility_class(column):
            
            if column.name not in d.hidden_columns:
                return "hidden-column"
            else:
                return ""
        
        def cell_visibility_class(column):
            if column.name in d.hidden_columns:
                return "hidden-column"
            else:
                return ""
                
        field_classifier_by_name=dict()
        
        for c  in d.columns:
            field_classifier_by_name[c.name]=field_classifier(c)
        
        d.link_for_join = link_for_join
        d.joinable_column=joinable_column
        d.shower_visibility_class= shower_visibility_class
        d.cell_visibility_class = cell_visibility_class
        d.field_classifier_by_name = field_classifier_by_name    
        d.link_for_sort_key = link_for_sort_key
        d.css_for_column_header=css_for_column_header
        d.sortable_column=sortable_column
        d.css_for_column_body=css_for_column_body
        d.field_classifier = field_classifier
        d.row_class = self.row_class

        