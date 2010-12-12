from tg import expose, flash, require, request, redirect, tmpl_context, TGController, config, validate, url
from tg.controllers import WSGIAppController
import libacr

from webob.exc import HTTPFound
from libacr.views.manager import ViewsManager
import ConfigParser, StringIO
from libacr.model.core import DBSession
from libacr.controllers.admin.base import BaseAdminController
from libacr.plugins.base import AdminEntry, AcrPlugin, plugin_expose
from libacr.model.content import Tag, Page, Slice, Content, ContentData
from libacr.controllers.admin.base import _create_node
from repoze.what import predicates
from tw.api import WidgetsList
import tw.forms as twf
from formencode import validators
from datetime import datetime
from sqlalchemy import join, desc

class AddUploadableContentForm(WidgetsList):
    document = twf.FileField(label_text="File:", validator=validators.FieldStorageUploadConverter(not_empty=True))
    filter_tag = twf.HiddenField()
    path = twf.HiddenField()
    page_uid = twf.HiddenField()

class AddSimpleContentForm(WidgetsList):
    filter_tag = twf.HiddenField()
    page_uid = twf.HiddenField()

class SimpleSliceGroupAdminController(BaseAdminController):
    @plugin_expose('add')
    @require(predicates.not_anonymous())
    def add(self, *args, **kw):
        page_uid = kw['page_uid']
        view = kw['view']
        filter_tag = kw['filter_tag']

        if view in (v.name for v in ViewsManager.rdisk_views):
            BaseForm = AddUploadableContentForm
            form_action = libacr.lib.url('/plugins/sgadmin/upload')
        else:
            BaseForm = AddSimpleContentForm
            form_action = libacr.lib.url('/plugins/sgadmin/save')

        kw['path'] = '/' + filter_tag + '_' + view
        return dict(view=view, filter_tag=filter_tag, values=kw,
                    form=ViewsManager.create_form(view, BaseForm),
                    form_action=form_action)

    @plugin_expose('del')
    @require(predicates.not_anonymous())
    def delete(self, page_uid, view, filter_tag, *args, **kw):
        slices = DBSession.query(Slice).join(Content).\
                           filter(Slice.tags.any(name=filter_tag)).\
                           order_by(desc(Slice.uid))

        view_instance = ViewsManager.find_view(view)
        return dict(view=view, filter_tag=filter_tag,
                    page_uid=page_uid, slices=slices,
                    view_instance=view_instance)

    @expose()
    @validate(ViewsManager.validator(AddSimpleContentForm), error_handler=add)
    @require(predicates.not_anonymous())
    def save(self, *args, **kw):
        slice_data = {}
        slice_data['name'] = kw['filter_tag'] + '_' + datetime.now().strftime('%y%m%d%H%M%S')
        slice_data['page'] = None
        slice_data['zone'] = 'main'
        slice_data['order'] = 0
        slice_data['tags'] = [kw['filter_tag']]
        slice_data['view'] = kw['view']
        slice_data['data'] = ViewsManager.encode(kw['view'], kw)
        slice_data['skip_permission'] = True
        _create_node(**slice_data)

        page = DBSession.query(Page).get(kw['page_uid'])
        return redirect(page.url)

    @expose()
    @validate(ViewsManager.validator(AddUploadableContentForm), error_handler=add)
    @require(predicates.not_anonymous())
    def upload(self, *args, **kw):
        from libacr.controllers.rdisk import RDiskController
        rd = RDiskController()
        try:
            real_groups = request.environ['repoze.what.credentials']['groups'] 
            request.environ['repoze.what.credentials']['groups'] = real_groups + ('acr',)
            rd.add_res(kw.pop('document'), kw.pop('path'), kw.pop('view'), None, [kw['filter_tag']], **kw)
            request.environ['repoze.what.credentials']['groups'] = real_groups
        except HTTPFound:
            pass

        page = DBSession.query(Page).get(kw['page_uid'])
        return redirect(page.url)

    @expose()
    @require(predicates.not_anonymous())
    def drop(self, page_uid, slice_uid, *args, **kw):
        slice = DBSession.query(Slice).get(slice_uid)
        DBSession.delete(slice)
        page = DBSession.query(Page).get(page_uid)
        return redirect(page.url)

class SliceGroupAdminRenderer(object):

    def __init__(self):
        self.name = 'slicegroup_admin'
        self.form_fields = [twf.SingleSelectField('filter_tag', label_text="Filter Tag:",
                                                        validator=twf.validators.String(not_empty=True, strip=True),
                                                        options=lambda : (p.name for p in DBSession.query(Tag))),
                            twf.SingleSelectField('view_type', label_text="Members View:", default='html',
                                                        validator=twf.validators.String(not_empty=True, strip=True),
                                                        options=lambda : ViewsManager.view_names())]
        self.exposed = True

    def to_dict(self, data):
        config = ConfigParser.ConfigParser({'view_type':'html'})
        config.readfp(StringIO.StringIO(data))

        view_type = config.get('sgadmin', 'view_type')
        filter_tag = config.get('sgadmin', 'filter_tag')

        return {'view_type' : view_type and view_type or 'html',
                'filter_tag': filter_tag}
    
    def from_dict(self, dic):
        config = ConfigParser.ConfigParser()
        config.add_section('sgadmin')
        config.set('sgadmin', 'filter_tag', dic.get('filter_tag', 'gallery'))
        config.set('sgadmin', 'view_type', dic.get('view_type', 'html'))        

        s = StringIO.StringIO()
        config.write(s)
        return s.getvalue()

    def preview(self, page, slice, data):
        return 'Preview not Implemented'

    def render(self, page, slice, data):
        from libacr.plugins.manager import PluginsManager

        data = self.to_dict(data)
        data['add_url'] = url(PluginsManager['sgadmin'].plugin_url('add'),
                              params=dict(page_uid=str(page.uid), view=data['view_type'],
                                          filter_tag=data['filter_tag']))
        data['del_url'] = url(PluginsManager['sgadmin'].plugin_url('delete'),
                              params=dict(page_uid=str(page.uid), view=data['view_type'],
                                          filter_tag=data['filter_tag']))

        if request.identity:
            result = '''
<div class="acr_group_admin_%(filter_tag)s">
    <a href="%(add_url)s">Add</a>
    <a href="%(del_url)s">Remove</a>
</div>
''' % data
        else:
            result = ''

        return result

class SliceGroupAdminPlugin(AcrPlugin):
    uri = 'sgadmin'

    def __init__(self):
        self.controller = SimpleSliceGroupAdminController()
        ViewsManager.register_view(SliceGroupAdminRenderer())
