import unittest
import os
import sys
from utils import MockResolver
from utils import MockConfigParser

class TestResolverBasic(unittest.TestCase):

    @property
    def resolver(self):
        from gf.rejuice.resolver import Resolver
        return Resolver

    def test_urljoin(self):
        resources = {
            'default.min.js' : [['default.js', None, None]], 
            'default.min.css' : [['default.css', None, None]],
        }

        r = self.resolver(['http://127.0.0.1:6543'], 'static', 'xxx', resources)
        css = r.resolve_css('http://127.0.0.1:6543/static/default.min.css')
        self.assertEqual(css, ['http://127.0.0.1:6543/static/default.css'])

    def test_urljoin2(self):
        resources = {
            'default.min.js' : [['default.js', None, None]], 
            'default.min.css' : [['default.css', None, None]],
        }

        r = self.resolver(['http://127.0.0.1:6543/start'], 'static', 'xxx', resources)
        css = r.resolve_css('http://127.0.0.1:6543/start/static/default.min.css')
        self.assertEqual(css, ['http://127.0.0.1:6543/start/static/default.css'])



class TestResolverListBasic(unittest.TestCase):

    @property
    def resolverlist(self):
        from gf.rejuice.resolver import ResolverList
        return ResolverList
        
    def test_url_prefix(self):
        def args(inifile, section_name):
            return MockConfigParser.results[inifile, section_name], inifile, section_name

        rl = self.resolverlist('http://127.0.0.1:6543', JuicerConfigParser=MockConfigParser, Resolver=MockResolver)
        rl.add_current_section(*args('/This/a0.ini', 'section17'))
        self.assertEqual(rl[0].arg, ('http://127.0.0.1:6543', 'static', '/This/static1',
            {'default.min.css': [['default.css', None, None]],
            'default.min.js': [['default.js', None, None]]}, 
            {('/This/a0.ini', 'section17'): rl[0]}))

        rl = self.resolverlist('http://127.0.0.1:6543', JuicerConfigParser=MockConfigParser, Resolver=MockResolver)
        rl.add_current_section(*args('/This/a0.ini', 'section18'))
        self.assertEqual(rl[0].arg, ('http://127.0.0.1:6543', 'static', '/This/static1', 
            {'default.min.css': [['default.css', None, None]], 
            'default.min.js': [['default.js', None, None]]}, 
            {('/This/a0.ini', 'section18'): rl[0]}))

        rl = self.resolverlist('http://127.0.0.1:6543', JuicerConfigParser=MockConfigParser, Resolver=MockResolver)
        rl.add_current_section(*args('/This/a0.ini', 'section19'))
        self.assertEqual(rl[0].arg, ('http://127.0.0.1:6543', 'static/test', '/This/static1', 
            {'default.min.css': [['default.css', None, None]], 
            'default.min.js': [['default.js', None, None]]}, 
            {('/This/a0.ini', 'section19'): rl[0]}))

class TestResolver(unittest.TestCase):
    ""
    @property
    def resolver(self):
        from gf.rejuice.resolver import Resolver
        return Resolver
    
    def static_path(self, *arg):
        return os.path.join(os.path.dirname(sys.modules[__name__].__file__), *arg)

    def test_resolve_css(self):
        resources = {
            'default.min.js' : [['default.js', None, None]], 
            'default.min.css' : [['default.css', None, None]],
        }
 
        r = self.resolver(['http://127.0.0.1:6543'], 'static', 'xxx', resources)
        
        css = r.resolve_css('http://127.0.0.1:6543/static/default.min.css')
        self.assertEqual(css, ['http://127.0.0.1:6543/static/default.css'])

        css = r.resolve_css('http://127.0.0.1:8080/static/default.min.css')
        self.assertEqual(css, ['http://127.0.0.1:8080/static/default.min.css'])

        css = r.resolve_css('http://127.0.0.1:6543/static/default.min.js')
        self.assertEqual(css, ['http://127.0.0.1:6543/static/default.min.js'])


        css = r.resolve_css('http://127.0.0.1:6543/static/default.js')
        self.assertEqual(css, ['http://127.0.0.1:6543/static/default.js'])

        css = r.resolve_css('http://127.0.0.1:6543/static/css/default.min.css')
        self.assertEqual(css, ['http://127.0.0.1:6543/static/css/default.min.css'])

    def test_resolve_css_request_base_url(self):
        resources = {
            'default.min.js' : [['default.js', None, None]], 
            'default.min.css' : [['default.css', None, None]],
        }
 
        r = self.resolver(['http://127.0.0.1:6543', None], 'static', self.static_path('static1'), resources)
        
        css = r.resolve_css('http://valami.hu:1234/static/default.min.css', 'http://valami.hu:1234')
        self.assertEqual(css, ['http://valami.hu:1234/static/default.css']) 
        
        css = r.resolve_css('http://valami.hu:1234/static/default.min.css', 'http://valamimas.hu:1234')
        self.assertEqual(css, ['http://valami.hu:1234/static/default.min.css']) 
        
        css = r.resolve_css('http://valami.hu:1234/static/default.min.css', 'http://valami.hu:2345')
        self.assertEqual(css, ['http://valami.hu:1234/static/default.min.css']) 
        
        css = r.resolve_css('http://valami.hu:1234/static/default.min.css', 'http://valami.hu')
        self.assertEqual(css, ['http://valami.hu:1234/static/default.min.css']) 

    def test_resolve_css_list(self):
        resources = {
            'default.min.js' : ['default.js', None, None], 
            'default.min.css' : [['default.css', None, None], ['static.css', None, None]],
        }
 
        r = self.resolver(['http://127.0.0.1:6543'], 'static', 'xxx', resources)
        
        css = r.resolve_css('http://127.0.0.1:6543/static/default.min.css')
        self.assertEqual(css, ['http://127.0.0.1:6543/static/default.css', 'http://127.0.0.1:6543/static/static.css'])

    def test_resolve_js(self):
        resources = {
            'default.min.js' : [['default.js', None, None]], 
            'default.min.css' : [['default.css', None, None]],
        }
 
        r = self.resolver(['http://127.0.0.1:6543'], 'static', self.static_path('static1'), resources)
        
        js = r.resolve_js('http://127.0.0.1:6543/static/default.min.js')
        self.assertEqual(js, [ 
                             'http://127.0.0.1:6543/static/js/c.js', 
                             'http://127.0.0.1:6543/static/js/d.js',
                             'http://127.0.0.1:6543/static/a.js', 
                             'http://127.0.0.1:6543/static/js/b.js',
                             'http://127.0.0.1:6543/static/default.js',
                             ]
                             )

        js = r.resolve_js('http://127.0.0.1:8080/static/default.min.js')
        self.assertEqual(js, ['http://127.0.0.1:8080/static/default.min.js'])

        js = r.resolve_js('http://127.0.0.1:6543/static/default.min.css')
        self.assertEqual(js, ['http://127.0.0.1:6543/static/default.min.css'])

        js = r.resolve_js('http://127.0.0.1:6543/static/css/default.min.css')
        self.assertEqual(js, ['http://127.0.0.1:6543/static/css/default.min.css'])

    def test_empty_url_prefix(self):
        resources = {
            'default.min.js' : [['default.js', None, None]], 
            'default.min.css' : [['default.css', None, None]],
        }
 
  
        r = self.resolver(['http://127.0.0.1:6543'], '', self.static_path('static1'), resources)
        
        css = r.resolve_css('http://127.0.0.1:6543/default.min.css')
        self.assertEqual(css, ['http://127.0.0.1:6543/default.css'])

        js = r.resolve_js('http://127.0.0.1:6543/default.min.js')
        self.assertEqual(js, [ 
                             'http://127.0.0.1:6543/js/c.js', 
                             'http://127.0.0.1:6543/js/d.js',
                             'http://127.0.0.1:6543/a.js', 
                             'http://127.0.0.1:6543/js/b.js',
                             'http://127.0.0.1:6543/default.js',
                             ]
                             )

    def test_resolve_js_depends_importsection(self):
        resources = {
            'default.min.js' : [
                ['extend.js', '/This/a2.ini', 'section2'],
                ['default.js', None, None],
                ], 
        }

        resources2 = {
            'url_prefix' : '/static2',
            'filepath' : '/views/static2',
            }

 
        r = self.resolver(['http://127.0.0.1:6543'], 'static1', self.static_path('static1'), resources)
        r2 = self.resolver(['http://127.0.0.1:6543'], 'static2', self.static_path('static2'), resources2)
        r.sections = {
            ('/This/a0.ini', 'section1'): r,
            ('/This/a2.ini', 'section2'): r2
        }

        js = r.resolve_js('http://127.0.0.1:6543/static1/default.min.js')
        self.assertEqual(js, [ 
                             'http://127.0.0.1:6543/static2/a.js', 
                             'http://127.0.0.1:6543/static2/b.js', 
                             'http://127.0.0.1:6543/static2/extend.js', 
                             'http://127.0.0.1:6543/static1/js/c.js', 
                             'http://127.0.0.1:6543/static1/js/d.js', 
                             'http://127.0.0.1:6543/static1/a.js', 
                             'http://127.0.0.1:6543/static1/js/b.js', 
                             'http://127.0.0.1:6543/static1/default.js'
                             ]
                             )


    def test_80_port(self):
        resources = {
            'default.min.js' : [['default.js', None, None]], 
            'default.min.css' : [['default.css', None, None]],
        }
 
        r = self.resolver(['http://127.0.0.1:6543', None], 'static', self.static_path('static1'), resources)
        
        js = r.resolve_js('http://valami.hu:80/static/default.min.js', 'http://valami.hu:80')
        self.assertEqual(js,[
                            'http://valami.hu:80/static/js/c.js', 
                            'http://valami.hu:80/static/js/d.js', 
                            'http://valami.hu:80/static/a.js', 
                            'http://valami.hu:80/static/js/b.js', 
                            'http://valami.hu:80/static/default.js'
                             ]
                             )

        js = r.resolve_js('http://valami.hu/static/default.min.js', 'http://valami.hu:80')
        self.assertEqual(js,[
                            'http://valami.hu/static/js/c.js', 
                            'http://valami.hu/static/js/d.js', 
                            'http://valami.hu/static/a.js', 
                            'http://valami.hu/static/js/b.js', 
                            'http://valami.hu/static/default.js'
                             ]
                             )



    def test_resolve_js_request_base_url(self):
        resources = {
            'default.min.js' : [['default.js', None, None]], 
            'default.min.css' : [['default.css', None, None]],
        }
 
        r = self.resolver(['http://127.0.0.1:6543', None], 'static', self.static_path('static1'), resources)
        js = r.resolve_js('http://valami.hu:1234/static/default.min.js', 'http://valami.hu:1234')
        self.assertEqual(js, 
            ['http://valami.hu:1234/static/js/c.js', 
            'http://valami.hu:1234/static/js/d.js', 
            'http://valami.hu:1234/static/a.js', 
            'http://valami.hu:1234/static/js/b.js', 
            'http://valami.hu:1234/static/default.js'])

        r = self.resolver(['http://127.0.0.1:6543', None], 'static', self.static_path('static1'), resources)
        js = r.resolve_js('http://valami.hu:1234/static/default.min.js', 'http://valamimas.hu:1234')
        self.assertEqual(js, ['http://valami.hu:1234/static/default.min.js']) 
    
        r = self.resolver(['http://127.0.0.1:6543', None], 'static', self.static_path('static1'), resources)
        js = r.resolve_js('http://valami.hu:1234/static/default.min.js', 'http://valami.hu:1233')
        self.assertEqual(js, ['http://valami.hu:1234/static/default.min.js']) 
    
        r = self.resolver(['http://127.0.0.1:6543', None], 'static', self.static_path('static1'), resources)
        js = r.resolve_js('http://valami.hu:1234/static/default.min.js', 'http://valami.hu')
        self.assertEqual(js, ['http://valami.hu:1234/static/default.min.js']) 
    
    def test_resolve_js_import(self):
        resources = {
            'default.min.js' : [['default.js', None, None], ['static.js', '/This/a0.ini', 'section2']], 
            }

        resources2 = {
            'url_prefix' : '/static2',
            'filepath' : 'egg:gf.szamla/views/static2'
            }

        r = self.resolver(['http://127.0.0.1:6543'], 'static', self.static_path('static1'), resources)
        r2 = self.resolver(['http://127.0.0.1:6543'], 'static', self.static_path('static1'), resources2)
        r.sections = {
            ('/This/a0.ini', 'section1'): r,
            ('/This/a0.ini', 'section2'): r2
        }

        js = r.resolve_js('http://127.0.0.1:6543/static/default.min.js')
        self.assertEqual(js, 
            ['http://127.0.0.1:6543/static/js/c.js', 
            'http://127.0.0.1:6543/static/js/d.js', 
            'http://127.0.0.1:6543/static/a.js', 
            'http://127.0.0.1:6543/static/js/b.js', 
            'http://127.0.0.1:6543/static/default.js', 
            'http://127.0.0.1:6543/static/static.js'])

    def test_resolve_js_list(self):
        resources = {
            'default.min.js' : [['default.js', None, None], ['static.js', None, None]], 
            'default.min.css' : [['default.css', None, None]],
        }
 
        r = self.resolver(['http://127.0.0.1:6543'], 'static', self.static_path('static1'), resources, )
        r.sections = {
            ('/This/a0.ini', 'section1'): r,
        }

        js = r.resolve_js('http://127.0.0.1:6543/static/default.min.js')
        self.assertEqual(js, [
                            'http://127.0.0.1:6543/static/js/c.js', 
                            'http://127.0.0.1:6543/static/js/d.js', 
                            'http://127.0.0.1:6543/static/a.js', 
                            'http://127.0.0.1:6543/static/js/b.js', 
                            'http://127.0.0.1:6543/static/default.js', 
                            'http://127.0.0.1:6543/static/static.js'
                            ])
    
    def test_resolve_css_import(self):
        resources = {
            'default.min.css' : [['default.css', None, None], ['static.css', '/This/a0.ini', 'section2']], 
        }

        resources2 = {
            'url_prefix' : '/static2',
            'filepath' : 'egg:gf.szamla/views/static2'
            }


        r = self.resolver(['http://127.0.0.1:6543'], 'static', 'xxx', resources)

        r2 = self.resolver(['http://127.0.0.1:6543'], 'static2', 'xxx', resources2)
        
        r.sections = {
            ('/This/a0.ini', 'section1'): r,
            ('/This/a0.ini', 'section2'): r2
        }
        css = r.resolve_css('http://127.0.0.1:6543/static/default.min.css')
        self.assertEqual(css, ['http://127.0.0.1:6543/static/default.css', 'http://127.0.0.1:6543/static2/static.css'])

    def test_resolve_css_recursive(self):
        resources = {
            'url_prefix' : '/static',
            'filepath' : '/this/views/static',
            'default.min.css' : [
                ['default.css', None, None],
                ['extend.min.css', '/This/a2.ini', 'section_extend'],
                ['more.min.css', None, None],
                ],
            'more.min.css' : [
                ['more.css', None, None],
                ['more2.css', None, None],
                ], 
            } 
        resources2 = {
            'url_prefix' : '/static2',
            'filepath' : '/this/views/static2',
            'extend.min.css' : [
                ['extend.css', None, None],
                ['extend2.css', None, None],
                ], 
            }
        r = self.resolver(['http://127.0.0.1:6543'], 'static', 'xxx', resources)
        r2 = self.resolver(['http://127.0.0.1:6543'], 'static2', 'xxx', resources2)
        r.sections = {
            ('/This/a0.ini', 'section1'): r,
            ('/This/a2.ini', 'section_extend'): r2
        }
        r2.sections = r.sections
        css = r.resolve_css('http://127.0.0.1:6543/static/default.min.css')
        self.assertEqual(css, 
                ['http://127.0.0.1:6543/static/default.css', 'http://127.0.0.1:6543/static2/extend.css', 
                'http://127.0.0.1:6543/static2/extend2.css', 'http://127.0.0.1:6543/static/more.css', 
                'http://127.0.0.1:6543/static/more2.css']
                )
    
    def test_resolve_css_recursive2(self):
        resources = {
            'url_prefix' : '/static',
            'filepath' : '/this/views/static',
            'default.min.css' : [
                ['default.css', None, None],
                ['more.min.css', None, None],
                ],
            'more.min.css' : [
                ['more.css', None, None],
                ['default.min.css', None, None],
                ], 
            } 
        r = self.resolver(['http://127.0.0.1:6543'], 'static', 'xxx', resources)
        r.sections = {('/This/a0.ini', 'section1'): r,}
        self.assertRaises(RuntimeError, r.resolve_css, 'http://127.0.0.1:6543/static/default.min.css')


class TestResolverList(unittest.TestCase):
    ""
    @property
    def resolverlist(self):
        from gf.rejuice.resolver import ResolverList
        return ResolverList
    
    def test_add_new_section_valueerror(self):
        rl = self.resolverlist('http://127.0.0.1:6543', JuicerConfigParser=MockConfigParser, Resolver=MockResolver)
        rl.add_new_section('/This/a0.ini', 'section0', {})
        self.assertRaises(ValueError, rl.add_new_section, '/This/a1.ini', 'section1', {})
        ##self.assertRaises(ValueError, rl.add_new_section, '/This/a2.ini', 'section2', {})
        self.assertRaises(ValueError, rl.add_new_section, '/This/a3.ini', 'section3', {})
        self.assertRaises(ValueError, rl.add_new_section, '/This/a4.ini', 'section4', {})

        rl.add_new_section('/This/a2.ini', 'section2', {})

    def test_add_current_section_valueerror(self):
        def args(inifile, section_name):
            return MockConfigParser.results[inifile, section_name], inifile, section_name

        rl = self.resolverlist('http://127.0.0.1:6543', JuicerConfigParser=MockConfigParser, Resolver=MockResolver)
        rl.add_current_section(*args('/This/a0.ini', 'section0'))
        self.assertRaises(ValueError, rl.add_current_section, *args('/This/a1.ini', 'section1'))
        self.assertRaises(ValueError, rl.add_current_section, *args('/This/a3.ini', 'section3'))
        self.assertRaises(ValueError, rl.add_current_section, *args('/This/a4.ini', 'section4'))

        ##self.assertRaises(ValueError, rl.add_current_section, *args('/This/a2.ini', 'section2'))
        rl.add_current_section(*args('/This/a2.ini', 'section2'))

    def test_basic(self):
        rl = self.resolverlist('http://127.0.0.1:6543', JuicerConfigParser=MockConfigParser, Resolver=MockResolver)
        rl.add_new_section('/This/a0.ini', 'section0', {})
        self.assertEqual(len(rl), 1)
        self.assertEqual(isinstance(rl[0], MockResolver), True)
        self.assertEqual(rl[0].arg, ('http://127.0.0.1:6543', 'static', '/This/static1', 
            {'default.min.css': [['default.css', None, None]], 
            'default.min.js': [['default.js', None, None]]}, 
            {('/This/a0.ini', 'section0'): rl[0]}))
        self.assertEqual(rl[0].kw, {})
        
    def test_extend(self):
        rl = self.resolverlist('http://127.0.0.1:6543', JuicerConfigParser=MockConfigParser, Resolver=MockResolver)
        rl.add_new_section('/This/a5.ini', 'section5', {})
        self.assertEqual(len(rl), 2)
        
        self.assertEqual(isinstance(rl[0], MockResolver), True)
        self.assertEqual(rl[0].arg, ('http://127.0.0.1:6543', 'static', '/This/static1', 
            {'default.min.css': [['default.css', None, None]], 
            'default.min.js': [['default.js', None, None]]}, 
            {('/This/a5.ini', 'section5'): rl[0], ('/This/a5.ini', 'section6'): rl[1]}))
        self.assertEqual(rl[0].kw, {})
        
        self.assertEqual(isinstance(rl[1], MockResolver), True)
        self.assertEqual(rl[1].arg, ('http://127.0.0.1:6543', 'static', '/This/static1', 
        {'default2.min.js': [['default2.js', None, None]], 
        'default2.min.css': [['default2.css', None, None]]}, 
        {('/This/a5.ini', 'section5'): rl[0], ('/This/a5.ini', 'section6'): rl[1]}))
        self.assertEqual(rl[1].kw, {})

    def test_extend_withempty(self):
        rl = self.resolverlist('http://127.0.0.1:6543', JuicerConfigParser=MockConfigParser, Resolver=MockResolver)
        rl.add_new_section('/This/a11.ini', 'section32', {})
        self.assertEqual(len(rl), 2)
        
        self.assertEqual(isinstance(rl[0], MockResolver), True)
        self.assertEqual(rl[0].arg, ('http://127.0.0.1:6543', 'static', '/This/static', 
            {'default.min.css': [['default.css', None, None]], 
            'default.min.js': [['default.js', None, None]]}, 
            {('/This/a11.ini', 'section32'): rl[0], ('/This/a11.ini', 'section33'): rl[1]}))
        self.assertEqual(rl[0].kw, {})
       
        # Even a section with empty resources, produces a resolver.
        self.assertEqual(isinstance(rl[1], MockResolver), True)
        self.assertEqual(rl[1].arg, ('http://127.0.0.1:6543', 'static2', '/This/static2', 
        {}, 
        {('/This/a11.ini', 'section32'): rl[0], ('/This/a11.ini', 'section33'): rl[1]}))
        self.assertEqual(rl[1].kw, {})

    def test_extend1(self):
        rl = self.resolverlist('http://127.0.0.1:6543', JuicerConfigParser=MockConfigParser, Resolver=MockResolver)
        rl.add_new_section('/This/a7.ini', 'section7', {})
        self.assertEqual(len(rl), 3)
        
        self.assertEqual(isinstance(rl[0], MockResolver), True)
        self.assertEqual(rl[0].arg, ('http://127.0.0.1:6543', 'static', '/This/static1', 
        {'default.min.css': [['default.css', None, None]], 
        'default.min.js': [['default.js', None, None]]}, 
        {('/This/a7.ini', 'section8'): rl[1], ('/This/a7.ini', 'section7'): rl[0], ('/This/a7.ini', 'section9'): rl[2]}))
        self.assertEqual(rl[0].kw, {})
        
        self.assertEqual(isinstance(rl[1], MockResolver), True)
        self.assertEqual(rl[1].arg, ('http://127.0.0.1:6543', 'static', '/This/static1', 
        {'default2.min.js': [['default2.js', None, None]], 
        'default2.min.css': [['default2.css', None, None]]}, 
        {('/This/a7.ini', 'section8'): rl[1], ('/This/a7.ini', 'section7'): rl[0], ('/This/a7.ini', 'section9'): rl[2]}))         
        self.assertEqual(rl[1].kw, {})
        
        self.assertEqual(isinstance(rl[2], MockResolver), True)
        self.assertEqual(rl[2].arg, ('http://127.0.0.1:6543', 'static', '/This/static1', 
        {'default3.min.css': [['default3.css', None, None]], 
        'default3.min.js': [['default3.js', None, None]]}, 
        {('/This/a7.ini', 'section8'): rl[1], ('/This/a7.ini', 'section7'): rl[0], ('/This/a7.ini', 'section9'): rl[2]}))
        self.assertEqual(rl[2].kw, {})

    def test_extend2(self):
        rl = self.resolverlist('http://127.0.0.1:6543', JuicerConfigParser=MockConfigParser, Resolver=MockResolver)
        rl.add_new_section('/This/a10.ini', 'section10', {})
        self.assertEqual(len(rl), 2)
        
        self.assertEqual(isinstance(rl[0], MockResolver), True)
        self.assertEqual(rl[0].arg, ('http://127.0.0.1:6543', 'static', '/This/static1', 
        {'default.min.css': [['default.css', None, None]], 
        'default.min.js': [['default.js', None, None]]}, 
        {('/This/a10.ini', 'section10'): rl[0], ('/This/a11.ini', 'section11'): rl[1]}))
        self.assertEqual(rl[0].kw, {})
        
        self.assertEqual(isinstance(rl[1], MockResolver), True)
        self.assertEqual(rl[1].arg, ('http://127.0.0.1:6543', 'static', '/This/static1', 
        {'default11.min.js': [['default11.js', None, None]], 
        'default11.min.css': [['default11.css', None, None]]}, 
        {('/This/a10.ini', 'section10'): rl[0], ('/This/a11.ini', 'section11'): rl[1]}))
        self.assertEqual(rl[1].kw, {})

    def test_extend3(self):
        rl = self.resolverlist('http://127.0.0.1:6543', JuicerConfigParser=MockConfigParser, Resolver=MockResolver)
        rl.add_new_section('/This/a12.ini', 'section12', {})
        self.assertEqual(len(rl), 5)
        
        self.assertEqual(isinstance(rl[0], MockResolver), True)
        self.assertEqual(rl[0].arg, ('http://127.0.0.1:6543', 'static', '/This/static1', 
        {'default.min.css': [['default.css', None, None]], 
        'default.min.js': [['default.js', None, None]]}, 
        {('/This/a12.ini', 'section13'): rl[1], 
            ('/This/a14.ini', 'section15'): rl[3], 
            ('/This/a14.ini', 'section14'): rl[2], 
            ('/This/a12.ini', 'section12'): rl[0], 
            ('/This/a14.ini', 'section16'): rl[4]}) )
        self.assertEqual(rl[0].kw, {})
        
        self.assertEqual(isinstance(rl[1], MockResolver), True)
        self.assertEqual(rl[1].arg, ('http://127.0.0.1:6543', 'static', '/This/static1', 
            {'default13.min.js': [['default13.js', None, None]], 
            'default13.min.css': [['default13.css', None, None]]}, 
            {('/This/a12.ini', 'section13'): rl[1], 
                ('/This/a14.ini', 'section15'): rl[3], 
                ('/This/a14.ini', 'section14'): rl[2], 
                ('/This/a12.ini', 'section12'): rl[0], 
                ('/This/a14.ini', 'section16'): rl[4] }))
        self.assertEqual(rl[1].kw, {})
        
        self.assertEqual(isinstance(rl[2], MockResolver), True)
        self.assertEqual(rl[2].arg, ('http://127.0.0.1:6543', 'static', '/This/static1', 
            {'default14.min.css': [['default14.css', None, None]], 
            'default14.min.js': [['default14.js', None, None]]}, 
            {('/This/a12.ini', 'section13'): rl[1], 
                ('/This/a14.ini', 'section15'): rl[3], 
                ('/This/a14.ini', 'section14'): rl[2], 
                ('/This/a12.ini', 'section12'): rl[0], 
                ('/This/a14.ini', 'section16'): rl[4] }))
        self.assertEqual(rl[2].kw, {})
        
        self.assertEqual(isinstance(rl[3], MockResolver), True)
        self.assertEqual(rl[3].arg, ('http://127.0.0.1:6543', 'static', '/This/static1', 
            {'default15.min.css': [['default15.css', None, None]], 
            'default15.min.js': [['default15.js', None, None]]}, 
            {('/This/a12.ini', 'section13'): rl[1], 
                ('/This/a14.ini', 'section15'): rl[3], 
                ('/This/a14.ini', 'section14'): rl[2], 
                ('/This/a12.ini', 'section12'): rl[0], 
                ('/This/a14.ini', 'section16'): rl[4] }))
        self.assertEqual(rl[3].kw, {})
        
        self.assertEqual(isinstance(rl[4], MockResolver), True)
        self.assertEqual(rl[4].arg, ('http://127.0.0.1:6543', 'static', '/This/static1', 
            {'default16.min.css': [['default16.css', None, None]], 
            'default16.min.js': [['default16.js', None, None]]},  
            {('/This/a12.ini', 'section13'): rl[1], 
                ('/This/a14.ini', 'section15'): rl[3], 
                ('/This/a14.ini', 'section14'): rl[2], 
                ('/This/a12.ini', 'section12'): rl[0], 
                ('/This/a14.ini', 'section16'): rl[4] }))
        self.assertEqual(rl[4].kw, {})
    
    def test_extend4(self):
        rl = self.resolverlist('http://127.0.0.1:6543', JuicerConfigParser=MockConfigParser, Resolver=MockResolver)
        rl.add_new_section('/This/a0.ini', 'section20', {})
        self.assertEqual(len(rl), 1)
        
        self.assertEqual(isinstance(rl[0], MockResolver), True)
        self.assertEqual(rl[0].arg, ('http://127.0.0.1:6543', 'static', '/This/static', 
            {'default.min.css': [['default.css', None, None], ['static.css', None, None]], 
            'default.min.js': [['default.js', None, None], ['static.js', None, None]]}, 
            {('/This/a0.ini', 'section20'): rl[0]}))
        self.assertEqual(rl[0].kw, {})

    def test_extend5(self):
        rl = self.resolverlist('http://127.0.0.1:6543', JuicerConfigParser=MockConfigParser, Resolver=MockResolver)
        self.assertRaises(ValueError, rl.add_new_section, '/This/a0.ini', 'section21')

        rl = self.resolverlist('http://127.0.0.1:6543', JuicerConfigParser=MockConfigParser, Resolver=MockResolver)
        rl.add_new_section('/This/a0.ini', 'section21', allow_filter_section_keys=True)
        self.assertEqual(len(rl), 1)
        self.assertEqual(rl[0].arg, ('http://127.0.0.1:6543', 'static', '/This/static', 
            {'default.min.css': [['default.css', None, None], ['static.css', None, None]], 
            'default.min.js': [['default.js', None, None], ['static.js', None, None]]}, 
            {('/This/a0.ini', 'section21'): rl[0]}))
        
        rl = self.resolverlist('http://127.0.0.1:6543', JuicerConfigParser=MockConfigParser, Resolver=MockResolver)
        rl.add_new_section('/This/a0.ini', 'section22', allow_filter_section_keys=True)
        self.assertEqual(len(rl), 2)
        self.assertEqual(rl[1].arg, ('http://127.0.0.1:6543', 'static', '/This/static', 
            {'default.min.css': [['default.css', None, None]], 
            'default.min.js': [['default.js', None, None]]}, 
            {('/This/a0.ini', 'section23'): rl[1], ('/This/a0.ini', 'section22'): rl[0]}))
        
        rl = self.resolverlist('http://127.0.0.1:6543', JuicerConfigParser=MockConfigParser, Resolver=MockResolver)
        self.assertRaises(ValueError, rl.add_new_section, '/This/a0.ini', 'section24', allow_filter_section_keys=True)

    def test_extend6(self):
        rl = self.resolverlist('http://127.0.0.1:6543', JuicerConfigParser=MockConfigParser, Resolver=MockResolver)
        rl.add_new_section('/This/a0.ini', 'section26')
        self.assertEqual(len(rl), 2)
    
    def test_extend7(self):
        rl = self.resolverlist('http://127.0.0.1:6543', JuicerConfigParser=MockConfigParser, Resolver=MockResolver)
        rl.add_new_section('/This/a0.ini', 'section28')
        self.assertEqual(len(rl), 4)
