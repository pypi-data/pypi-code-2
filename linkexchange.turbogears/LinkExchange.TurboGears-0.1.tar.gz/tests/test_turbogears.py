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
        '/index': [
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
        '/': [
            'Learn more about <a href="http://example.com">TurboGears</a>',
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

class LinkExchangeTurboGearsTest(unittest.TestCase):
    linkexchange_cfg = """
[options]
as_kid_xml = true

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

        # search for tg-admin
        tg_admin = search_script('tg-admin')
        assert tg_admin
        cls.tg_admin_run = get_run_args(tg_admin)

        cls.prevdir = os.getcwd()
        cls.topdir = tempfile.mkdtemp()
        os.chdir(cls.topdir)

        # call tg-admin to create project
        retcode = os.spawnv(os.P_WAIT, cls.tg_admin_run[0],
                cls.tg_admin_run + ['quickstart',
                    '--sqlobject', '--identity',
                    '--package=testprj', 'TestProj'])
        assert retcode == 0

        cls.projectdir = os.path.join(cls.topdir, 'TestProj')
        os.chdir(cls.projectdir)

        cls.sape_server = MySapeTestServer()
        cls.sape_context_server = MySapeContextTestServer()
        cls.sape_art_template_server = MySapeArticlesTemplateTestServer()
        template_urls = [('1', cls.sape_art_template_server.url)]
        cls.sape_art_index_server = MySapeArticlesIndexTestServer(
                template_urls=template_urls)
        cls.sape_art_article_server = MySapeArticlesArticleTestServer()

        q = lambda s: s.replace('%', '%%')
        open(os.path.join('linkexchange.cfg'),
                'w').write(cls.linkexchange_cfg % {
            'sape_server': q(cls.sape_server.url),
            'sape_context_server': q(cls.sape_context_server.url),
            'sape_art_index_server': q(cls.sape_art_index_server.url),
            'sape_art_article_server': q(cls.sape_art_article_server.url),
            })

        start_py = open('start-testprj.py').read()
        start_py = re.compile(r'^((#[^\r\n]*[\r\n]+)*(""".+?"""[\r\n]+)?)',
                re.S).sub("\\1__requires__ = 'TurboGears'\n", start_py)
        open('start-testprj.py', 'w').write(start_py)

        cls.host, cls.port = ('127.0.0.1', 8000)

        dev_cfg = open('dev.cfg').read()
        dev_cfg = re.compile(r'^#\s*(server.socket_port\s*=\s*).*$',
                re.M).sub(lambda m: m.group(1) + str(cls.port), dev_cfg)
        open('dev.cfg', 'w').write(dev_cfg)

        app_cfg_path = os.path.join('testprj', 'config', 'app.cfg')
        app_cfg = open(app_cfg_path).read()
        app_cfg = re.compile(r'[\r\n]+package\s*=[^\r\n]+[\r\n]+',
                0).sub(lambda m: m.group(0) + ('linkexchange.config = '
                    '"%(top_level_dir)s/../linkexchange.cfg"\n'), app_cfg)
        open(app_cfg_path, 'w').write(app_cfg)

        init_py_path = os.path.join('testprj', '__init__.py')
        init_py = open(init_py_path).read()
        init_py += 'import turbogears\n'
        init_py += 'from linkexchange.turbogears import support as lx_support\n'
        init_py += 'turbogears.view.variable_providers.append(lx_support.add_stdvars)\n'
        open(init_py_path, 'w').write(init_py)

        controllers_py_path = os.path.join('testprj', 'controllers.py')
        controllers_py = open(controllers_py_path).read()
        controllers_py = re.compile(r'class Root[^:]*:[\r\n]',
                0).sub(lambda m: "from linkexchange.turbogears.controllers "
                        "import LinkExchangeHandler\n" + m.group(0) +
                        "    articles = LinkExchangeHandler()\n", controllers_py)
        open(controllers_py_path, 'w').write(controllers_py)

        master_kid_path = os.path.join('testprj', 'templates', 'master.kid')
        master_kid = open(master_kid_path).read()
        master_kid = re.compile(r'<div py:replace="\[item.text\]'
                r'\+item\[:\]">page content</div>',
                re.M).sub("""
                <div py:if="hasattr(tg, 'linkexchange_filter')"
                     py:replace="tg.linkexchange_filter([item.text]+item[:])"/>
                <div py:if="not hasattr(tg, 'linkexchange_filter')"
                     py:replace="[item.text]+item[:]"/>
                <div py:if="hasattr(tg, 'linkexchange_blocks')" 
                     py:replace="tg.linkexchange_blocks[0]"/>""", master_kid)
        open(master_kid_path, 'w').write(master_kid)

        cls.start_run = [sys.executable, 'start-testprj.py']
        
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
        tg_server = WebAppProcess(self.start_run, (self.host, self.port))
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
                    '<a href="http://example.com">TurboGears</a>' in body, True)
            self.assertEqual(
                    '<a href="/articles/1">example announcement link</a>' in body, True)

            body = urllib2.urlopen(baseurl + '/index').read()

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
            tg_server.terminate()
            tg_server.wait()
