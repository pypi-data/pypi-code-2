
# --
# Mock classes needed for testing
# the relevant components in an isolated way
# --

import os

class MockResolver(object):

    mock_results = [
        # we need some different result sets, for setting resolving in a resolver list 

        # _bump_mock_results(0) and default case    
        dict(
            css = {
                'http://127.0.0.1:6543/static/default.min.css': ['http://127.0.0.1:6543/static/default.css'],
                'http://127.0.0.1:1234/static/static.min.css': ['http://127.0.0.1:1234/static/static.css'],
                'http://foo.com:8080/static/static.min.css' : ['http://foo.com:8080/static/static.css'],
                'http://foo.com:80/static/static.min.css' : ['http://foo.com:80/static/static.css'],
                'http://foo.com/static/static2.min.css' : ['http://foo.com/static/static2.css'],
                },

            js = {
                'http://127.0.0.1:6543/static/default.min.js': 
                        [
                        'http://127.0.0.1:6543/static/a.js',
                        'http://127.0.0.1:6543/static/b.js',
                        'http://127.0.0.1:6543/static/default.js'  
                        ],
                'http://foo.com:8080/static/static.min.js': 
                        [
                        'http://foo.com:8080/static/static.js',
                        ],
                },
            ),

        # _bump_mock_results(1)   
        dict(
            css = {
                'http://127.0.0.1:6543/static/default2.min.css': ['http://127.0.0.1:6543/static/default2.css'],
                },

            js = {
                'http://127.0.0.1:6543/static/default2.min.js': 
                        [
                        'http://127.0.0.1:6543/static/a2.js',
                        'http://127.0.0.1:6543/static/b2.js',
                        'http://127.0.0.1:6543/static/default2.js'  
                        ],
                },
            ),

        # _bump_mock_results(2)   
        dict(
            css = {
                'http://127.0.0.1:6543/static/default3.min.css': ['http://127.0.0.1:6543/static/default3.css'],
                },

            js = {
                'http://127.0.0.1:6543/static/default3.min.js':
                        [
                        'http://127.0.0.1:6543/static/a3.js',
                        'http://127.0.0.1:6543/static/b3.js',
                        'http://127.0.0.1:6543/static/default3.js'  
                        ],
                },
            ),

        ]

    def __init__(self, *arg, **kw):
        self.arg = arg
        self.kw = kw
        #
        self._bump_mock_results(0) # by default, the first result set works

    def _bump_mock_results(self, selector):
        self._mock_results_selector = selector

    def resolve_js(self, minified_resource, request_base_url):
        _no_result = [minified_resource]
        return self.mock_results[self._mock_results_selector]['js'].get(minified_resource, _no_result)

    def resolve_css(self, minified_resource, request_base_url):
        _no_result = [minified_resource]
        return self.mock_results[self._mock_results_selector]['css'].get(minified_resource, _no_result)
    
    @property
    def resources(self):
        # ... good enough for testing,
        return {
            'default.min.js' : [['default.js', None, None]], 
            'default.min.css' : [['default.css', None, None]],
        }


class MockResolverList(MockResolver):
    # We do not really want to mock a list of resolvers, only the case of
    # a single resolver in a list. So, resolve_js and resolve_css
    # return the same results, and an empty add_current_section
    # is adequate for our testing purposes.

    def add_current_section(self, config, inifile, section_name):
        pass

    def __iter__(self):
        yield self


class MockConfigParser(object):

    results = {
        ('/This/a0.ini', 'section0'): {
            'url_prefix': 'static', 
            'filepath': '/This/static1',
            'default.min.js' : 'default.js',
            'default.min.css' : 'default.css', 
            },
        ('/This/a1.ini', 'section1'): {
            'filepath': '/This/static1',
            'default.min.js' : 'default.js',
            'default.min.css' : 'default.css', 
            },
        ('/This/a2.ini', 'section2'): {
            'url_prefix': 'static', 
            'filepath': '/This/static1',
            },
        ('/This/a3.ini', 'section3'): {
            'url_prefix': 'static', 
            },
        ('/This/a4.ini', 'section4'): {
            'url_prefix': 'static', 
            'filepath': '/This/static1',
            'default.min.js' : 'default.js',
            'default.min.css' : 'default.css', 
            'xxx' : 'yyy',
            },
        ('/This/a5.ini', 'section5'): {
            'url_prefix': 'static', 
            'filepath': '/This/static1',
            'extend_resources' : 'section6',
            'default.min.js' : 'default.js',
            'default.min.css' : 'default.css', 
            },
        ('/This/a5.ini', 'section6'): {
            'url_prefix': 'static', 
            'filepath': '/This/static1',
            'default2.min.js' : 'default2.js',
            'default2.min.css' : 'default2.css', 
            },
        ('/This/a7.ini', 'section7'): {
            'url_prefix': 'static', 
            'filepath': '/This/static1',
            'default.min.js' : 'default.js',
            'default.min.css' : 'default.css', 
            'extend_resources' : 'section8\nsection9',
            },
        ('/This/a7.ini', 'section8'): {
            'url_prefix': 'static', 
            'filepath': '/This/static1',
            'default2.min.js' : 'default2.js',
            'default2.min.css' : 'default2.css', 
            },
        ('/This/a7.ini', 'section9'): {
            'url_prefix': 'static', 
            'filepath': '/This/static1',
            'default3.min.js' : 'default3.js',
            'default3.min.css' : 'default3.css', 
            },
        ('/This/a10.ini', 'section10'): {
            'url_prefix': 'static', 
            'filepath': '/This/static1',
            'default.min.js' : 'default.js',
            'default.min.css' : 'default.css', 
            'extend_resources' : 'config:/This/a11.ini#section11',
            },
        ('/This/a11.ini', 'section11'): {
            'url_prefix': 'static', 
            'filepath': '/This/static1',
            'default11.min.js' : 'default11.js',
            'default11.min.css' : 'default11.css', 
            },


        ('/This/a12.ini', 'section12'): {
            'url_prefix': 'static', 
            'filepath': '/This/static1',
            'default.min.js' : 'default.js',
            'default.min.css' : 'default.css', 
            'extend_resources' : 'section13\nconfig:/This/a14.ini#section14',
            },
        ('/This/a12.ini', 'section13'): {
            'url_prefix': 'static', 
            'filepath': '/This/static1',
            'default13.min.js' : 'default13.js',
            'default13.min.css' : 'default13.css', 
            },
        ('/This/a14.ini', 'section14'): {
            'url_prefix': 'static', 
            'filepath': '/This/static1',
            'default14.min.js' : 'default14.js',
            'default14.min.css' : 'default14.css', 
            'extend_resources' : 'section15\nsection16',
            },
        ('/This/a14.ini', 'section15'): {
            'url_prefix': 'static', 
            'filepath': '/This/static1',
            'default15.min.js' : 'default15.js',
            'default15.min.css' : 'default15.css', 
            },
        ('/This/a14.ini', 'section16'): {
            'url_prefix': 'static', 
            'filepath': '/This/static1',
            'default16.min.js' : 'default16.js',
            'default16.min.css' : 'default16.css', 
            },
        ('/This/a0.ini', 'section17'): {
            'url_prefix': 'static', 
            'filepath': '/This/static1',
            'default.min.js' : 'default.js',
            'default.min.css' : 'default.css', 
            },
        ('/This/a0.ini', 'section18'): {
            'url_prefix': '/static', 
            'filepath': '/This/static1',
            'default.min.js' : 'default.js',
            'default.min.css' : 'default.css', 
            },
        ('/This/a0.ini', 'section19'): {
            'url_prefix': '/static/test', 
            'filepath': '/This/static1',
            'default.min.js' : 'default.js',
            'default.min.css' : 'default.css', 
            },
        ('/This/a0.ini', 'section20'): {
            'url_prefix': 'static', 
            'filepath': '/This/static',
            'default.min.js' : '\ndefault.js\nstatic.js',
            'default.min.css' : '\ndefault.css\nstatic.css', 
            },
        ('/This/a0.ini', 'section21'): {
            'base_urls': 'XXX',
            'url_prefix': 'static', 
            'filepath': '/This/static',
            'default.min.js' : '\ndefault.js\nstatic.js',
            'default.min.css' : '\ndefault.css\nstatic.css', 
            },
        ('/This/a0.ini', 'section22'): {
            'base_urls': 'XXX',
            'url_prefix': 'static', 
            'filepath': '/This/static',
            'default.min.js' : '\ndefault.js\nstatic.js',
            'default.min.css' : '\ndefault.css\nstatic.css', 
            'extend_resources' : 'section23',
            },
        ('/This/a0.ini', 'section23'): {
            'url_prefix': 'static', 
            'filepath': '/This/static',
            'default.min.js' : 'default.js',
            'default.min.css' : 'default.css', 
            },
        ('/This/a0.ini', 'section24'): {
            'base_urls': 'XXX',
            'url_prefix': 'static', 
            'filepath': '/This/static',
            'default.min.js' : '\ndefault.js\nstatic.js',
            'default.min.css' : '\ndefault.css\nstatic.css', 
            'extend_resources' : 'section25',
            },
        ('/This/a0.ini', 'section25'): {
            'base_urls': 'XXX',
            'url_prefix': 'static', 
            'filepath': '/This/static',
            'default.min.js' : 'default.js',
            'default.min.css' : 'default.css', 
            },
        ('/This/a0.ini', 'section26'): {
            'url_prefix': 'static', 
            'filepath': '/This/static',
            'default.min.js' : '\ndefault.js\nstatic.js',
            'default.min.css' : '\ndefault.css\nstatic.css', 
            'extend_resources' : 'section27',
            },
        ('/This/a0.ini', 'section27'): {
            'url_prefix': 'static', 
            'filepath': '/This/static',
            'default.min.js' : 'default.js',
            'default.min.css' : 'default.css', 
            'extend_resources' : 'section26',
            },
        ('/This/a0.ini', 'section28'): {
            'url_prefix': 'static', 
            'filepath': '/This/static',
            'default.min.js' : '\ndefault.js\nstatic.js',
            'default.min.css' : '\ndefault.css\nstatic.css', 
            'extend_resources' : 'section29',
            },
        ('/This/a0.ini', 'section29'): {
            'url_prefix': 'static', 
            'filepath': '/This/static',
            'default.min.js' : 'default.js',
            'default.min.css' : 'default.css', 
            'extend_resources' : 'section30',
            },
        ('/This/a0.ini', 'section30'): {
            'url_prefix': 'static', 
            'filepath': '/This/static',
            'default.min.js' : '\ndefault.js\nstatic.js',
            'default.min.css' : '\ndefault.css\nstatic.css', 
            'extend_resources' : 'section31',
            },
        ('/This/a0.ini', 'section31'): {
            'url_prefix': 'static', 
            'filepath': '/This/static',
            'default.min.js' : 'default.js',
            'default.min.css' : 'default.css', 
            'extend_resources' : 'section28',
            },

        ('/This/a11.ini', 'section32'): {
            'url_prefix': 'static', 
            'filepath': '/This/static',
            'default.min.css' : 'default.css',
            'default.min.js' : 'default.js',
            'extend_resources' : 'section33',
            },
         ('/This/a11.ini', 'section33'): {
            'url_prefix': 'static2', 
            'filepath': '/This/static2',
            },


        # imported resources
         ('/This/ir0.ini', 'section1'): {
            'url_prefix': 'static', 
            'filepath': '/This/static',
            'default.min.css' : '\ndefault.css\nstatic.css section2',
            'extend_resources' : 'section2',
            },
         ('/This/ir0.ini', 'section2'): {
            'url_prefix': 'static2', 
            'filepath': '/This/static2',
            },


        }

    def __init__(self, filename):
        self.filename = filename

    def load(self):
        pass

    def get_section(self, section_name):
        return self.results[self.filename, section_name]


class FakeModule(object):

    def __init__(self, path):
        self.__file__ = os.path.join(path, '__init__.py')
