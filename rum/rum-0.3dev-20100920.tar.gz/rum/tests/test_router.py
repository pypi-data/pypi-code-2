from inspect import isclass
import webob
import unittest
from rum.router import RumRouter, DefaultController
from rum import RumApp
from rum import repository

class Basket(object):
    pass

class Vegetable(object):
    pass

class Potato(Vegetable):
    pass

class Onion(Vegetable):
    pass

repository.RepositoryFactory.set_names(Potato, "potato", "potatoes")

class TestRumRouter(unittest.TestCase):
    def setUp(self):
        self.app = RumApp(debug=True)
        self.r = self.app.router = RumRouter()
        self.ctx = self.app.mounted_at()
        self.ctx.__enter__()

    def tearDown(self):
        self.ctx.__exit__()
        
class TestRumRouterConnect(TestRumRouter):
    def test_simple_match(self):
        r = self.r
        class FooController: pass
        r.connect('foobars/:action', controller=FooController)
        m = r.match('/foobars/index')
        self.failUnless(m, repr(m))
        self.failUnless(m['controller'] is FooController)
        self.failUnlessEqual(m['action'], 'index')
        for k in r._route_args:
            self.failUnless(m[k] is None)

    def test_match_with_route_args(self):
        r = self.r
        class FooController: pass
        r.connect('potatoes/:action', controller=FooController, resource=Potato)
        r.connect('onions/:action', controller=FooController, resource=Onion)

        m = r.match('/potatoes/index')
        #appended index, as that test depended on the deprecated explict=False feature
        self.failUnless(m, repr(m))
        self.failUnless(m['controller'] is FooController)
        self.failUnless(m['resource'] is Potato)
        self.failUnlessEqual(m['action'], 'index')

        m = r.match('/onions/index')
        self.failUnless(m, repr(m))
        self.failUnless(m['controller'] is FooController)
        self.failUnless(m['resource'] is Onion)
        self.failUnlessEqual(m['action'], 'index')

    def test_url_for_with_route_args_and_default_controller(self):
        r = self.r
        r.connect('potatoes/:action', resource=Potato)
        r.connect('onions/:action', resource=Onion)

        url = r.url_for(Potato)
        self.failUnlessEqual(url, '/potatoes/index')
        #changed, no minimization any more
        
        url = r.url_for(Potato, action='edit')
        self.failUnlessEqual(url, '/potatoes/edit')

        m = r.match('/potatoes/index')
        self.failUnless(m, repr(m))
        self.failUnless(m['controller'] is DefaultController)

        url = r.url_for(resource=Onion)
        self.failUnlessEqual(url, '/onions/index')
        url = r.url_for(resource=Onion, action='edit')
        self.failUnlessEqual(url, '/onions/edit')

    def test_dispatch(self):
        r = self.r
        r.connect('potatoes', resource=Potato, conditions={'method':['GET']})
        r.connect('potatoes', resource=Potato, conditions={'method':['POST']},
                  action='create')
        # test GET
        req = webob.Request.blank('/potatoes', base_url='http://example.com/',
                                  method='GET')
        m = r.dispatch(req.environ)
        self.failUnless(m, repr(m))
        self.failUnlessEqual(m['action'], 'index')

        # test POST
        req = webob.Request.blank('/potatoes', base_url='http://example.com/',
                                  method='POST')
        m = r.dispatch(req.environ)
        self.failUnless(m, repr(m))
        self.failUnlessEqual(m['action'], 'create')

        # test POST via _method
        req = webob.Request.blank('/potatoes', base_url='http://example.com/')
        req.GET['_method'] = 'POST'
        m = r.dispatch(req.environ)
        self.failUnless(m, repr(m))
        self.failUnlessEqual(m['action'], 'create')

    #we do not support memory any more
    # def test_routes_memory(self):
    #     r = self.r
    #     r.connect('potatoes/:action', resource=Potato)
    #     r.connect('onions/:action', resource=Onion)
    # 
    #     req = webob.Request.blank('/potatoes', base_url='http://example.com',
    #                               method='GET')
    #     r.dispatch(req.environ)
    #     url = r.url_for(action='edit')
    #     self.failUnlessEqual(url, '/potatoes/edit')


class TestResource(TestRumRouter):
    def setUp(self):
        super(TestResource, self).setUp()
        self.r.resource(Potato)


class TestResourceUrlGen(TestResource):
    def test_index_create(self):
        self.failUnlessEqual(self.r.url_for(Potato), "/potatoes")
        self.failUnlessEqual(self.r.url_for(Potato, format='json'),
                             "/potatoes.json")
        self.failUnlessEqual(self.r.url_for(Potato, format='html', lang='es'),
                             "/potatoes.es.html")

    def test_new(self):
        self.failUnlessEqual(self.r.url_for(Potato, action='new'),
                             "/potatoes/new")
        self.failUnlessEqual(self.r.url_for(Potato, action='new',
                                            format='json'),
                             "/potatoes/new.json")
        self.failUnlessEqual(self.r.url_for(Potato, action='new', format='html',
                                            lang='es'),
                             "/potatoes/new.es.html")

    def test_preview(self):
        self.failUnlessEqual(self.r.url_for(Potato,
                                            action='preview'),
                             "/potatoes/preview")
        self.failUnlessEqual(self.r.url_for(Potato,
                                            action='preview', format='json'),
                             "/potatoes/preview.json")
        self.failUnlessEqual(self.r.url_for(Potato,
                                            action='preview', format='json',
                                            lang='es'),
                             "/potatoes/preview.es.json")


    def test_show_delete_update(self):
        self.failUnlessEqual(self.r.url_for(Potato, id=5),
                             "/potatoes/5")
        self.failUnlessEqual(self.r.url_for(Potato, id=5,
                                            format='json'),
                             "/potatoes/5.json")
        self.failUnlessEqual(self.r.url_for(Potato, id=5,
                                            format='json', lang='es'),
                             "/potatoes/5.es.json")


    def test_confirm_delete(self):
        self.failUnlessEqual(self.r.url_for(Potato, id=5,
                                            action='confirm_delete'),
                             "/potatoes/5/delete")
        self.failUnlessEqual(self.r.url_for(Potato, id=5,
                                            action='confirm_delete',
                                            format='json'),
                             "/potatoes/5/delete.json")
        self.failUnlessEqual(self.r.url_for(Potato, id=5,
                                            action='confirm_delete',
                                            format='json', lang='es'),
                             "/potatoes/5/delete.es.json")


    def test_edit(self):
        self.failUnlessEqual(self.r.url_for(Potato, id=5,
                                            action='edit'),
                             "/potatoes/5/edit")
        self.failUnlessEqual(self.r.url_for(Potato, id=5,
                                            action='edit', format='json'),
                             "/potatoes/5/edit.json")
        self.failUnlessEqual(self.r.url_for(Potato, id=5,
                                            action='edit', format='json',
                                            lang='es'),
                             "/potatoes/5/edit.es.json")


class TestResourceDispatch(TestResource):

    def test_index(self):
        req = webob.Request.blank('/potatoes', base_url='http://example.com/',
                                  method='GET')
        m = self.r.dispatch(req.environ)
        self.failUnless(m, repr(m))
        self.failUnlessEqual(m['resource'], Potato)
        self.failUnlessEqual(m['action'], 'index')
        self.failUnlessEqual(m['lang'], None)
    
    def test_index_json(self):
        req = webob.Request.blank('/potatoes.json',
                                  base_url='http://example.com/',
                                  method='GET')
        m = self.r.dispatch(req.environ)
        self.failUnless(m, repr(m))
        self.failUnlessEqual(m['resource'], Potato)
        self.failUnlessEqual(m['action'], 'index')
        self.failUnlessEqual(m['format'], 'json')
        self.failUnlessEqual(m['lang'], None)

    def test_create(self):
        req = webob.Request.blank('/potatoes', base_url='http://example.com/',
                                  method='POST')
        m = self.r.dispatch(req.environ)
        self.failUnless(m, repr(m))
        self.failUnlessEqual(m['resource'], Potato)
        self.failUnlessEqual(m['action'], 'create')
        self.failUnlessEqual(m['lang'], None)

    def test_new(self):
        req = webob.Request.blank('/potatoes/new',
                                  base_url='http://example.com/',
                                  method='GET')
        m = self.r.dispatch(req.environ)
        self.failUnless(m, repr(m))
        self.failUnlessEqual(m['resource'], Potato)
        self.failUnlessEqual(m['action'], 'new')
        self.failUnlessEqual(m['lang'], None)

    def test_preview(self):
        req = webob.Request.blank('/potatoes/preview',
                                  base_url='http://example.com/',
                                  method='POST')
        m = self.r.dispatch(req.environ)
        self.failUnless(m, repr(m))
        self.failUnlessEqual(m['resource'], Potato)
        self.failUnlessEqual(m['action'], 'preview')
        self.failUnlessEqual(m['lang'], None)

class TestResourceDispatchWithLang(TestResource):

    def test_index(self):
        req = webob.Request.blank('/potatoes.es.html',
                                  base_url='http://example.com/',
                                  method='GET')
        m = self.r.dispatch(req.environ)
        self.failUnless(m, repr(m))
        self.failUnlessEqual(m['resource'], Potato)
        self.failUnlessEqual(m['action'], 'index')
        self.failUnlessEqual(m['lang'], 'es')
    
    def test_create(self):
        req = webob.Request.blank('/potatoes.es.html',
                                  base_url='http://example.com/',
                                  method='POST')
        m = self.r.dispatch(req.environ)
        self.failUnless(m, repr(m))
        self.failUnlessEqual(m['resource'], Potato)
        self.failUnlessEqual(m['action'], 'create')
        self.failUnlessEqual(m['lang'], 'es')

    def test_new(self):
        req = webob.Request.blank('/potatoes/new.es.html',
                                  base_url='http://example.com/',
                                  method='GET')
        m = self.r.dispatch(req.environ)
        self.failUnless(m, repr(m))
        self.failUnlessEqual(m['resource'], Potato)
        self.failUnlessEqual(m['action'], 'new')
        self.failUnlessEqual(m['lang'], 'es')

    def test_preview(self):
        req = webob.Request.blank('/potatoes/preview.es.html',
                                  base_url='http://example.com/',
                                  method='POST')
        m = self.r.dispatch(req.environ)
        self.failUnless(m, repr(m))
        self.failUnlessEqual(m['resource'], Potato)
        self.failUnlessEqual(m['action'], 'preview')
        self.failUnlessEqual(m['lang'], 'es')

class TestResourceWithParent(TestRumRouter):
    def setUp(self):
        super(TestResourceWithParent, self).setUp()
        self.r.resource(Potato, parent=Onion)

class TestResourceWithParentUrlGen(TestResourceWithParent):
    def test_index_create(self):
        self.failUnlessEqual(self.r.url_for(Potato, parent=Onion, parent_id=5),
                             "/onions/5/potatoes")
        self.failUnlessEqual(self.r.url_for(Potato, parent=Onion, parent_id=5,
                                            format='json'),
                             "/onions/5/potatoes.json")

    def test_new(self):
        self.failUnlessEqual(self.r.url_for(Potato, parent=Onion, parent_id=5,
                                            action='new'),
                             "/onions/5/potatoes/new")
        self.failUnlessEqual(self.r.url_for(Potato, parent=Onion, parent_id=5,
                                            action='new', format='json'),
                             "/onions/5/potatoes/new.json")

    def test_preview(self):
        self.failUnlessEqual(self.r.url_for(Potato, parent=Onion, parent_id=5,
                                            action='preview'),
                             "/onions/5/potatoes/preview")
        self.failUnlessEqual(self.r.url_for(Potato, parent=Onion, parent_id=5,
                                            action='preview', format='json'),
                             "/onions/5/potatoes/preview.json")

    def test_show_delete_update(self):
        self.failUnlessEqual(self.r.url_for(Potato, id=15, parent=Onion,
                                            parent_id=5),
                             "/onions/5/potatoes/15")
        self.failUnlessEqual(self.r.url_for(Potato, id=15, parent=Onion,
                                            parent_id=5, format='json'),
                             "/onions/5/potatoes/15.json")

    def test_confirm_delete(self):
        self.failUnlessEqual(self.r.url_for(Potato, id=15, parent=Onion,
                                            parent_id=5,
                                            action='confirm_delete'),
                             "/onions/5/potatoes/15/delete")
        self.failUnlessEqual(self.r.url_for(Potato, id=15, parent=Onion,
                                            parent_id=5,
                                            action='confirm_delete',
                                            format='json'),
                             "/onions/5/potatoes/15/delete.json")

    def test_edit(self):
        self.failUnlessEqual(self.r.url_for(Potato, id=15, parent=Onion,
                                            parent_id=5, action='edit'),
                             "/onions/5/potatoes/15/edit")
        self.failUnlessEqual(self.r.url_for(Potato, id=15, parent=Onion,
                                            parent_id=5, action='edit',
                                            format='json'),
                             "/onions/5/potatoes/15/edit.json")

class TestResourceWithParentDispatch(TestResourceWithParent):

    def test_index(self):
        req = webob.Request.blank('/onions/6/potatoes',
                                  base_url='http://example.com/',
                                  method='GET')
        m = self.r.dispatch(req.environ)
        self.failUnless(m, repr(m))
        self.failUnlessEqual(m['parent'], Onion)
        self.failUnlessEqual(m['parent_id'], '6')
        self.failUnlessEqual(m['resource'], Potato)
        self.failUnlessEqual(m['action'], 'index')
    
    def test_index_json(self):
        req = webob.Request.blank('/onions/6/potatoes.json',
                                  base_url='http://example.com/',
                                  method='GET')
        m = self.r.dispatch(req.environ)
        self.failUnless(m, repr(m))
        self.failUnlessEqual(m['parent'], Onion)
        self.failUnlessEqual(m['parent_id'], '6')
        self.failUnlessEqual(m['resource'], Potato)
        self.failUnlessEqual(m['action'], 'index')
        self.failUnlessEqual(m['format'], 'json')

    def test_create(self):
        req = webob.Request.blank('/onions/6/potatoes',
                                  base_url='http://example.com/',
                                  method='POST')
        m = self.r.dispatch(req.environ)
        self.failUnless(m, repr(m))
        self.failUnlessEqual(m['parent'], Onion)
        self.failUnlessEqual(m['parent_id'], '6')
        self.failUnlessEqual(m['resource'], Potato)
        self.failUnlessEqual(m['action'], 'create')

    def test_new(self):
        req = webob.Request.blank('/onions/6/potatoes/new',
                                  base_url='http://example.com/',
                                  method='GET')
        m = self.r.dispatch(req.environ)
        self.failUnless(m, repr(m))
        self.failUnlessEqual(m['parent'], Onion)
        self.failUnlessEqual(m['parent_id'], '6')
        self.failUnlessEqual(m['resource'], Potato)
        self.failUnlessEqual(m['action'], 'new')

    def test_preview(self):
        req = webob.Request.blank('/onions/6/potatoes/preview',
                                  base_url='http://example.com/',
                                  method='POST')
        m = self.r.dispatch(req.environ)
        self.failUnless(m, repr(m))
        self.failUnlessEqual(m['parent'], Onion)
        self.failUnlessEqual(m['parent_id'], '6')
        self.failUnlessEqual(m['resource'], Potato)
        self.failUnlessEqual(m['action'], 'preview')

class TestResourceWithParentAndAttrUrlGen(TestRumRouter):
    def setUp(self):
        super(TestResourceWithParentAndAttrUrlGen, self).setUp()
        self.r.resource(Potato, parent=Onion, remote_name='mypotatoes')

    def test_index_create(self):
        self.failUnlessEqual(self.r.url_for(parent=Onion, remote_name='mypotatoes',
                                            parent_id=5),
                             "/onions/5/mypotatoes")
        self.failUnlessEqual(self.r.url_for(parent=Onion, parent_id=5,
                                            remote_name='mypotatoes',
                                            format='json'),
                             "/onions/5/mypotatoes.json")

    def test_new(self):
        self.failUnlessEqual(self.r.url_for(parent=Onion, parent_id=5,
                                            remote_name='mypotatoes',
                                            action='new'),
                             "/onions/5/mypotatoes/new")
        self.failUnlessEqual(self.r.url_for(parent=Onion, parent_id=5,
                                            remote_name='mypotatoes',
                                            action='new', format='json'),
                             "/onions/5/mypotatoes/new.json")

    def test_preview(self):
        self.failUnlessEqual(self.r.url_for(parent=Onion, parent_id=5,
                                            remote_name='mypotatoes',
                                            action='preview'),
                             "/onions/5/mypotatoes/preview")
        self.failUnlessEqual(self.r.url_for(parent=Onion, parent_id=5,
                                            remote_name='mypotatoes',
                                            action='preview', format='json'),
                             "/onions/5/mypotatoes/preview.json")

    def test_show_delete_update(self):
        self.failUnlessEqual(self.r.url_for(id=15, parent=Onion,
                                            remote_name='mypotatoes',
                                            parent_id=5),
                             "/onions/5/mypotatoes/15")
        self.failUnlessEqual(self.r.url_for(Potato, id=15, parent=Onion,
                                            remote_name='mypotatoes',
                                            parent_id=5, format='json'),
                             "/onions/5/mypotatoes/15.json")

    def test_confirm_delete(self):
        self.failUnlessEqual(self.r.url_for(id=15, parent=Onion,
                                            remote_name='mypotatoes',
                                            parent_id=5,
                                            action='confirm_delete'),
                             "/onions/5/mypotatoes/15/delete")
        self.failUnlessEqual(self.r.url_for(id=15, parent=Onion,
                                            remote_name='mypotatoes',
                                            parent_id=5,
                                            action='confirm_delete',
                                            format='json'),
                             "/onions/5/mypotatoes/15/delete.json")

    def test_edit(self):
        self.failUnlessEqual(self.r.url_for(id=15, parent=Onion,
                                            remote_name='mypotatoes',
                                            parent_id=5, action='edit'),
                             "/onions/5/mypotatoes/15/edit")
        self.failUnlessEqual(self.r.url_for(id=15, parent=Onion,
                                            remote_name='mypotatoes',
                                            parent_id=5, action='edit',
                                            format='json'),
                             "/onions/5/mypotatoes/15/edit.json")

class TestResourceWithParentAndAttrDispatch(TestRumRouter):
    def setUp(self):
        super(TestResourceWithParentAndAttrDispatch, self).setUp()
        self.r.resource(Potato, parent=Onion, remote_name='mypotatoes')

    def test_index(self):
        req = webob.Request.blank('/onions/6/mypotatoes',
                                  base_url='http://example.com/',
                                  method='GET')
        m = self.r.dispatch(req.environ)
        self.failUnless(m, repr(m))
        self.failUnlessEqual(m['parent'], Onion)
        self.failUnlessEqual(m['parent_id'], '6')
        self.failUnlessEqual(m['resource'], Potato)
        self.failUnlessEqual(m['action'], 'index')
        self.failUnlessEqual(m['remote_name'], 'mypotatoes')
    
    def test_index_json(self):
        req = webob.Request.blank('/onions/6/mypotatoes.json',
                                  base_url='http://example.com/',
                                  method='GET')
        m = self.r.dispatch(req.environ)
        self.failUnless(m, repr(m))
        self.failUnlessEqual(m['parent'], Onion)
        self.failUnlessEqual(m['parent_id'], '6')
        self.failUnlessEqual(m['resource'], Potato)
        self.failUnlessEqual(m['action'], 'index')
        self.failUnlessEqual(m['format'], 'json')
        self.failUnlessEqual(m['remote_name'], 'mypotatoes')

    def test_create(self):
        req = webob.Request.blank('/onions/6/mypotatoes',
                                  base_url='http://example.com/',
                                  method='POST')
        m = self.r.dispatch(req.environ)
        self.failUnless(m, repr(m))
        self.failUnlessEqual(m['parent'], Onion)
        self.failUnlessEqual(m['parent_id'], '6')
        self.failUnlessEqual(m['resource'], Potato)
        self.failUnlessEqual(m['action'], 'create')
        self.failUnlessEqual(m['remote_name'], 'mypotatoes')

    def test_new(self):
        req = webob.Request.blank('/onions/6/mypotatoes/new',
                                  base_url='http://example.com/',
                                  method='GET')
        m = self.r.dispatch(req.environ)
        self.failUnless(m, repr(m))
        self.failUnlessEqual(m['parent'], Onion)
        self.failUnlessEqual(m['parent_id'], '6')
        self.failUnlessEqual(m['resource'], Potato)
        self.failUnlessEqual(m['action'], 'new')
        self.failUnlessEqual(m['remote_name'], 'mypotatoes')

    def test_preview(self):
        req = webob.Request.blank('/onions/6/mypotatoes/preview',
                                  base_url='http://example.com/',
                                  method='POST')
        m = self.r.dispatch(req.environ)
        self.failUnless(m, repr(m))
        self.failUnlessEqual(m['parent'], Onion)
        self.failUnlessEqual(m['parent_id'], '6')
        self.failUnlessEqual(m['resource'], Potato)
        self.failUnlessEqual(m['action'], 'preview')
        self.failUnlessEqual(m['remote_name'], 'mypotatoes')

class TestResourceWithPrefix(TestRumRouter):
    def setUp(self):
        super(TestResourceWithPrefix, self).setUp()
        self.r.resource(Potato, prefix='admin')

class TestResourceWithPrefixUrlGen(TestResourceWithPrefix):
    def test_index_create(self):
        self.failUnlessEqual(self.r.url_for(Potato, prefix='admin'),
                             "/admin/potatoes")
        self.failUnlessEqual(self.r.url_for(Potato, prefix='admin',
                                            format='json'),
                             "/admin/potatoes.json")

    def test_new(self):
        self.failUnlessEqual(self.r.url_for(Potato, action='new',
                                            prefix='admin'),
                             "/admin/potatoes/new")
        self.failUnlessEqual(self.r.url_for(Potato, action='new',
                                            prefix='admin', format='json'),
                             "/admin/potatoes/new.json")

    def test_preview(self):
        self.failUnlessEqual(self.r.url_for(Potato, prefix='admin',
                                            action='preview'),
                             "/admin/potatoes/preview")
        self.failUnlessEqual(self.r.url_for(Potato, prefix='admin',
                                            action='preview', format='json'),
                             "/admin/potatoes/preview.json")

    def test_show_delete_update(self):
        self.failUnlessEqual(self.r.url_for(Potato, id=5, prefix='admin'),
                             "/admin/potatoes/5")
        self.failUnlessEqual(self.r.url_for(Potato, id=5, prefix='admin',
                                            format='json'),
                             "/admin/potatoes/5.json")

    def test_confirm_delete(self):
        self.failUnlessEqual(self.r.url_for(Potato, id=5, prefix='admin',
                                            action='confirm_delete'),
                             "/admin/potatoes/5/delete")
        self.failUnlessEqual(self.r.url_for(Potato, id=5, prefix='admin',
                                            action='confirm_delete',
                                            format='json'),
                             "/admin/potatoes/5/delete.json")

    def test_edit(self):
        self.failUnlessEqual(self.r.url_for(Potato, id=5, prefix='admin',
                                            action='edit'),
                             "/admin/potatoes/5/edit")
        self.failUnlessEqual(self.r.url_for(Potato, id=5, prefix='admin',
                                            action='edit', format='json'),
                             "/admin/potatoes/5/edit.json")

class TestResourceWithPrefixDispatch(TestResourceWithPrefix):

    def test_index(self):
        req = webob.Request.blank('/admin/potatoes',
                                  base_url='http://example.com/',
                                  method='GET')
        m = self.r.dispatch(req.environ)
        self.failUnless(m, repr(m))
        self.failUnlessEqual(m['resource'], Potato)
        self.failUnlessEqual(m['prefix'], 'admin')
        self.failUnlessEqual(m['action'], 'index')
    
    def test_index_json(self):
        req = webob.Request.blank('/admin/potatoes.json',
                                  base_url='http://example.com/',
                                  method='GET')
        m = self.r.dispatch(req.environ)
        self.failUnless(m, repr(m))
        self.failUnlessEqual(m['resource'], Potato)
        self.failUnlessEqual(m['prefix'], 'admin')
        self.failUnlessEqual(m['action'], 'index')
        self.failUnlessEqual(m['format'], 'json')

    def test_create(self):
        req = webob.Request.blank('/admin/potatoes',
                                  base_url='http://example.com/',
                                  method='POST')
        m = self.r.dispatch(req.environ)
        self.failUnless(m, repr(m))
        self.failUnlessEqual(m['resource'], Potato)
        self.failUnlessEqual(m['prefix'], 'admin')
        self.failUnlessEqual(m['action'], 'create')

    def test_new(self):
        req = webob.Request.blank('/admin/potatoes/new',
                                  base_url='http://example.com/',
                                  method='GET')
        m = self.r.dispatch(req.environ)
        self.failUnless(m, repr(m))
        self.failUnlessEqual(m['resource'], Potato)
        self.failUnlessEqual(m['prefix'], 'admin')
        self.failUnlessEqual(m['action'], 'new')

    def test_preview(self):
        req = webob.Request.blank('/admin/potatoes/preview',
                                  base_url='http://example.com/',
                                  method='POST')
        m = self.r.dispatch(req.environ)
        self.failUnless(m, repr(m))
        self.failUnlessEqual(m['resource'], Potato)
        self.failUnlessEqual(m['prefix'], 'admin')
        self.failUnlessEqual(m['action'], 'preview')


class TestResourceWithParentAndPrefix(TestRumRouter):
    def setUp(self):
        super(TestResourceWithParentAndPrefix, self).setUp()
        self.r.resource(Potato, parent=Onion, prefix='admin')

class TestResourceWithParentAndPrefixUrlGen(TestResourceWithParentAndPrefix):
    def test_index_create(self):
        self.failUnlessEqual(self.r.url_for(Potato, parent=Onion, parent_id=5,
                                            prefix='admin'),
                             "/admin/onions/5/potatoes")
        self.failUnlessEqual(self.r.url_for(Potato, parent=Onion, parent_id=5,
                                            format='json', prefix='admin'),
                             "/admin/onions/5/potatoes.json")

    def test_new(self):
        self.failUnlessEqual(self.r.url_for(Potato, parent=Onion, parent_id=5,
                                            action='new', prefix='admin'),
                             "/admin/onions/5/potatoes/new")
        self.failUnlessEqual(self.r.url_for(Potato, parent=Onion, parent_id=5,
                                            action='new', format='json',
                                            prefix='admin'),
                             "/admin/onions/5/potatoes/new.json")

    def test_preview(self):
        self.failUnlessEqual(self.r.url_for(Potato, parent=Onion, parent_id=5,
                                            action='preview', prefix='admin'),
                             "/admin/onions/5/potatoes/preview")
        self.failUnlessEqual(self.r.url_for(Potato, parent=Onion, parent_id=5,
                                            action='preview', format='json',
                                            prefix='admin'),
                             "/admin/onions/5/potatoes/preview.json")

    def test_show_delete_update(self):
        self.failUnlessEqual(self.r.url_for(Potato, id=15, parent=Onion,
                                            parent_id=5, prefix='admin'),
                             "/admin/onions/5/potatoes/15")
        self.failUnlessEqual(self.r.url_for(Potato, id=15, parent=Onion,
                                            parent_id=5, format='json',
                                            prefix='admin'),
                             "/admin/onions/5/potatoes/15.json")

    def test_confirm_delete(self):
        self.failUnlessEqual(self.r.url_for(Potato, id=15, parent=Onion,
                                            parent_id=5, prefix='admin',
                                            action='confirm_delete'),
                             "/admin/onions/5/potatoes/15/delete")
        self.failUnlessEqual(self.r.url_for(Potato, id=15, parent=Onion,
                                            parent_id=5, prefix='admin',
                                            action='confirm_delete',
                                            format='json'),
                             "/admin/onions/5/potatoes/15/delete.json")

    def test_edit(self):
        self.failUnlessEqual(self.r.url_for(Potato, id=15, parent=Onion,
                                            parent_id=5, action='edit',
                                            prefix='admin'),
                             "/admin/onions/5/potatoes/15/edit")
        self.failUnlessEqual(self.r.url_for(Potato, id=15, parent=Onion,
                                            parent_id=5, action='edit',
                                            format='json',
                                            prefix='admin'),
                             "/admin/onions/5/potatoes/15/edit.json")

class TestResourceWithParentAndPrefixDispatch(TestResourceWithParentAndPrefix):

    def test_index(self):
        req = webob.Request.blank('/admin/onions/6/potatoes',
                                  base_url='http://example.com/',
                                  method='GET')
        m = self.r.dispatch(req.environ)
        self.failUnless(m, repr(m))
        self.failUnlessEqual(m['parent'], Onion)
        self.failUnlessEqual(m['parent_id'], '6')
        self.failUnlessEqual(m['prefix'], 'admin')
        self.failUnlessEqual(m['resource'], Potato)
        self.failUnlessEqual(m['action'], 'index')
    
    def test_index_json(self):
        req = webob.Request.blank('/admin/onions/6/potatoes.json',
                                  base_url='http://example.com/',
                                  method='GET')
        m = self.r.dispatch(req.environ)
        self.failUnless(m, repr(m))
        self.failUnlessEqual(m['parent'], Onion)
        self.failUnlessEqual(m['parent_id'], '6')
        self.failUnlessEqual(m['resource'], Potato)
        self.failUnlessEqual(m['prefix'], 'admin')
        self.failUnlessEqual(m['action'], 'index')
        self.failUnlessEqual(m['format'], 'json')

    def test_create(self):
        req = webob.Request.blank('/admin/onions/6/potatoes',
                                  base_url='http://example.com/',
                                  method='POST')
        m = self.r.dispatch(req.environ)
        self.failUnless(m, repr(m))
        self.failUnlessEqual(m['parent'], Onion)
        self.failUnlessEqual(m['parent_id'], '6')
        self.failUnlessEqual(m['prefix'], 'admin')
        self.failUnlessEqual(m['resource'], Potato)
        self.failUnlessEqual(m['action'], 'create')

    def test_new(self):
        req = webob.Request.blank('/admin/onions/6/potatoes/new',
                                  base_url='http://example.com/',
                                  method='GET')
        m = self.r.dispatch(req.environ)
        self.failUnless(m, repr(m))
        self.failUnlessEqual(m['parent'], Onion)
        self.failUnlessEqual(m['parent_id'], '6')
        self.failUnlessEqual(m['prefix'], 'admin')
        self.failUnlessEqual(m['resource'], Potato)
        self.failUnlessEqual(m['action'], 'new')

    def test_preview(self):
        req = webob.Request.blank('/admin/onions/6/potatoes/preview',
                                  base_url='http://example.com/',
                                  method='POST')
        m = self.r.dispatch(req.environ)
        self.failUnless(m, repr(m))
        self.failUnlessEqual(m['parent'], Onion)
        self.failUnlessEqual(m['prefix'], 'admin')
        self.failUnlessEqual(m['parent_id'], '6')
        self.failUnlessEqual(m['resource'], Potato)
        self.failUnlessEqual(m['action'], 'preview')

class TestResourceSubclassesWithParent(TestRumRouter):
    def setUp(self):
        super(TestResourceSubclassesWithParent, self).setUp()
        self.r.resource(Vegetable, parent=Basket)

    def test_show_delete_update(self):
        self.failUnlessEqual(
            self.r.url_for(Potato, id=15, parent=Basket, parent_id=5),
            #introduced remote_name argument, rum should not guess
            "/baskets/5/vegetables/15"
            )
        self.failUnlessEqual(
            self.r.url_for(
                Potato, id=15, parent=Basket, parent_id=5, format='json'
                ),
            "/baskets/5/vegetables/15.json"
            )

    def test_confirm_delete(self):
        self.failUnlessEqual(
            self.r.url_for(
                Potato, id=15, parent=Basket, parent_id=5,
                action='confirm_delete'
                ),
            "/baskets/5/vegetables/15/delete"
            )
        self.failUnlessEqual(
            self.r.url_for(
                Potato, id=15, parent=Basket, parent_id=5,
                action='confirm_delete', format='json'
                ),
            "/baskets/5/vegetables/15/delete.json"
            )

    def test_edit(self):
        self.failUnlessEqual(
            self.r.url_for(
                Potato, id=15, parent=Basket, parent_id=5, action='edit'
                ),
            "/baskets/5/vegetables/15/edit"
            )
        self.failUnlessEqual(
            self.r.url_for(
                Potato, id=15, parent=Basket, parent_id=5, action='edit',
                format='json'
                ),
            "/baskets/5/vegetables/15/edit.json"
            )

if __name__ == '__main__':
    import logging, sys
    logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)
    unittest.main()

