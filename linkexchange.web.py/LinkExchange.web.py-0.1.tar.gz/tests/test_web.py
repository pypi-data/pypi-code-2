import unittest
import sys
import os
import re
import tempfile
import shutil
import urllib2
import time

from linkexchange.clients.sape import SapeTestServer
from linkexchange.clients.sape import SapeArticlesIndexTestServer
from linkexchange.clients.sape import SapeArticlesArticleTestServer
from linkexchange.clients.sape import SapeArticlesTemplateTestServer
from linkexchange.tests import WebAppProcess

class MySapeTestServer(SapeTestServer):
    data = {
        '/': [
            '<a href="http://example1.com">example text 1</a>',
            '<a href="http://example2.com">example text 2</a>',
            ],
        '/path/1': [
            '<a href="http://example1.com">example text 1</a>',
            '<a href="http://example2.com">example text 2</a>',
            '<a href="http://example3.com">example text 3</a>',
            '<a href="http://example4.com">example text 4</a>',
            ],
        '__sape_new_url__': '<!--12345-->',
        '__sape_delimiter__': '. ',
        }

class MySapeContextTestServer(SapeTestServer):
    data = {
        '/?name=x': [
            'I just wanted <a href="http://example.com">to say</a>',
            ],
        '__sape_new_url__': '<!--12345-->',
        }

class MySapeArticlesIndexTestServer(SapeArticlesIndexTestServer):
    data = {
            'announcements': {
                '/': [
                    '<a href="/articles/1">example announcement link</a>'],
                },
            'articles': {
                '/articles/1': {
                    'id': '1',
                    'date_updated': '0',
                    'template_id': '1',
                    },
                },
            'images': {},
            'templates': {
                '1': {
                    'lifetime': '3600',
                    },
                },
            'template_fields': [
                'title', 'keywords', 'header', 'body',
                ],
            'template_required_fields': [
                'title', 'keywords', 'header', 'body',
                ],
            'ext_links_allowed': [],
            'checkCode': '<!--12345-->',
            'announcements_delimiter': '|',
            }

class MySapeArticlesArticleTestServer(SapeArticlesArticleTestServer):
    data = {
            'date_updated': '0',
            'title': 'The article title',
            'keywords': 'The keywords',
            'header': 'The article header',
            'body': '<p>The article <a href="http://example.com">body</a>.</p>',
            }

class MySapeArticlesTemplateTestServer(SapeArticlesTemplateTestServer):
    raw_data = """
    <html>
      <head>
        <title>{title}</title>
        <meta name="keywords" content="{keywords}"/>
      </head>
    <body>
      <h1>{header}</h1>
      {body}
    </body>
    </html>
    """

class LinkExchangeWebPyTest(unittest.TestCase):
    linkexchange_cfg = """
[client-1]
type = sape
user = user12345
db_driver.type = shelve
db_driver.filename = %%(basedir)s/sape-XXX.db
server-1 = %(sape_server)s

[client-2]
type = sape_context
user = user12345
db_driver.type = shelve
db_driver.filename = %%(basedir)s/sape_context-XXX.db
server-1 = %(sape_context_server)s

[client-3]
type = sape_articles
user = user12345
index_db_driver.type = shelve
index_db_driver.filename = %%(basedir)s/sape-articles-index-XXX.db
article_db_driver.type = shelve
article_db_driver.filename = %%(basedir)s/sape-articles-article-XXX.db
image_db_driver.type = shelve
image_db_driver.filename = %%(basedir)s/sape-articles-image-XXX.db
template_db_driver.type = shelve
template_db_driver.filename = %%(basedir)s/sape-articles-template-XXX.db
index_server-1 = %(sape_art_index_server)s
article_server-1 = %(sape_art_article_server)s

[formatter-1]
type = inline
count = none
"""
    code_py = """
import web

from linkexchange.web import support as lx_support

urls = (
    '/articles/.*', 'linkexchange_handler',
    '/(.*)', 'hello',
)

web.config.linkexchange_config = 'linkexchange.cfg'
app = web.application(urls, globals())
lx_support.configure(app)
render = web.template.render('templates/', globals=globals())

class hello:        
    def GET(self, name):
        i = web.input(name=None)
        return lx_support.content_filter(app, render.index(i.name))

linkexchange_handler = lx_support.linkexchange_handler

if __name__ == "__main__":
    app.run()
"""

    index_html = """\
$def with (name)
<html>
<body>
$if name:
    I just wanted to say <em>hello</em> to $name.
$else:
    <em>Hello</em>, world!
$:web.ctx.linkexchange_blocks[0]
</body>
<html>
"""

    def setUpClass(cls):
        cls.prevdir = os.getcwd()
        cls.topdir = tempfile.mkdtemp()
        os.chdir(cls.topdir)

        cls.sape_server = MySapeTestServer()
        cls.sape_context_server = MySapeContextTestServer()
        cls.sape_art_template_server = MySapeArticlesTemplateTestServer()
        template_urls = [('1', cls.sape_art_template_server.url)]
        cls.sape_art_index_server = MySapeArticlesIndexTestServer(
                template_urls=template_urls)
        cls.sape_art_article_server = MySapeArticlesArticleTestServer()

        os.mkdir('templates')
        open(os.path.join('templates', 'index.html'),
                'w').write(cls.index_html)

        q = lambda s: s.replace('%', '%%')
        open(os.path.join('linkexchange.cfg'),
                'w').write(cls.linkexchange_cfg % {
            'sape_server': q(cls.sape_server.url),
            'sape_context_server': q(cls.sape_context_server.url),
            'sape_art_index_server': q(cls.sape_art_index_server.url),
            'sape_art_article_server': q(cls.sape_art_article_server.url),
            })

        open('code.py', 'w').write(cls.code_py)

        cls.host, cls.port = ('127.0.0.1', 8000)
        cls.code_run = [sys.executable, 'code.py',
                '%s:%d' % (cls.host, cls.port)]
    setUpClass = classmethod(setUpClass)

    def tearDownClass(cls):
        del cls.sape_server
        del cls.sape_context_server
        del cls.sape_art_index_server
        del cls.sape_art_article_server
        del cls.sape_art_template_server
        os.chdir(cls.prevdir)
        shutil.rmtree(cls.topdir)
    tearDownClass = classmethod(tearDownClass)

    def test_run(self):
        success = False
        web_server = WebAppProcess(self.code_run, (self.host, self.port))
        try:
            baseurl = 'http://%s:%d' % (self.host, self.port)
            search = lambda pat, s: bool(re.search(pat, s))

            body = urllib2.urlopen(baseurl + '/').read()
            self.assertEqual(search(r'<html\b', body), True)

            self.assertEqual(
                    '<a href="http://example1.com">example text 1</a>' in body, True)
            self.assertEqual(
                    '<a href="http://example2.com">example text 2</a>' in body, True)
            self.assertEqual(
                    '<a href="/articles/1">example announcement link</a>' in body, True)

            body = urllib2.urlopen(baseurl + '/?name=x').read()
            self.assertEqual(
                    '<a href="http://example.com">to say</a>' in body, True)

            body = urllib2.urlopen(baseurl + '/path/1').read()

            self.assertEqual(
                    '<a href="http://example1.com">example text 1</a>' in body, True)
            self.assertEqual(
                    '<a href="http://example2.com">example text 2</a>' in body, True)
            self.assertEqual(
                    '<a href="http://example3.com">example text 3</a>' in body, True)
            self.assertEqual(
                    '<a href="http://example4.com">example text 4</a>' in body, True)

            body = urllib2.urlopen(baseurl + '/articles/1').read()
            self.assertEqual(
                    '<title>The article title</title>' in body, True)
            self.assertEqual(
                    '<h1>The article header</h1>' in body, True)
            self.assertEqual(
                    '<a href="http://example.com">' in body, True)

            success = True
        finally:
            if not success:
                time.sleep(3)
            sys.stdout.flush()
            web_server.terminate()
            web_server.wait()
