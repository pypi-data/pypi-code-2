import math
from tw.api import Widget, lazystring as _

from rum import app

class Paginator(Widget):
    template = "genshi:tw.rum.templates.paginator"
    params = ["page_size", "radius"]
    css_class = "rum-paginator"
    page_size = None
    radius = 5

    def update_params(self, d):
        super(Paginator, self).update_params(d)
        query = d.value
        d.page_size = d.page_size or query.limit or 10
        offset = query.offset or 0
        d.num_pages = int(math.ceil((query.count / float(d.page_size))))
        d.page_num = min(d.num_pages-1, offset / d.page_size)
        lower = max(0, d.page_num - d.radius)
        upper = min(d.num_pages, d.page_num + d.radius)
        d.pages = range(lower, upper)
        def link_for_page(page_num):
            new_query = query.clone(offset=d.page_size*page_num,
                                    limit=d.page_size)
            if query.count:
                assert new_query.offset < query.count, `(new_query,query.count,d.pages)`
            kw=app.request.routes.get
            return app.url_for(action=kw('action'),
                resource=kw('resource'),
                remote_name=kw('remote_name',None),
                parent=kw('parent', None),
                parent_id=kw('parent_id', None),
                parent_obj = kw('parent_obj', None),
                **new_query.as_flat_dict())
        d.link_for_page = link_for_page
    
    def display(self, value, **kw):
        if value is None:
            return ''
        return super(Paginator, self).display(value, **kw)

    def render(self, value, **kw):
        if value is None:
            return ''
        return super(Paginator, self).render(value, **kw)
