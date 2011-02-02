import random
from pkg_resources import resource_filename
from unittest import TestCase
from turbojson.jsonify import jsonify
import rum
from rum import RumApp, Controller,  wsgiutil, app, exceptions
from rum.controller import formats, CRUDController
from rum.testutil import RumTestApp
from rum.tests import model
from rum.fields import FieldFactory, Field, Relation, ToOneRelation
from rum.query import Query 
FieldFactory.fields(model.Model, [Field('a', default=model.Model.a), Field('b', default=model.Model.b), Field('c', default=model.Model.c), ToOneRelation('d', other=model.Model, remote_name=None, default=None)])

jsonify.when("isinstance(obj, model.Model)")(lambda o: o.__dict__.copy())

class TestedController(Controller):
    def index(self):
        return 'index'

    def forbidden(self):
        raise wsgiutil.HTTPForbidden().exception

    def redirect(self):
        app.redirect_to('index')

    @formats("json")
    def get_json(self):
        return {'test':'foo'}
        
    def negotiate(self):
        self.template = 'test1'
        return {'item':'foo'}

class TestController(TestCase):
    def setUp(self):
        config = {
            'debug': True,
            'templating':{
                'search_path':[resource_filename('rum.tests','templates')],
                }
            }
        app = RumApp(config, finalize=False)
        app.router.connect('/test/', controller=TestedController, action='index')
        app.router.connect('/test/:action', controller=TestedController)
        app.finalize()
        self.app = RumTestApp(app)

    def test_root(self):
        self.app.get('/test/')

    def test_not_implemented(self):
        self.app.get('/test/foo', status=501)

    def test_can_raise_HTTPExceptions(self):
        self.app.get('/test/forbidden', status=403)

    def test_can_redirect(self):
        resp = self.app.get('/test/redirect').follow()
        self.failUnless('index' in resp, resp)

    def test_explicit_json(self):
        resp = self.app.get('/test/get_json')
        self.failUnlessEqual(resp.content_type, 'application/json')
        self.failUnlessEqual(resp.json, {'test':'foo'})
        
    def test_unsupported_media_type(self):
        resp = self.app.get('/test/get_json')
        self.failUnlessEqual(resp.content_type, 'application/json')
        self.failUnlessEqual(resp.json, {'test':'foo'})

    def test_content_negotiation_json(self):
        resp = self.app.get(
            '/test/negotiate',
            headers={'Accept': 'application/json'},
            )
        self.failUnlessEqual(resp.content_type, 'application/json')
        self.failUnlessEqual(resp.json, {'item':'foo'})

    def test_content_negotiation_html(self):
        resp = self.app.get(
            '/test/negotiate',
            headers={'Accept': 'text/html'},
            )
        self.failUnlessEqual(resp.content_type, 'text/html')

    def test_content_negotiation_unsupported(self):
        resp = self.app.get(
            '/test/negotiate',
            headers={'Accept': 'application/pdf'},
            )
        # Degrade to default format
        self.failUnlessEqual(resp.content_type, 'text/html')

    def test_content_ie6_negotiation_wildcard(self):
        resp = self.app.get(
            '/test/negotiate',
            headers={
                'Accept': '*/*',
                'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)'
                },
            )
        self.failUnlessEqual(resp.content_type, 'text/html')
    def test_sublass(self):
        class FooController(CRUDController):
            pass
        self.failUnlessEqual(FooController.error_handlers, CRUDController.error_handlers)
        self.failUnless(FooController.error_handlers is not CRUDController.error_handlers)


class TestCRUDController(TestCase):
    def setUp(self):
        config = {
            'rum.repositoryfactory': {
                'use': 'rum.tests.test_repository:DummyRepositoryFactory',
                'scan_modules': ['rum.tests.model'],
                },
            'rum.viewfactory': {
                'use': 'rum.tests.test_view:ModelViewFactory',
                },
            'rum.translator': {
                'use': 'default',
                'locales': ['en', 'es'],
                }
            }
        app = RumApp(config)
        rum.app._push_object(app)
        self.app = RumTestApp(app)

    def tearDown(self):
        rum.app._pop_object()
        model.clear_all()

class TestCRUDControllerCollection(TestCRUDController):
    def test_non_routeable(self):
        self.assertRaises(exceptions.RoutesException, app.url_for, model.Model,
                          action='generate_query')
        url = '/models/generate_query'
        self.app.get(url, status=400) # generate_query is interpreted as rsrc id

    def test_tw_resources_included(self):
        resp = self.app.get(app.url_for(model.Model, action='_meta'))
        self.failUnless(resp.html.findAll('link', type="text/css"), resp)

    def test_meta(self):
        resp = self.app.get(app.url_for(model.Model, action='_meta'))
        self.failUnlessEqual(resp.routes['action'], '_meta')
        self.failUnless('text/html' in resp.content_type)

    def test_meta_json(self):
        resp = self.app.get(app.url_for(model.Model, action='_meta', format='json'))
        self.failUnlessEqual(resp.routes['action'], '_meta')
        self.failUnlessEqual(resp.routes['format'], 'json')
        self.failUnless('application/json' in resp.content_type)
        self.failUnless('fields' in resp.json)

    def test_index(self):
        resp = self.app.get(app.url_for(model.Model))
        self.failUnlessEqual(resp.routes['action'], 'index')
        #self.failUnlessEqual(resp.routes['format'], 'html')
        self.failUnless('text/html' in resp.content_type)

    def test_index_json(self):
        resp = self.app.get(app.url_for(model.Model, format='json'))
        self.failUnlessEqual(resp.routes['action'], 'index')
        self.failUnlessEqual(resp.routes['format'], 'json')
        self.failUnless('application/json' in resp.content_type)
        self.failUnless('items' in resp.json, resp)

    def test_index_csv(self):
        resp = self.app.get(app.url_for(model.Model, format='csv'))
        self.failUnlessEqual(resp.routes['action'], 'index')
        self.failUnlessEqual(resp.routes['format'], 'csv')
        self.failUnless('text/csv' in resp.content_type)
    
    def test_index_query(self):
        query= Query(join=['d.d.d'])
        resp = self.app.get(app.url_for(model.Model, **query.as_flat_dict()))

    def test_create(self):
        data = dict(a='foo', b='bar')
        resp = self.app.post(app.url_for(model.Model), data)
        self.failUnless(300 <= resp.status_int < 400)
        resp.follow()

    def test_redirect_after_create(self):
        data = dict(
            a = 'foo',
            b = 'bar',
            _next_redirect = app.url_for(model.Model, action='index')
            )
        resp = self.app.post(app.url_for(model.Model), data)
        self.failUnless(300 <= resp.status_int < 400)
        resp = resp.follow()
        self.failUnless('index' in resp, resp)

    def test_create_bad_data(self):
        data = dict(a='foo', b='bar', c='i should be a number')
        resp = self.app.post(app.url_for(model.Model), data, status=400)
        self.failUnlessEqual(resp.routes['action'], 'new')
        #self.failUnlessEqual(resp.routes['format'], 'html')

    def test_new(self):
        resp = self.app.get(app.url_for(model.Model, action='new'))
        self.failUnlessEqual(resp.routes['action'], 'new')
        #self.failUnlessEqual(resp.routes['format'], 'html')
        self.failUnless('text/html' in resp.content_type, resp)

    def test_new_json(self):
        resp = self.app.get(app.url_for(model.Model, action='new', format='json'))
        self.failUnlessEqual(resp.routes['action'], 'new')
        self.failUnlessEqual(resp.routes['format'], 'json')
        self.failUnless('application/json' in resp.content_type)


    def test_preview(self):
        data = dict(a=1, b='fooobar')
        resp = self.app.post(app.url_for(model.Model, action='preview'), data)
        self.failUnlessEqual(resp.routes['action'], 'preview')
        #self.failUnlessEqual(resp.routes['format'], 'html')
        self.failUnless('text/html' in resp.content_type, resp)
        self.failUnless('fooobar' in resp)

    def test_preview_json(self):
        data = dict(a='baz', b='fooobar', c=4)
        resp = self.app.post(app.url_for(model.Model, action='preview',
                             format='json'), data)
        assert model.Model in app.resources                   
        self.failUnlessEqual(resp.routes['action'], 'preview')
        self.failUnlessEqual(resp.routes['format'], 'json')
        self.failUnless('application/json' in resp.content_type)
        preview_item = resp.json['item']
        self.failUnless(preview_item is not None, preview_item)
        for k in data.keys():
            self.failUnlessEqual(preview_item[k], data[k], preview_item)


class TestCRUDControllerMember(TestCRUDController):
    def setUp(self):
        super(TestCRUDControllerMember, self).setUp()
        self.ids = []
        for n in xrange(10):
            m = model.Model(number=n)
            m.save()
            self.ids.append(m.id)

    def tearDown(self):
        super(TestCRUDControllerMember, self).tearDown()
        del self.ids[:]

    def test_non_routeable(self):
        self.assertRaises(exceptions.RoutesException, app.url_for, model.Model,
                          action='generate_query')
        url = '/models/%s/generate_query' % self.ids[0]
        self.app.get(url, status=404)

    def test_show(self):
        id = str(self.ids[0])
        resp = self.app.get(app.url_for(model.Model, id=id))
        self.failUnlessEqual(resp.routes['action'], 'show')
        self.failUnlessEqual(resp.routes['id'], id)

    def test_show_with_lang(self):
        id = str(self.ids[0])
        url = app.url_for(model.Model, id=id, lang='es', format='html')
        resp = self.app.get(url)
        self.failUnlessEqual(resp.routes['action'], 'show')
        self.failUnlessEqual(resp.routes['id'], id)
        self.failUnlessEqual(resp.routes['lang'], 'es')

    def test_show_unsupported_lang(self):
        id = str(self.ids[0])
        url = app.url_for(model.Model, id=id, lang='fr', format='html')
        resp = self.app.get(url, status=404)

    def test_show_non_existent(self):
        while True:
            id = random.randint(1,1000)
            if id not in self.ids:
                break
        self.app.get(app.url_for(model.Model, id=id), status=404)

    def test_show_bad_id(self):
        self.app.get(app.url_for(model.Model, id='foobar'), status=400)

    def test_show_json(self):
        id = str(self.ids[0])
        url = app.url_for(model.Model, id=id, format='json')
        resp = self.app.get(url)
        self.failUnless('item' in resp.json)
        self.failUnlessEqual(resp.routes['action'], 'show')
        self.failUnlessEqual(resp.routes['format'], 'json')
        self.failUnlessEqual(resp.routes['id'], id)
        
    def test_edit(self):
        id = str(self.ids[0])
        resp = self.app.get(app.url_for(model.Model, id=id, action='edit'))
        self.failUnlessEqual(resp.routes['action'], 'edit')
        self.failUnlessEqual(resp.routes['id'], id)

    def test_edit_json(self):
        id = str(self.ids[0])
        resp = self.app.get(app.url_for(model.Model, id=id, format='json',
                                    action='edit'))
        self.failUnless('item' in resp.json)
        self.failUnlessEqual(resp.routes['action'], 'edit')
        self.failUnlessEqual(resp.routes['format'], 'json')
        self.failUnlessEqual(resp.routes['id'], id)

    def test_confirm_delete(self):
        id = str(self.ids[0])
        resp = self.app.get(app.url_for(model.Model, id=id,
                                    action='confirm_delete'))
        self.failUnlessEqual(resp.routes['action'], 'confirm_delete')
        self.failUnlessEqual(resp.routes['id'], id)

    def test_confirm_delete_json(self):
        id = str(self.ids[0])
        resp = self.app.get(app.url_for(model.Model, id=id, format='json',
                                    action='confirm_delete'))
        self.failUnless('item' in resp.json)
        self.failUnlessEqual(resp.routes['action'], 'confirm_delete')
        self.failUnlessEqual(resp.routes['format'], 'json')
        self.failUnlessEqual(resp.routes['id'], id)

    def test_update(self):
        data = dict(a='foo', b='bar')
        id = str(self.ids[0])
        resp = self.app.put(
            app.url_for(
                model.Model,
                id=id), data)
        self.failUnless(300 <= resp.status_int < 400)
        resp = resp.follow()
        self.failUnless('foo' in resp, resp)
    
    def test_redirect_after_update(self):
        data = dict(
            a = 'foo',
            b = 'bar',
            _next_redirect = app.url_for(model.Model, action='index')
            )
        id = str(self.ids[0])
        resp = self.app.put(app.url_for(model.Model, id=id), data)
        self.failUnless(300 <= resp.status_int < 400)
        resp = resp.follow()
        self.failUnless('index' in resp, resp)
    
    def test_update_with_mangled_method(self):
        data = dict(a='foo', b='bar', _method='put')
        id = str(self.ids[0])
        url= app.url_for(model.Model, id=id)
        resp = self.app.post(url, data)
        self.failUnless(300 <= resp.status_int < 400)
        resp = resp.follow()
        self.failUnless('foo' in resp, resp)

    def test_delete(self):
        id = str(self.ids[0])
        resp = self.app.delete(app.url_for(model.Model, id=id))
        self.failUnless(300 <= resp.status_int < 400)
        resp.follow()
        resp = self.app.get(app.url_for(model.Model, id=id), status=404)

    def test_redirect_after_delete(self):
        data = dict(_next_redirect = app.url_for(model.Model, action='index'))
        id = str(self.ids[0])
        resp = self.app.delete(app.url_for(model.Model, id=id), data)
        self.failUnless(300 <= resp.status_int < 400)
        resp = resp.follow()
        self.failUnless('index' in resp, resp)

    def test_delete_with_mangled_method(self):
        id = str(self.ids[0])
        resp = self.app.post(app.url_for(model.Model, id=id), {'_method':'delete'})
        self.failUnless(300 <= resp.status_int < 400)
        resp.follow()
        resp = self.app.get(app.url_for(model.Model, id=id), status=404)
