import unittest

from repoze.bfg.testing import cleanUp
from repoze.bfg import testing

class TestTemplateRendererFactory(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()
        
    def _callFUT(self, path, factory):
        from repoze.bfg.renderers import template_renderer_factory
        return template_renderer_factory(path, factory)

    def test_abspath_notfound(self):
        from repoze.bfg.interfaces import ITemplateRenderer
        abspath = '/wont/exist'
        testing.registerUtility({}, ITemplateRenderer, name=abspath)
        self.assertRaises(ValueError, self._callFUT, abspath, None)

    def test_abspath_alreadyregistered(self):
        from repoze.bfg.interfaces import ITemplateRenderer
        import os
        abspath = os.path.abspath(__file__)
        renderer = {}
        testing.registerUtility(renderer, ITemplateRenderer, name=abspath)
        result = self._callFUT(abspath, None)
        self.failUnless(result is renderer)

    def test_abspath_notyetregistered(self):
        from repoze.bfg.interfaces import ITemplateRenderer
        import os
        abspath = os.path.abspath(__file__)
        renderer = {}
        testing.registerUtility(renderer, ITemplateRenderer, name=abspath)
        result = self._callFUT(abspath, None)
        self.failUnless(result is renderer)

    def test_relpath_path_registered(self):
        renderer = {}
        from repoze.bfg.interfaces import ITemplateRenderer
        testing.registerUtility(renderer, ITemplateRenderer, name='foo/bar')
        result = self._callFUT('foo/bar', None)
        self.failUnless(renderer is result)

    def test_relpath_is_package_registered(self):
        renderer = {}
        from repoze.bfg.interfaces import ITemplateRenderer
        testing.registerUtility(renderer, ITemplateRenderer, name='foo:bar/baz')
        result = self._callFUT('foo:bar/baz', None)
        self.failUnless(renderer is result)

    def test_spec_notfound(self):
        self.assertRaises(ValueError, self._callFUT,
                          'repoze.bfg.tests:wont/exist', None)

    def test_spec_alreadyregistered(self):
        from repoze.bfg.interfaces import ITemplateRenderer
        from repoze.bfg import tests
        module_name = tests.__name__
        relpath = 'test_renderers.py'
        spec = '%s:%s' % (module_name, relpath)
        renderer = {}
        testing.registerUtility(renderer, ITemplateRenderer, name=spec)
        result = self._callFUT(spec, None)
        self.failUnless(result is renderer)

    def test_spec_notyetregistered(self):
        import os
        from repoze.bfg import tests
        module_name = tests.__name__
        relpath = 'test_renderers.py'
        renderer = {}
        factory = DummyFactory(renderer)
        spec = '%s:%s' % (module_name, relpath)
        result = self._callFUT(spec, factory)
        self.failUnless(result is renderer)
        path = os.path.abspath(__file__)
        if path.endswith('pyc'): # pragma: no cover
            path = path[:-1]
        self.assertEqual(factory.path, path)
        self.assertEqual(factory.kw, {})

    def test_reload_resources_true(self):
        from repoze.bfg.threadlocal import get_current_registry
        from repoze.bfg.interfaces import ISettings
        from repoze.bfg.interfaces import ITemplateRenderer
        settings = {'reload_resources':True}
        testing.registerUtility(settings, ISettings)
        renderer = {}
        factory = DummyFactory(renderer)
        result = self._callFUT('repoze.bfg.tests:test_renderers.py', factory)
        self.failUnless(result is renderer)
        spec = '%s:%s' % ('repoze.bfg.tests', 'test_renderers.py')
        reg = get_current_registry()
        self.assertEqual(reg.queryUtility(ITemplateRenderer, name=spec),
                         None)

    def test_reload_resources_false(self):
        from repoze.bfg.threadlocal import get_current_registry
        from repoze.bfg.interfaces import ISettings
        from repoze.bfg.interfaces import ITemplateRenderer
        settings = {'reload_resources':False}
        testing.registerUtility(settings, ISettings)
        renderer = {}
        factory = DummyFactory(renderer)
        result = self._callFUT('repoze.bfg.tests:test_renderers.py', factory)
        self.failUnless(result is renderer)
        spec = '%s:%s' % ('repoze.bfg.tests', 'test_renderers.py')
        reg = get_current_registry()
        self.assertNotEqual(reg.queryUtility(ITemplateRenderer, name=spec),
                            None)

class TestRendererFromName(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()
        
    def _callFUT(self, path, package=None):
        from repoze.bfg.renderers import renderer_from_name
        return renderer_from_name(path, package)

    def test_it(self):
        from repoze.bfg.interfaces import IRendererFactory
        import os
        here = os.path.dirname(os.path.abspath(__file__))
        fixture = os.path.join(here, 'fixtures/minimal.pt')
        def factory(path, **kw):
            return path
        testing.registerUtility(factory, IRendererFactory, name='.pt')
        result = self._callFUT(fixture)
        self.assertEqual(result, fixture)

    def test_with_package(self):
        from repoze.bfg.interfaces import IRendererFactory
        def factory(path, **kw):
            return path
        testing.registerUtility(factory, IRendererFactory, name='.pt')
        import repoze.bfg.tests
        result = self._callFUT('fixtures/minimal.pt', repoze.bfg.tests)
        self.assertEqual(result, 'repoze.bfg.tests:fixtures/minimal.pt')

    def test_it_no_renderer(self):
        self.assertRaises(ValueError, self._callFUT, 'foo')
        

class Test_json_renderer_factory(unittest.TestCase):
    def _callFUT(self, name):
        from repoze.bfg.renderers import json_renderer_factory
        return json_renderer_factory(name)

    def test_it(self):
        renderer = self._callFUT(None)
        result = renderer({'a':1}, {})
        self.assertEqual(result, '{"a": 1}')

    def test_with_request_content_type_notset(self):
        request = testing.DummyRequest()
        renderer = self._callFUT(None)
        renderer({'a':1}, {'request':request})
        self.assertEqual(request.response_content_type, 'application/json')

    def test_with_request_content_type_set(self):
        request = testing.DummyRequest()
        request.response_content_type = 'text/mishmash'
        renderer = self._callFUT(None)
        renderer({'a':1}, {'request':request})
        self.assertEqual(request.response_content_type, 'text/mishmash')

class Test_string_renderer_factory(unittest.TestCase):
    def _callFUT(self, name):
        from repoze.bfg.renderers import string_renderer_factory
        return string_renderer_factory(name)

    def test_it_unicode(self):
        renderer = self._callFUT(None)
        value = unicode('La Pe\xc3\xb1a', 'utf-8')
        result = renderer(value, {})
        self.assertEqual(result, value)
                          
    def test_it_str(self):
        renderer = self._callFUT(None)
        value = 'La Pe\xc3\xb1a'
        result = renderer(value, {})
        self.assertEqual(result, value)

    def test_it_other(self):
        renderer = self._callFUT(None)
        value = None
        result = renderer(value, {})
        self.assertEqual(result, 'None')

    def test_with_request_content_type_notset(self):
        request = testing.DummyRequest()
        renderer = self._callFUT(None)
        renderer(None, {'request':request})
        self.assertEqual(request.response_content_type, 'text/plain')

    def test_with_request_content_type_set(self):
        request = testing.DummyRequest()
        request.response_content_type = 'text/mishmash'
        renderer = self._callFUT(None)
        renderer(None, {'request':request})
        self.assertEqual(request.response_content_type, 'text/mishmash')

class Test_rendered_response(unittest.TestCase):
    def setUp(self):
        testing.setUp()
        from zope.deprecation import __show__
        __show__.off()

    def tearDown(self):
        testing.tearDown()
        from zope.deprecation import __show__
        __show__.on()

    def _callFUT(self, renderer, response, view=None,
                 context=None, request=None, renderer_name=None):
        from repoze.bfg.renderers import rendered_response
        if request is None:
            request = testing.DummyRequest()
        return rendered_response(renderer, response, view,
                                 context, request, renderer_name)

    def _makeRenderer(self):
        def renderer(*arg):
            return 'Hello!'
        return renderer

    def test_is_response(self):
        renderer = self._makeRenderer()
        response = DummyResponse()
        result = self._callFUT(renderer, response)
        self.assertEqual(result, response)

    def test_calls_renderer(self):
        renderer = self._makeRenderer()
        response = {'a':'1'}
        result = self._callFUT(renderer, response)
        self.assertEqual(result.body, 'Hello!')


class TestRendererHelper(unittest.TestCase):
    def setUp(self):
        self.config = cleanUp()

    def tearDown(self):
        cleanUp()

    def _makeOne(self, *arg, **kw):
        from repoze.bfg.renderers import RendererHelper
        return RendererHelper(*arg, **kw)

    def _registerRendererFactory(self):
        from repoze.bfg.interfaces import IRendererFactory
        def renderer(*arg):
            def respond(*arg):
                return arg
            return respond
        self.config.registry.registerUtility(renderer, IRendererFactory,
                                             name='.foo')
        return renderer

    def test_resolve_spec_path_is_None(self):
        helper = self._makeOne('loo.foo')
        result = helper.resolve_spec(None)
        self.assertEqual(result, None)

    def test_resolve_spec_package_is_None(self):
        helper = self._makeOne('loo.foo')
        result = helper.resolve_spec('/foo/bar')
        self.assertEqual(result, '/foo/bar')

    def test_resolve_spec_absolute(self):
        helper = self._makeOne('loo.foo')
        result = helper.resolve_spec('repoze.bfg:flub')
        self.assertEqual(result, 'repoze.bfg:flub')

    def test_resolve_spec_relative(self):
        helper = self._makeOne('loo.foo', package='repoze.bfg')
        result = helper.resolve_spec('flub')
        self.assertEqual(result, 'repoze.bfg:flub')

    def test_render_to_response(self):
        self._registerRendererFactory()
        request = Dummy()
        helper = self._makeOne('loo.foo')
        response = helper.render_to_response('values', 'system_values',
                                             request=request)
        self.assertEqual(response.body, ('values', 'system_values'))

    def test_render_explicit_registry(self):
        factory = self._registerRendererFactory()
        class DummyRegistry(object):
            def __init__(self):
                self.responses = [factory, lambda *arg: {}]
            def queryUtility(self, iface, name=None):
                self.queried = True
                return self.responses.pop(0)
        reg = DummyRegistry()
        helper = self._makeOne('loo.foo', registry=reg)
        result = helper.render('value', {})
        self.assertEqual(result, ('value', {}))
        self.failUnless(reg.queried)

    def test_render_system_values_is_None(self):
        self._registerRendererFactory()
        request = Dummy()
        context = Dummy()
        request.context = context
        helper = self._makeOne('loo.foo')
        result = helper.render('values', None, request=request)
        system = {'request':request, 'context':context,
                  'renderer_name':'loo.foo', 'view':None}
        self.assertEqual(result, ('values', system))

    def test_render_renderer_globals_factory_active(self):
        self._registerRendererFactory()
        from repoze.bfg.interfaces import IRendererGlobalsFactory
        def rg(system):
            return {'a':1}
        self.config.registry.registerUtility(rg, IRendererGlobalsFactory)
        helper = self._makeOne('loo.foo')
        result = helper.render('values', None)
        self.assertEqual(result[1]['a'], 1)

    def test__make_response_with_content_type(self):
        request = testing.DummyRequest()
        attrs = {'response_content_type':'text/nonsense'}
        request.__dict__.update(attrs)
        helper = self._makeOne('loo.foo')
        response = helper._make_response('abc', request)
        self.assertEqual(response.content_type, 'text/nonsense')
        self.assertEqual(response.body, 'abc')

    def test__make_response_with_headerlist(self):
        request = testing.DummyRequest()
        attrs = {'response_headerlist':[('a', '1'), ('b', '2')]}
        request.__dict__.update(attrs)
        helper = self._makeOne('loo.foo')
        response = helper._make_response('abc', request)
        self.assertEqual(response.headerlist,
                         [('Content-Type', 'text/html; charset=UTF-8'),
                          ('Content-Length', '3'),
                          ('a', '1'),
                          ('b', '2')])
        self.assertEqual(response.body, 'abc')

    def test__make_response_with_status(self):
        request = testing.DummyRequest()
        attrs = {'response_status':'406 You Lose'}
        request.__dict__.update(attrs)
        helper = self._makeOne('loo.foo')
        response = helper._make_response('abc', request)
        self.assertEqual(response.status, '406 You Lose')
        self.assertEqual(response.body, 'abc')

    def test__make_response_with_charset(self):
        request = testing.DummyRequest()
        attrs = {'response_charset':'UTF-16'}
        request.__dict__.update(attrs)
        helper = self._makeOne('loo.foo')
        response = helper._make_response('abc', request)
        self.assertEqual(response.charset, 'UTF-16')

    def test__make_response_with_cache_for(self):
        request = testing.DummyRequest()
        attrs = {'response_cache_for':100}
        request.__dict__.update(attrs)
        helper = self._makeOne('loo.foo')
        response = helper._make_response('abc', request)
        self.assertEqual(response.cache_control.max_age, 100)

    def test_with_alternate_response_factory(self):
        from repoze.bfg.interfaces import IResponseFactory
        class ResponseFactory(object):
            def __init__(self, result):
                self.result = result
        self.config.registry.registerUtility(ResponseFactory, IResponseFactory)
        request = testing.DummyRequest()
        helper = self._makeOne('loo.foo')
        response = helper._make_response('abc', request)
        self.assertEqual(response.__class__, ResponseFactory)
        self.assertEqual(response.result, 'abc')

    def test__make_response_with_real_request(self):
        # functional
        from repoze.bfg.request import Request
        request = Request({})
        attrs = {'response_status':'406 You Lose'}
        request.__dict__.update(attrs)
        helper = self._makeOne('loo.foo')
        response = helper._make_response('abc', request)
        self.assertEqual(response.status, '406 You Lose')
        self.assertEqual(response.body, 'abc')

class Test_render(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, renderer_name, value, request=None, package=None):
        from repoze.bfg.renderers import render
        return render(renderer_name, value, request=request, package=package)

    def test_it_no_request(self):
        renderer = self.config.testing_add_renderer(
            'repoze.bfg.tests:abc/def.pt')
        renderer.string_response = 'abc'
        result = self._callFUT('abc/def.pt', dict(a=1))
        self.assertEqual(result, 'abc')
        renderer.assert_(a=1)
        renderer.assert_(request=None)
        
    def test_it_with_request(self):
        renderer = self.config.testing_add_renderer(
            'repoze.bfg.tests:abc/def.pt')
        renderer.string_response = 'abc'
        request = testing.DummyRequest()
        result = self._callFUT('abc/def.pt',
                               dict(a=1), request=request)
        self.assertEqual(result, 'abc')
        renderer.assert_(a=1)
        renderer.assert_(request=request)

class Test_render_to_response(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, renderer_name, value, request=None, package=None):
        from repoze.bfg.renderers import render_to_response
        return render_to_response(renderer_name, value, request=request,
                                  package=package)

    def test_it_no_request(self):
        renderer = self.config.testing_add_renderer(
            'repoze.bfg.tests:abc/def.pt')
        renderer.string_response = 'abc'
        response = self._callFUT('abc/def.pt', dict(a=1))
        self.assertEqual(response.body, 'abc')
        renderer.assert_(a=1)
        renderer.assert_(request=None)
        
    def test_it_with_request(self):
        renderer = self.config.testing_add_renderer(
            'repoze.bfg.tests:abc/def.pt')
        renderer.string_response = 'abc'
        request = testing.DummyRequest()
        response = self._callFUT('abc/def.pt',
                                 dict(a=1), request=request)
        self.assertEqual(response.body, 'abc')
        renderer.assert_(a=1)
        renderer.assert_(request=request)
    
class Test_get_renderer(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, renderer_name, **kw):
        from repoze.bfg.renderers import get_renderer
        return get_renderer(renderer_name)

    def test_it(self):
        renderer = self.config.testing_add_renderer(
            'repoze.bfg.tests:abc/def.pt')
        result = self._callFUT('abc/def.pt')
        self.assertEqual(result, renderer)

class Dummy:
    pass

class DummyResponse:
    status = '200 OK'
    headerlist = ()
    app_iter = ()
    body = ''

class DummyFactory:
    def __init__(self, renderer):
        self.renderer = renderer

    def __call__(self, path, **kw):
        self.path = path
        self.kw = kw
        return self.renderer
    

