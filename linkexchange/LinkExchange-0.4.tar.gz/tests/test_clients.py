import unittest
import re

from linkexchange.utils import find_links
from linkexchange.tests import ClientLinksTestMixin
from linkexchange.tests import ClientContentFilterTestMixin

from linkexchange.clients.sape import SapeClient, SapeContextClient
from linkexchange.clients.sape import SapeArticlesClient
from linkexchange.clients.sape import SapeTestServer

from linkexchange.clients.sape import SapeArticlesIndexTestServer
from linkexchange.clients.sape import SapeArticlesArticleTestServer
from linkexchange.clients.sape import SapeArticlesTemplateTestServer

from linkexchange.clients.linkfeed import LinkFeedClient
from linkexchange.clients.linkfeed import LinkFeedTestServer

from linkexchange.clients.trustlink import TrustLinkClient
from linkexchange.clients.trustlink import TrustLinkTestServer

class NoQueryStringTestMixin:
    def test_no_query_string(self):
        client = self.new_client(no_query_string=True)
        request = self.new_request(uri='/not_exists')
        self.assertEqual(
                self.check_code in client.get_raw_links(request)[0], True)
        request = self.new_request(uri='/not_exists?param=value')
        self.assertEqual(
                client.get_raw_links(request) == [], True)

        for test_uri, test_links in self.page_link_map.items():
            if '?' in test_uri:
                continue
            request = self.new_request(uri=test_uri + '?not_exists')
            raw_links1 = client.get_raw_links(request)
            request = self.new_request(uri=test_uri)
            raw_links2 = client.get_raw_links(request)
            self.assertEqual(len(raw_links1), len(test_links))
            self.assertEqual(len(raw_links2), len(test_links))
            for i in range(len(test_links)):
                test_href, test_anchor = test_links[i]
                attrs, anchor = find_links(raw_links1[i])[0]
                self.assertEqual(attrs.get('href', ''), test_href)
                self.assertEqual(anchor.strip(), test_anchor.strip())
                attrs, anchor = find_links(raw_links2[i])[0]
                self.assertEqual(attrs.get('href', ''), test_href)
                self.assertEqual(anchor.strip(), test_anchor.strip())

        client = self.new_client(no_query_string=False)
        request = self.new_request(uri='/not_exists')
        self.assertEqual(
                self.check_code in client.get_raw_links(request)[0], True)
        request = self.new_request(uri='/not_exists?param=value')
        self.assertEqual(
                self.check_code in client.get_raw_links(request)[0], True)

        for test_uri, test_links in self.page_link_map.items():
            if '?' in test_uri:
                continue
            request = self.new_request(uri=test_uri + '?not_exists')
            for link in client.get_raw_links(request):
                self.assertEqual(find_links(link), [])

class SapeClientXTestMixin(NoQueryStringTestMixin, ClientLinksTestMixin):
    """
    Base test case to test SapeClient independent of server format.
    """
    page_link_map = {
            '/':[
                ('http://example1.com', 'example text 1'),
                ('http://example2.com', 'example text 2'),
                ],
            '/path/1':[
                ('http://example1.com', 'example text 1'),
                ('http://example2.com', 'example text 2'),
                ('http://example3.com', 'example text 3'),
                ('http://example4.com', 'example text 4'),
                ],
            }
    check_code = '<!--12345-->'
    server_format = None
    cookies = {'sape_cookie': 'user123456789'}
    html_links_delim_pattern = r'\. '

    def create_servers(cls):
        return [SapeTestServer(server_format=cls.server_format)]
    create_servers = classmethod(create_servers)

    def new_client(self, **kw):
        kw.setdefault('user', 'user123456789')
        kw.setdefault('db_driver', ('mem',))
        kw.setdefault('server_list', [
            self.servers[0].url.replace('%', '%%')])
        kw.setdefault('server_format', self.server_format)
        if kw.get('broken_server', False):
            kw['server_list'] = ['file:///not_exists']
        return SapeClient(**kw)

class SapeClientPHPTest(SapeClientXTestMixin, unittest.TestCase):
    """
    Test SapeClient with php server format.
    """
    server_format = 'php'

class SapeClientXMLTest(SapeClientXTestMixin, unittest.TestCase):
    """
    Test SapeClient with xml server format.
    """
    server_format = 'xml'

class SapeContextClientXCookiesTestMixin(ClientContentFilterTestMixin):
    """
    Base test case to test SapeContextClient independent of server_format and
    service cookie enabled.
    """
    page_content_map = {
            '/': [
                ("""This&#x20;text contains
                    example text 1.""",
                 """<sape_index>This&#x20;text contains
                    <a href="http://example1.com">example text 1</a>.</sape_index><!--12345-->"""),
                ("""foo <textarea>
                    example text 1 bar</textarea>""",
                 """<sape_index>foo <textarea>
                    example text 1 bar</textarea></sape_index><!--12345-->"""),
                ("""<html>
                    <body>
                    Full example text 2.
                    </body>
                    </html>""",
                 """<html>
                    <body><sape_index>
                    Full <a href="http://example2.com">example text 2</a>.
                    </sape_index><!--12345--></body>
                    </html>"""),
                ("""<html>
                    <body>
                    <sape_index>First example text 1.</sape_index>
                    Second example text 2.
                    </body>
                    </html>""",
                 """<html>
                    <body>
                    <sape_index>First <a href="http://example1.com">example text 1</a>.</sape_index><!--12345-->
                    Second example text 2.
                    </body>
                    </html>"""),
                ],
            }
    check_code = '<!--12345-->'
    server_format = None
    cookies = {'sape_cookie': 'user123456789'}

    def create_servers(cls):
        return [SapeTestServer(server_format=cls.server_format)]
    create_servers = classmethod(create_servers)

    def new_client(self, **kw):
        kw.setdefault('user', 'user123456789')
        kw.setdefault('db_driver', ('mem',))
        kw.setdefault('server_list', [
            self.servers[0].url.replace('%', '%%')])
        kw.setdefault('server_format', self.server_format)
        return SapeContextClient(**kw)

class SapeContextClientPHPCookiesTest(SapeContextClientXCookiesTestMixin,
        unittest.TestCase):
    server_format = 'php'

class SapeContextClientXMLCookiesTest(SapeContextClientXCookiesTestMixin,
        unittest.TestCase):
    server_format = 'xml'

class SapeContextClientXTestMixin(SapeContextClientXCookiesTestMixin):
    """
    Base test case to test SapeContextClient independent of server_format and
    service cookie disabled.
    """
    page_content_map = {
            '/': [
                ("""This&#x20;text contains
                    example text 1.""",
                 """This&#x20;text contains
                    <a href="http://example1.com">example text 1</a>."""),
                ("""foo <textarea>
                    example text 1 bar</textarea>""",
                 """foo <textarea>
                    example text 1 bar</textarea>"""),
                ("""<html>
                    <body>
                    Full example text 2.
                    </body>
                    </html>""",
                 """<html>
                    <body>
                    Full <a href="http://example2.com">example text 2</a>.
                    </body>
                    </html>"""),
                ("""<html>
                    <body>
                    <sape_index>First example text 1.</sape_index>
                    Second example text 2.
                    </body>
                    </html>""",
                 """<html>
                    <body>
                    First <a href="http://example1.com">example text 1</a>.
                    Second example text 2.
                    </body>
                    </html>"""),
                ],
            }
    server_format = None
    cookies = None

class SapeContextClientPHPTest(SapeContextClientXTestMixin,
        unittest.TestCase):
    server_format = 'php'

class SapeContextClientXMLTest(SapeContextClientXTestMixin,
        unittest.TestCase):
    server_format = 'xml'

class SapeArticlesClientTest(NoQueryStringTestMixin, ClientLinksTestMixin,
        unittest.TestCase):
    page_link_map = {
            '/':[
                ('/articles/1', 'ann link 1'),
                ('/articles/1', 'ann link 2'),
                ],
            }
    check_code = '<!-- announcements place -->'
    server_format = 'php'
    cookies = {'sape_cookie': 'user123456789'}

    def create_servers(cls):
        template_test_server = SapeArticlesTemplateTestServer()
        template_urls = [('1', template_test_server.url)]
        return [SapeArticlesIndexTestServer(template_urls=template_urls),
                SapeArticlesArticleTestServer(),
                template_test_server]
    create_servers = classmethod(create_servers)

    def new_client(self, **kw):
        kw.setdefault('user', 'user123456789')
        kw.setdefault('index_db_driver', ('mem',))
        kw.setdefault('article_db_driver', ('mem',))
        kw.setdefault('image_db_driver', ('mem',))
        kw.setdefault('template_db_driver', ('mem',))
        kw.setdefault('index_server_list', [
            self.servers[0].url.replace('%', '%%')])
        kw.setdefault('article_server_list', [
            self.servers[1].url.replace('%', '%%')])
        if kw.get('broken_server', False):
            kw['index_server_list'] = ['file:///not_exists']
            kw['article_server_list'] = ['file:///not_exists']
        return SapeArticlesClient(**kw)

    def test_handle_request(self):
        client = self.new_client()
        request = self.new_request(uri='/articles/1')
        response = client.handle_request(request)
        self.assertEqual(response.status, 200)
        mime = response.headers['Content-Type'].split(';')[0]
        self.assertEqual(mime, 'text/html')
        title_found = '<title>The article title</title>' in response.body
        self.assertEqual(title_found, True)
        body_found = '<p>The article ' in response.body
        self.assertEqual(body_found, True)
        extlink_re = re.compile(r'<noindex><a[^>]+href='
                r'"http://external-link.com"[^>]*>'
                r'External link</a></noindex>', re.S)
        m = extlink_re.search(response.body)
        self.assertEqual(m is not None, True)
        self.assertEqual('rel="nofollow"' in m.group(0), True)
        client.refresh_db(self.new_request(uri='/'))

class LinkFeedClientXTestMixin(NoQueryStringTestMixin, ClientLinksTestMixin):
    """
    Base test case to test LinkFeedClient independent of server format.
    """
    page_link_map = {
            '/':[
                ('http://example1.com', 'example text 1'),
                ('http://example2.com', 'example text 2'),
                ],
            '/path/1':[
                ('http://example1.com', 'example text 1'),
                ('http://example2.com', 'example text 2'),
                ('http://example3.com', 'example text 3'),
                ('http://example4.com', 'example text 4'),
                ],
            }
    check_code = '<!--12345-->'
    html_links_delim_pattern = r'\. '
    server_format = None
    bot_ip = '123.45.67.89'

    def create_servers(cls):
        return [LinkFeedTestServer(server_format=cls.server_format)]
    create_servers = classmethod(create_servers)

    def new_client(self, **kw):
        kw.setdefault('user', 'user123456789')
        kw.setdefault('db_driver', ('mem',))
        kw.setdefault('server_list', [
            self.servers[0].url.replace('%', '%%')])
        kw.setdefault('server_format', self.server_format)
        if kw.get('broken_server', False):
            kw['server_list'] = ['file:///not_exists']
        return LinkFeedClient(**kw)

class LinkFeedClientPHPTest(LinkFeedClientXTestMixin, unittest.TestCase):
    """
    Test LinkFeedClient with php server format.
    """
    server_format = 'php'

class LinkFeedClientXMLTest(LinkFeedClientXTestMixin, unittest.TestCase):
    """
    Test LinkFeedClient with xml server format.
    """
    server_format = 'xml'

class TrustLinkClientTest(NoQueryStringTestMixin, ClientLinksTestMixin,
        unittest.TestCase):
    page_link_map = {
            '/':[
                ('http://example1.com', 'anchor 1'),
                ('http://example2.com', 'anchor 2'),
                ],
            '/path/1':[
                ('http://example1.com', 'anchor 1'),
                ('http://example2.com', 'anchor 2'),
                ('http://example3.com', 'anchor 3'),
                ('http://example4.com', 'anchor 4'),
                ],
            }
    check_code = '<!--12345-->'
    html_links_delim_pattern = r'\. '
    server_format = None
    bot_ip = '123.45.67.89'

    def create_servers(cls):
        return [TrustLinkTestServer()]
    create_servers = classmethod(create_servers)

    def new_client(self, **kw):
        kw.setdefault('user', 'user123456789')
        kw.setdefault('db_driver', ('mem',))
        kw.setdefault('server_list', [
            self.servers[0].url.replace('%', '%%')])
        kw.setdefault('link_template',
                '<a href="%(href)s">%(anchor)s</a> %(text)s')
        if kw.get('broken_server', False):
            kw['server_list'] = ['file:///not_exists']
        return TrustLinkClient(**kw)
