import unittest
from BeautifulSoup import BeautifulSoup
from utils import MockResolverList

class TestUnit():
    
    def __init__(self, html):
        self.html = html
    
    def start_response(self, status, headers):
        pass
    
    def app(self, env, start_response):
        from webob import Response
        res = Response(body=self.html)
        return res(env, start_response)

class TestMiddleware(unittest.TestCase):
    ""
    @property
    def middleware(self):
        from gf.rejuice.develjuice import DevelJuiceMiddleware
        return DevelJuiceMiddleware
    
    def test_css(self):
        html = '''
            <html><head>
                <link type="text/css" media="screen" href="http://127.0.0.1:6543/static/default.min.css">
            </head><body></body></html>'''

        tu = TestUnit(html)
        #import pdb;pdb.set_trace()
        mw = self.middleware(tu.app, {'__file__': None}, ResolverList=MockResolverList, 
            base_urls = 'http://127.0.0.1:6543',         
            url_prefix='PROVIDED BY MOCKRESOLVER',
            filepath='PROVIDED BY MOCKRESOLVER',
            resources='PROVIDED BY MOCKRESOLVER',
            extend_resources=None)
        response = mw({
                'REQUEST_METHOD': 'GET',
                'SCRIPT_NAME': 'X',
                'SERVER_NAME': 'foo',
                'SERVER_PORT': '80',
                'wsgi.url_scheme': 'http',
                'REMOTE_ADDR': 'foo.com',
            }, tu.start_response)
        
        body = ''.join(response)
        soup = BeautifulSoup(body)
        link = soup.findAll('link')
        self.assertEqual(len(link), 1)
        css = link[0]['href'] 
        self.assertEqual(css, 'http://127.0.0.1:6543/static/default.css')

    

    def test_js(self):
        html = '''
            <html><head>
                <script type="text/javascript" src="http://127.0.0.1:6543/static/default.min.js"></script>
            </head><body></body></html>'''

        tu = TestUnit(html)

        mw = self.middleware(tu.app, {'__file__': None}, ResolverList=MockResolverList,
            base_urls = 'http://127.0.0.1:6543', 
            url_prefix='PROVIDED BY MOCKRESOLVER', 
            filepath='PROVIDED BY MOCKRESOLVER',
            resources='PROVIDED BY MOCKRESOLVER',
            extend_resources=None)
        response = mw({
                'REQUEST_METHOD': 'GET',
                'SCRIPT_NAME': 'X',
                'SERVER_NAME': 'foo',
                'SERVER_PORT': '80',
                'wsgi.url_scheme': 'http',
                'REMOTE_ADDR': 'foo.com',
            }, tu.start_response)
        
        body = ''.join(response)
        soup = BeautifulSoup(body)
        scripts = soup.findAll('script')
        js = []
        for script in scripts:
            js.append(script['src'])
        self.assertEqual(js, [
            'http://127.0.0.1:6543/static/a.js',
            'http://127.0.0.1:6543/static/b.js',
            'http://127.0.0.1:6543/static/default.js'
            ])

class TestBasic(unittest.TestCase):

    @property
    def middleware(self):
        from gf.rejuice.develjuice import DevelJuiceMiddleware
        return DevelJuiceMiddleware

    def test_base_urls_noslash(self):
        # no slash in base_urls
        html = '''
            <html><head>
                <link type="text/css" media="screen" href="http://127.0.0.1:6543/static/default.min.css">
            </head><body></body></html>'''

        tu = TestUnit(html)
        mw = self.middleware(tu.app, {'__file__': None}, ResolverList=MockResolverList, 
            base_urls = 'http://127.0.0.1:6543',          #no slash in the end
            url_prefix='PROVIDED BY MOCKRESOLVER',
            filepath='PROVIDED BY MOCKRESOLVER',
            resources='PROVIDED BY MOCKRESOLVER',
            extend_resources=None)
        response = mw({
                'REQUEST_METHOD': 'GET',
                'SCRIPT_NAME': 'X',
                'SERVER_NAME': 'foo',
                'SERVER_PORT': '80',
                'wsgi.url_scheme': 'http',
                'REMOTE_ADDR': 'foo.com',
            }, tu.start_response)
        
        body = ''.join(response)
        soup = BeautifulSoup(body)
        link = soup.findAll('link')
        self.assertEqual(len(link), 1)
        css = link[0]['href'] 
        self.assertEqual(css, 'http://127.0.0.1:6543/static/default.css')

    def test_base_urls_slash(self):
        # slash in base_urls
        html = '''
            <html><head>
                <link type="text/css" media="screen" href="http://127.0.0.1:6543/static/default.min.css">
            </head><body></body></html>'''

        tu = TestUnit(html)
        mw = self.middleware(tu.app, {'__file__': None}, ResolverList=MockResolverList, 
            base_urls = 'http://127.0.0.1:6543/',          #slash in the end
            url_prefix='PROVIDED BY MOCKRESOLVER',
            filepath='PROVIDED BY MOCKRESOLVER',
            resources='PROVIDED BY MOCKRESOLVER',
            extend_resources=None)
        response = mw({
                'REQUEST_METHOD': 'GET',
                'SCRIPT_NAME': 'X',
                'SERVER_NAME': 'foo.com',
                'SERVER_PORT': '80',
                'wsgi.url_scheme': 'http',
                'REMOTE_ADDR': 'foo.com',
            }, tu.start_response)
        
        body = ''.join(response)
        soup = BeautifulSoup(body)
        link = soup.findAll('link')
        self.assertEqual(len(link), 1)
        css = link[0]['href'] 
        self.assertEqual(css, 'http://127.0.0.1:6543/static/default.css')

    def test_base_urls_more_url(self):
        html = '''
            <html><head>
                <link type="text/css" media="screen" href="http://127.0.0.1:6543/static/default.min.css">
                <link type="text/css" media="screen" href="http://127.0.0.1:1234/static/static.min.css">
            </head><body></body></html>'''

        tu = TestUnit(html)
        mw = self.middleware(tu.app, {'__file__': None}, ResolverList=MockResolverList, 
            base_urls = 'http://127.0.0.1:6543/\nhttp://127.0.0.1:1234',
            url_prefix='PROVIDED BY MOCKRESOLVER',
            filepath='PROVIDED BY MOCKRESOLVER',
            resources='PROVIDED BY MOCKRESOLVER',
            extend_resources=None)
        response = mw({
                'REQUEST_METHOD': 'GET',
                'SCRIPT_NAME': 'X',
                'SERVER_NAME': 'foo',
                'SERVER_PORT': '80',
                'wsgi.url_scheme': 'http',
                'REMOTE_ADDR': 'foo.com',
            }, tu.start_response)
        
        body = ''.join(response)
        soup = BeautifulSoup(body)
        link = soup.findAll('link')
        self.assertEqual(len(link), 2)
        css = link[0]['href'] 
        self.assertEqual(css, 'http://127.0.0.1:6543/static/default.css')
        css = link[1]['href'] 
        self.assertEqual(css, 'http://127.0.0.1:1234/static/static.css')

    def test_base_urls_request_base_url(self):
        html = '''
            <html><head>
                <link type="text/css" media="screen" href="http://127.0.0.1:6543/static/default.min.css">
                <link type="text/css" media="screen" href="http://foo.com:8080/static/static.min.css">
                <script type="text/javascript" src="http://127.0.0.1:6543/static/default.min.js"></script>            
                <script type="text/javascript" src="http://foo.com:8080/static/static.min.js"></script>            
            </head><body></body></html>'''

        tu = TestUnit(html)
        mw = self.middleware(tu.app, {'__file__': None}, ResolverList=MockResolverList, 
            base_urls = 'http://127.0.0.1:6543/',
            url_prefix='PROVIDED BY MOCKRESOLVER',
            filepath='PROVIDED BY MOCKRESOLVER',
            resources='PROVIDED BY MOCKRESOLVER',
            extend_resources=None)
        response = mw({
                'REQUEST_METHOD': 'GET',
                'SCRIPT_NAME': 'X',
                'SERVER_NAME': 'foo.com',
                'SERVER_PORT': '8080',
                'wsgi.url_scheme': 'http',
                'REMOTE_ADDR': 'foo.com',
            }, tu.start_response)

        body = ''.join(response)
        soup = BeautifulSoup(body)
        link = soup.findAll('link')
        self.assertEqual(len(link), 2)
        css = link[0]['href'] 
        self.assertEqual(css, 'http://127.0.0.1:6543/static/default.css')
        css = link[1]['href'] 
        self.assertEqual(css, 'http://foo.com:8080/static/static.css')

        scripts = soup.findAll('script')
        js = []
        for script in scripts:
            js.append(script['src'])
        self.assertEqual(js, [
            'http://127.0.0.1:6543/static/a.js',
            'http://127.0.0.1:6543/static/b.js',
            'http://127.0.0.1:6543/static/default.js',
            'http://foo.com:8080/static/static.js',
            ])

    def test_use_request_url(self):
        html = '''
            <html><head>
                <link type="text/css" media="screen" href="http://127.0.0.1:6543/static/default.min.css">
                <link type="text/css" media="screen" href="http://foo.com:8080/static/static.min.css">
                <script type="text/javascript" src="http://127.0.0.1:6543/static/default.min.js"></script>            
                <script type="text/javascript" src="http://foo.com:8080/static/static.min.js"></script>            
            </head><body></body></html>'''

        tu = TestUnit(html)
        mw = self.middleware(tu.app, {'__file__': None}, ResolverList=MockResolverList, 
            base_urls = 'http://127.0.0.1:6543/',
            use_request_url = 'true',
            url_prefix='PROVIDED BY MOCKRESOLVER',
            filepath='PROVIDED BY MOCKRESOLVER',
            resources='PROVIDED BY MOCKRESOLVER',
            extend_resources=None)
        mw({
                'REQUEST_METHOD': 'GET',
                'SCRIPT_NAME': 'X',
                'SERVER_NAME': 'foo.com',
                'SERVER_PORT': '8080',
                'wsgi.url_scheme': 'http',
                'REMOTE_ADDR': 'foo.com',
            }, tu.start_response)
        self.assertEqual(mw.base_urls, ['http://127.0.0.1:6543/', None])

        mw = self.middleware(tu.app, {'__file__': None}, ResolverList=MockResolverList, 
            base_urls = 'http://127.0.0.1:6543/',
            use_request_url = 'false',
            url_prefix='PROVIDED BY MOCKRESOLVER',
            filepath='PROVIDED BY MOCKRESOLVER',
            resources='PROVIDED BY MOCKRESOLVER',
            extend_resources=None)
        mw({
                'REQUEST_METHOD': 'GET',
                'SCRIPT_NAME': 'X',
                'SERVER_NAME': 'foo.com',
                'SERVER_PORT': '8080',
                'wsgi.url_scheme': 'http',
                'REMOTE_ADDR': 'foo.com',
            }, tu.start_response)
        self.assertEqual(mw.base_urls, ['http://127.0.0.1:6543/'])

        mw = self.middleware(tu.app, {'__file__': None}, ResolverList=MockResolverList, 
            base_urls = 'http://127.0.0.1:6543/',
            url_prefix='PROVIDED BY MOCKRESOLVER',
            filepath='PROVIDED BY MOCKRESOLVER',
            resources='PROVIDED BY MOCKRESOLVER',
            extend_resources=None)
        mw({
                'REQUEST_METHOD': 'GET',
                'SCRIPT_NAME': 'X',
                'SERVER_NAME': 'foo.com',
                'SERVER_PORT': '8080',
                'wsgi.url_scheme': 'http',
                'REMOTE_ADDR': 'foo.com',
            }, tu.start_response)
        self.assertEqual(mw.base_urls, ['http://127.0.0.1:6543/', None])

        self.assertRaises(ValueError, self.middleware, tu.app, {'__file__': None}, ResolverList=MockResolverList, 
            base_urls = 'http://127.0.0.1:6543/',
            use_request_url = 'xxx',
            url_prefix='PROVIDED BY MOCKRESOLVER',
            filepath='PROVIDED BY MOCKRESOLVER',
            resources='PROVIDED BY MOCKRESOLVER',
            extend_resources=None)

        mw = self.middleware(tu.app, {'__file__': None}, ResolverList=MockResolverList, 
            url_prefix='PROVIDED BY MOCKRESOLVER',
            filepath='PROVIDED BY MOCKRESOLVER',
            resources='PROVIDED BY MOCKRESOLVER',
            extend_resources=None)
        mw({
                'REQUEST_METHOD': 'GET',
                'SCRIPT_NAME': 'X',
                'SERVER_NAME': 'foo.com',
                'SERVER_PORT': '8080',
                'wsgi.url_scheme': 'http',
                'REMOTE_ADDR': 'foo.com',
            }, tu.start_response)
        self.assertEqual(mw.base_urls, [None])

    def test_port_80(self):
        html = '''
            <html><head>
                <link type="text/css" media="screen" href="http://127.0.0.1:6543/static/default.min.css">
                <link type="text/css" media="screen" href="http://foo.com:80/static/static.min.css">
                <link type="text/css" media="screen" href="http://foo.com/static/static2.min.css">
            </head><body></body></html>'''

        tu = TestUnit(html)
        mw = self.middleware(tu.app, {'__file__': None}, ResolverList=MockResolverList, 
            base_urls = 'http://127.0.0.1:6543',
            use_request_url = 'true',
            url_prefix='PROVIDED BY MOCKRESOLVER',
            filepath='PROVIDED BY MOCKRESOLVER',
            resources='PROVIDED BY MOCKRESOLVER',
            extend_resources=None)
        response = mw({
                'REQUEST_METHOD': 'GET',
                'SCRIPT_NAME': 'X',
                'SERVER_NAME': 'foo.com',
                'SERVER_PORT': '80',
                'wsgi.url_scheme': 'http',
                'REMOTE_ADDR': 'foo.com',
            }, tu.start_response)
        self.assertEqual(mw.base_urls, ['http://127.0.0.1:6543', None])

        body = ''.join(response)
        soup = BeautifulSoup(body)
        link = soup.findAll('link')
        css_list = []
        css_list.append(link[0]['href']) 
        css_list.append(link[1]['href']) 
        css_list.append(link[2]['href']) 
        self.assertEqual('http://127.0.0.1:6543/static/default.css' in css_list, True)
        self.assertEqual('http://foo.com:80/static/static.css' in css_list, True)
        self.assertEqual('http://foo.com/static/static2.css' in css_list, True)

