import unittest
import sys
import os
import re
import tempfile
import shutil
import urllib2
import time
import ConfigParser

from linkexchange.clients.sape import SapeTestServer
from linkexchange.clients.sape import SapeArticlesIndexTestServer
from linkexchange.clients.sape import SapeArticlesArticleTestServer
from linkexchange.clients.sape import SapeArticlesTemplateTestServer
from linkexchange.tests import WebAppProcess

class MySapeTestServer(SapeTestServer):
    data = {
        '/testenv': [
            '<a href="http://example1.com">example text 1</a>',
            '<a href="http://example2.com">example text 2</a>',
            ],
        '/testenv/timeline': [
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
        '/testenv': [
            '<a href="http://example.com">Trac</a> is',
            ],
        '__sape_new_url__': '<!--12345-->',
        }

class MySapeArticlesIndexTestServer(SapeArticlesIndexTestServer):
    data = {
            'announcements': {
                '/testenv': [
                    '<a href="/testenv/articles/1">example announcement link</a>'],
                },
            'articles': {
                '/testenv/articles/1': {
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

class LinkExchangeTracTest(unittest.TestCase):
    linkexchange_cfg = """
[options]
content_filtering = true
handler_path_match = ^/articles/

[client-1]
type = sape
user = user12345
db_driver.type = shelve
db_driver.filename = %%(envdir)s/sape-XXX.db
server-1 = %(sape_server)s

[client-2]
type = sape_context
user = user12345
db_driver.type = shelve
db_driver.filename = %%(envdir)s/sape_context-XXX.db
server-1 = %(sape_context_server)s

[client-3]
type = sape_articles
user = user12345
index_db_driver.type = shelve
index_db_driver.filename = %%(envdir)s/sape-articles-index-XXX.db
article_db_driver.type = shelve
article_db_driver.filename = %%(envdir)s/sape-articles-article-XXX.db
image_db_driver.type = shelve
image_db_driver.filename = %%(envdir)s/sape-articles-image-XXX.db
template_db_driver.type = shelve
template_db_driver.filename = %%(envdir)s/sape-articles-template-XXX.db
index_server-1 = %(sape_art_index_server)s
article_server-1 = %(sape_art_article_server)s

[formatter-1]
type = inline
count = none
"""
    site_html = """
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:py="http://genshi.edgewall.org/" py:strip="">
    <body py:match="body" py:attrs="select('@*')">
        ${select('*|text()')}
        <div py:if="defined('linkexchange_blocks')" py:strip="True">
            ${Markup(linkexchange_blocks[0])}
        </div>
    </body>
</html>
"""

    def setUpClass(cls):
        def search_script(script_name):
            pathname = None
            dirs = filter(lambda x: x, os.getenv('PYTHONPATH', '').split(os.pathsep))
            dirs.extend(
                    filter(lambda x: x, os.getenv('PATH', '').split(os.pathsep)))
            dirs.append(os.path.dirname(sys.executable))
            dirs.append(os.path.join(os.path.dirname(sys.executable), 'Scripts'))
            files = [script_name + '.py', script_name + '-script.py',
                    script_name, script_name + '.exe']
            for d in dirs:
                for f in files:
                    p = os.path.join(d, f)
                    if os.path.exists(p):
                        pathname = p
                        break
                if pathname:
                    break
            return pathname

        def get_run_args(script_path):
            if script_path.endswith('.py'):
                run_args = [sys.executable, script_path]
            else:
                run_args = [script_path]
            return run_args

        # search for trac-admin
        trac_admin = search_script('trac-admin')
        assert trac_admin
        cls.trac_admin_run = get_run_args(trac_admin)

        # search for tracd
        tracd = search_script('tracd')
        assert tracd
        cls.tracd_run = get_run_args(tracd)

        cls.prevdir = os.getcwd()
        cls.topdir = tempfile.mkdtemp()
        os.chdir(cls.topdir)

        # call trac-admin to create environment
        retcode = os.spawnv(os.P_WAIT, cls.trac_admin_run[0],
                cls.trac_admin_run + ['testenv', 'initenv',
                    'Test Project', 'sqlite:db/trac.db', 'svn', ''])
        assert retcode == 0

        cls.envdir = os.path.join(cls.topdir, 'testenv')
        os.chdir(cls.envdir)

        cls.sape_server = MySapeTestServer()
        cls.sape_context_server = MySapeContextTestServer()
        cls.sape_art_template_server = MySapeArticlesTemplateTestServer()
        template_urls = [('1', cls.sape_art_template_server.url)]
        cls.sape_art_index_server = MySapeArticlesIndexTestServer(
                template_urls=template_urls)
        cls.sape_art_article_server = MySapeArticlesArticleTestServer()

        q = lambda s: s.replace('%', '%%')
        open(os.path.join('conf', 'linkexchange.cfg'),
                'w').write(cls.linkexchange_cfg % {
            'sape_server': q(cls.sape_server.url),
            'sape_context_server': q(cls.sape_context_server.url),
            'sape_art_index_server': q(cls.sape_art_index_server.url),
            'sape_art_article_server': q(cls.sape_art_article_server.url),
            })

        if not os.path.exists('templates'):
            os.mkdir('templates')
        open(os.path.join('templates', 'site.html'), 'w').write(cls.site_html)

        trac_ini = os.path.join('conf', 'trac.ini')
        cfg = ConfigParser.ConfigParser()
        cfg.readfp(open(trac_ini))
        if not cfg.has_section('components'):
            cfg.add_section('components')
        cfg.set('components',
                'linkexchange.trac.plugin.linkexchangeplugin', 'enabled')
        cfg.write(open(trac_ini, 'w'))

        cls.host, cls.port = ('127.0.0.1', 8000)
        
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
        trac_server = WebAppProcess(self.tracd_run +
                ['--port', str(self.port), self.envdir],
                (self.host, self.port))
        try:
            baseurl = 'http://%s:%d' % (self.host, self.port)
            search = lambda pat, s: bool(re.search(pat, s))

            body = urllib2.urlopen(baseurl + '/testenv').read()
            self.assertEqual(search(r'<html\b', body), True)

            self.assertEqual(
                    '<a href="http://example1.com">example text 1</a>' in body, True)
            self.assertEqual(
                    '<a href="http://example2.com">example text 2</a>' in body, True)
            self.assertEqual(
                    '<a href="http://example.com">Trac</a>' in body, True)
            self.assertEqual(
                    '<a href="/testenv/articles/1">example announcement link</a>' in body, True)

            body = urllib2.urlopen(baseurl + '/testenv/timeline').read()

            self.assertEqual(
                    '<a href="http://example1.com">example text 1</a>' in body, True)
            self.assertEqual(
                    '<a href="http://example2.com">example text 2</a>' in body, True)
            self.assertEqual(
                    '<a href="http://example3.com">example text 3</a>' in body, True)
            self.assertEqual(
                    '<a href="http://example4.com">example text 4</a>' in body, True)

            body = urllib2.urlopen(baseurl + '/testenv/articles/1').read()
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
            trac_server.terminate()
            trac_server.wait()

