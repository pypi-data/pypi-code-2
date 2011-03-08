import unittest
import os
import sys
from utils import FakeModule

class TestFilePath(unittest.TestCase):

    @property
    def fake_modules(self):
        return {
            'my.package1': FakeModule('/This/path1'),
            'my.package2': FakeModule('/This/path2'),
            'my.package3': FakeModule('/This/path3'),
            }

    def test_absolute_path(self):
        from gf.rejuice.config import get_filepath_path
        
        result = get_filepath_path('/This/a2.ini', '/Else/static', error_info='ERROR_INFO', modules=self.fake_modules)
        self.assertEqual(result, '/Else/static') 

    def test_relative_path(self):
        from gf.rejuice.config import get_filepath_path
        
        result = get_filepath_path('/This/a2.ini', 'Else/static', error_info='ERROR_INFO', modules=self.fake_modules)
        self.assertEqual(result, '/This/Else/static')

    def test_null_path(self):
        from gf.rejuice.config import get_filepath_path
        
        result = get_filepath_path('/This/a2.ini', '', error_info='ERROR_INFO', modules=self.fake_modules)
        self.assertEqual(result, '/This')

    def test_egg_import(self):
        from gf.rejuice.config import get_filepath_path
        
        result = get_filepath_path('/This/a2.ini', 'egg:my.package1/Else/static', error_info='ERROR_INFO', modules=self.fake_modules)
        self.assertEqual(result, '/This/path1/Else/static') 

        result = get_filepath_path('/This/a2.ini', 'egg:my.package1', error_info='ERROR_INFO', modules=self.fake_modules)
        self.assertEqual(result, '/This/path1') 
 
        result = get_filepath_path('/This/a2.ini', 'egg:my.package2/Else/static', error_info='ERROR_INFO', modules=self.fake_modules)
        self.assertEqual(result, '/This/path2/Else/static') 

        result = get_filepath_path('/This/a2.ini', 'egg:my.package2', error_info='ERROR_INFO', modules=self.fake_modules)
        self.assertEqual(result, '/This/path2') 

        result = get_filepath_path('/This/a2.ini', 'egg:my.package3/Else/static', error_info='ERROR_INFO', modules=self.fake_modules)
        self.assertEqual(result, '/This/path3/Else/static') 

        result = get_filepath_path('/This/a2.ini', 'egg:my.package3', error_info='ERROR_INFO', modules=self.fake_modules)
        self.assertEqual(result, '/This/path3') 

    def test_egg_import_error(self):
        from gf.rejuice.config import get_filepath_path
        
        self.assertRaises(ImportError, get_filepath_path, '/This/a2.ini', 'egg:no.such.package.on.earth/Else/static', error_info='ERROR_INFO', modules=self.fake_modules)

    def test_valueerror(self):
        from gf.rejuice.config import get_filepath_path
        self.assertRaises(ValueError, get_filepath_path, '/This/a2.ini', 'valamimas:no.such.package.on.earth/Else/static', error_info='ERROR_INFO', modules=self.fake_modules)
        


class TestGetIniSection(unittest.TestCase):
    @property
    def fake_modules(self):
        return {
            'my.package1': FakeModule('/This/path1'),
            'my.package2': FakeModule('/This/path2'),
            'my.package3': FakeModule('/This/path3'),
            }

    def test_basic(self):
        from gf.rejuice.config import get_ini_section
        
        result = get_ini_section('/This/a1.ini', 'section1', error_info='ERROR_INFO')
        self.assertEqual(result, ('/This/a1.ini', 'section1')) 

    def test_relative_path(self):
        from gf.rejuice.config import get_ini_section
        
        result = get_ini_section('/This/a1.ini', 'config:/This1/szla2.ini#section2', error_info='ERROR_INFO')
        self.assertEqual(result, ('/This1/szla2.ini', 'section2')) 

    def test_absolute_path(self):
        from gf.rejuice.config import get_ini_section
        
        result = get_ini_section('/This/a1.ini', 'config:This1/szla2.ini#section2', error_info='ERROR_INFO')
        self.assertEqual(result, ('/This/This1/szla2.ini', 'section2')) 

    def test_valuerror(self):
        from gf.rejuice.config import get_ini_section
        
        self.assertRaises(ValueError, get_ini_section, '/This/a1.ini', 'conf:This1/szla2.ini#section2', error_info='ERROR_INFO')
        self.assertRaises(ValueError, get_ini_section, '/This/a1.ini', 'config:This1/szla2.ini:section2', error_info='ERROR_INFO')
        self.assertRaises(ValueError, get_ini_section, '/This/a1.ini', 'config:This1/szla2.ini#section1#section2', error_info='ERROR_INFO')

    def test_egg(self):
        from gf.rejuice.config import get_ini_section
        
        result = get_ini_section('/This/a1.ini', 'egg:my.package1/This1/szla2.ini#section2', error_info='ERROR_INFO', modules=self.fake_modules)
        self.assertEqual(result, ('/This/path1/This1/szla2.ini', 'section2')) 

    def test_egg_valuerror(self):
        from gf.rejuice.config import get_ini_section
        
        self.assertRaises(ValueError, get_ini_section, '/This/a1.ini', 'conf:a2.ini#section2', error_info='ERROR_INFO')
        self.assertRaises(ValueError, get_ini_section, '/This/a1.ini', 'egg:This1/szla2.ini:section2', error_info='ERROR_INFO')
        self.assertRaises(ValueError, get_ini_section, '/This/a1.ini', 'egg:This1/szla2.ini#section1#section2', error_info='ERROR_INFO')
        self.assertRaises(ImportError, get_ini_section, '/This/a2.ini', 'egg:no.such.package.on.earth/Else/static#section1', error_info='ERROR_INFO', modules=self.fake_modules)


class TestJuicerConfigParser(unittest.TestCase):
    ""
    @property
    def parser(self):
        from gf.rejuice.config import JuicerConfigParser
        return JuicerConfigParser

    def static_path(self, *arg):
        return os.path.join(os.path.dirname(sys.modules[__name__].__file__), *arg)
    
    def test_parser(self): 
        p = self.parser(self.static_path('config1/szla.ini'))
        p.load()
        config = p.get_section('filter:rejuice')
        self.assertEqual(config, 
            {'url_prefix': '\nhttp://127.0.0.1:6543/static', 
            'default.min.css': 'default.css', 
            'default.min.js': 'default.js', 
            'filepath': 'egg:gf.szamla/views/static',
            'use': 'egg:gf.rejuice#develjuice',
            })
        
    def test_parser1(self): 
        p = self.parser(self.static_path('config1/szla1.ini'))
        p.load()
        config = p.get_section('filter:rejuice')
        self.assertEqual(config, 
            {'url_prefix': '\nhttp://127.0.0.1:6543/static', 
            'default.min.js' : 'default.js', 
            'default.min.css' : 'default.css', 
            'extend_resources': 'section1', 
            'filepath': 'egg:gf.szamla/views/static',
            'use': 'egg:gf.rejuice#develjuice',
            })

    def test_parser2(self): 
        p = self.parser(self.static_path('config1/szla2.ini'))
        p.load()
        config = p.get_section('filter:rejuice')
        self.assertEqual(config, 
            {'url_prefix': '\nhttp://127.0.0.1:6543/static', 
            'default.min.js' : 'default.js', 
            'default.min.css' : 'default.css', 
            'extend_resources': 'section1\nsection2', 
            'filepath': 'egg:gf.szamla/views/static',
            'use': 'egg:gf.rejuice#develjuice',
            })

    def test_parser3(self): 
        p = self.parser(self.static_path('config1/szla3.ini'))
        p.load()
        config = p.get_section('filter:rejuice')
        self.assertEqual(config, 
            {'url_prefix': '\nhttp://127.0.0.1:6543/static', 
            'default.min.js' : 'default.js', 
            'default.min.css' : 'default.css', 
            'extend_resources': 'config:/config1/szla4.ini#section4', 
            'filepath': 'egg:gf.szamla/views/static',
            'use': 'egg:gf.rejuice#develjuice',
            })

    def test_defaults(self): 
        p = self.parser(self.static_path('config1/szla4.ini'))
        p.load()
        config = p.get_section('filter:rejuiceC4')
        self.assertEqual(config, {
            'url_prefix': '\nhttp://127.0.0.1:6543/static2', 
            'default.min.css': 'default.css', 
            'default.min.js': 'default.js', 
            'extend_resources': 'section1', 
            'filepath': 'egg:gf.szamla/views/static2',
            'use': 'egg:gf.rejuice#develjuice',
            })

        p = self.parser(self.static_path('config1/szla4.ini'))
        p.load()
        config = p.get_section('C4section1')
        self.assertEqual(config, {
            'url_prefix': '\nhttp://127.0.0.1:6543/static', 
            'filepath': 'egg:gf.szamla/views/static'
            })


    def test_interpolation(self): 
        p = self.parser(self.static_path('config1/szla5.ini'))
        p.load()
        config = p.get_section('sectionC5')
        self.assertEqual(config, {
            'url_prefix': '/a/b/c/d',
            'filepath': self.static_path('config1') + '/foo',
            })

        p = self.parser(self.static_path('config1/szla5.ini'))
        p.load()
        config = p.get_section('section1C5')
        self.assertEqual(config, {
            'url_prefix': '/a/b/c/d/e/f',
            'filepath': self.static_path('config1') + '/y/foo',
            })
