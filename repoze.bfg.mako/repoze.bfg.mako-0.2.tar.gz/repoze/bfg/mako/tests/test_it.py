## come on python gimme some of that -*- coding: utf-8 -*-

import unittest

class Base(object):
    def setUp(self):
        from repoze.bfg.configuration import Configurator
        self.config = Configurator()
        self.config.begin()
        import os
        here = os.path.abspath(os.path.dirname(__file__))
        self.templates_dir = os.path.join(here, 'templates')

    def tearDown(self):
        self.config.end()

class Test_renderer_factory(Base, unittest.TestCase):
    def _callFUT(self, path):
        from repoze.bfg.mako import renderer_factory
        return renderer_factory(path)

    def test_no_directories(self):
        from repoze.bfg.exceptions import ConfigurationError
        self.assertRaises(ConfigurationError, self._callFUT, 'path')

    def test_no_lookup(self):
        from repoze.bfg.mako import IMakoLookup
        self.config.add_settings({'mako.directories':self.templates_dir})
        renderer = self._callFUT('helloworld.mak')
        lookup = self.config.registry.getUtility(IMakoLookup)
        self.assertEqual(lookup.directories, [self.templates_dir])
        self.assertEqual(lookup.filesystem_checks, False)
        self.assertEqual(renderer.path, 'helloworld.mak')
        self.assertEqual(renderer.lookup, lookup)

    def test_composite_directories_path(self):
        from repoze.bfg.mako import IMakoLookup
        twice = self.templates_dir + '\n' + self.templates_dir
        self.config.add_settings({'mako.directories':twice})
        self._callFUT('helloworld.mak')
        lookup = self.config.registry.getUtility(IMakoLookup)
        self.assertEqual(lookup.directories, [self.templates_dir]*2)

    def test_with_lookup(self):
        from repoze.bfg.mako import IMakoLookup
        lookup = dict()
        self.config.registry.registerUtility(lookup, IMakoLookup)
        renderer = self._callFUT('helloworld.mak')
        self.assertEqual(renderer.lookup, lookup)
        self.assertEqual(renderer.path, 'helloworld.mak')

class MakoLookupTemplateRendererTests(Base, unittest.TestCase):
    def _getTargetClass(self):
        from repoze.bfg.mako import MakoLookupTemplateRenderer
        return MakoLookupTemplateRenderer

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_instance_implements_ITemplate(self):
        from zope.interface.verify import verifyObject
        from repoze.bfg.interfaces import ITemplateRenderer
        verifyObject(ITemplateRenderer, self._makeOne(None, None))

    def test_class_implements_ITemplate(self):
        from zope.interface.verify import verifyClass
        from repoze.bfg.interfaces import ITemplateRenderer
        verifyClass(ITemplateRenderer, self._getTargetClass())

    def test_call(self):
        lookup = DummyLookup()
        instance = self._makeOne('path', lookup)
        result = instance({}, {'system':1})
        self.failUnless(isinstance(result, unicode))
        self.assertEqual(result, u'result')

    def test_call_with_system_context(self):
        # lame
        lookup = DummyLookup()
        instance = self._makeOne('path', lookup)
        result = instance({}, {'context':1})
        self.failUnless(isinstance(result, unicode))
        self.assertEqual(result, u'result')
        self.assertEqual(lookup.values, {'_context':1})

    def test_call_with_nondict_value(self):
        lookup = DummyLookup()
        instance = self._makeOne('path', lookup)
        self.assertRaises(ValueError, instance, None, {})

    def test_implementation(self):
        lookup = DummyLookup()
        instance = self._makeOne('path', lookup)
        result = instance.implementation().render_unicode()
        self.failUnless(isinstance(result, unicode))
        self.assertEqual(result, u'result')
        
class Test_resolve_resource_spec(unittest.TestCase):
    def _callFUT(self, spec, package_name='__main__'):
        from repoze.bfg.mako import resolve_resource_spec
        return resolve_resource_spec(spec, package_name)

    def test_abspath(self):
        import os
        here = os.path.dirname(__file__)
        path = os.path.abspath(here)
        package_name, filename = self._callFUT(path, 'apackage')
        self.assertEqual(filename, path)
        self.assertEqual(package_name, None)

    def test_rel_spec(self):
        pkg = 'repoze.bfg.mako.tests'
        path = 'test_resource.py'
        package_name, filename = self._callFUT(path, pkg)
        self.assertEqual(package_name, 'repoze.bfg.mako.tests')
        self.assertEqual(filename, 'test_resource.py')
        
    def test_abs_spec(self):
        pkg = 'repoze.bfg.mako.tests'
        path = 'repoze.bfg.mako.nottests:test_resource.py'
        package_name, filename = self._callFUT(path, pkg)
        self.assertEqual(package_name, 'repoze.bfg.mako.nottests')
        self.assertEqual(filename, 'test_resource.py')

    def test_package_name_is_None(self):
        pkg = None
        path = 'test_resource.py'
        package_name, filename = self._callFUT(path, pkg)
        self.assertEqual(package_name, None)
        self.assertEqual(filename, 'test_resource.py')
        
class Test_abspath_from_resource_spec(unittest.TestCase):
    def _callFUT(self, spec, pname='__main__'):
        from repoze.bfg.mako import abspath_from_resource_spec
        return abspath_from_resource_spec(spec, pname)

    def test_pname_is_None_before_resolve_resource_spec(self):
        result = self._callFUT('abc', None)
        self.assertEqual(result, 'abc')

    def test_pname_is_None_after_resolve_resource_spec(self):
        result = self._callFUT('/abc', '__main__')
        self.assertEqual(result, '/abc')

    def test_pkgrelative(self):
        import os
        here = os.path.dirname(__file__)
        path = os.path.abspath(here)
        result = self._callFUT('abc', 'repoze.bfg.mako.tests')
        self.assertEqual(result, os.path.join(path, 'abc'))

class TestIntegration(unittest.TestCase):
    def setUp(self):
        import repoze.bfg.mako
        from repoze.bfg.configuration import Configurator
        self.config = Configurator()
        self.config.begin()
        self.config.add_settings({'mako.directories':
                                'repoze.bfg.mako.tests:templates'})
        self.config.add_renderer('.mak', repoze.bfg.mako.renderer_factory)

    def tearDown(self):
        self.config.end()

    def test_render(self):
        from repoze.bfg.renderers import render
        result = render('helloworld.mak', {'a':1})
        self.assertEqual(result, u'\nHello föö\n')

    def test_render_to_response(self):
        from repoze.bfg.renderers import render_to_response
        result = render_to_response('helloworld.mak', {'a':1})
        self.assertEqual(result.ubody, u'\nHello föö\n')

    def test_get_renderer(self):
        from repoze.bfg.renderers import get_renderer
        result = get_renderer('helloworld.mak')
        self.assertEqual(result.implementation().render_unicode(),
                         u'\nHello föö\n')

class TestZCMLIntegration(unittest.TestCase):
    def setUp(self):
        from repoze.bfg.configuration import Configurator
        self.config = Configurator()
        self.config.begin()
        self.config.add_settings({'mako.directories':
                                'repoze.bfg.mako.tests:templates'})
        self.config.load_zcml('repoze.bfg.mako:configure.zcml')

    def tearDown(self):
        self.config.end()

    def test_mak(self):
        from repoze.bfg.renderers import render
        result = render('helloworld.mak', {'a':1})
        self.assertEqual(result, u'\nHello föö\n')

    def test_mako(self):
        from repoze.bfg.renderers import render
        result = render('helloworld.mako', {'a':1})
        self.assertEqual(result, u'\nHello föö\n')


class DummyLookup(object):
    def get_template(self, path):
        self.path = path
        return self

    def render_unicode(self, **values):
        self.values = values
        return u'result'
        
