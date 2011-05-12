import unittest
import sys
import os
import re
import tempfile
import shutil
import urllib2
import time
import tarfile

from linkexchange.clients.sape import SapeTestServer
from linkexchange.clients.sape import SapeArticlesIndexTestServer
from linkexchange.clients.sape import SapeArticlesArticleTestServer
from linkexchange.clients.sape import SapeArticlesTemplateTestServer
from linkexchange.tests import WebAppProcess

class MySapeTestServer(SapeTestServer):
    data = {
        '/MyPage1': [
            '<a href="http://example1.com">example text 1</a>',
            '<a href="http://example2.com">example text 2</a>',
            ],
        '/MyPage2?xxx': [
            '<a href="http://example1.com">example text 1</a>',
            '<a href="http://example2.com">example text 2</a>',
            '<a href="http://example3.com">example text 3</a>',
            '<a href="http://example4.com">example text 4</a>',
            ],
        '/Question%3F': [
            'Test <a href="http://example.com">question sign</a> in URI.',
            ],
        '/Unicode%20%C2%ABTest%C2%BB': [
            'Test <a href="http://example.com">Unicode</a> characters.',
            ],
        '__sape_new_url__': '<!--12345-->',
        '__sape_delimiter__': '. ',
        }

class MySapeContextTestServer(SapeTestServer):
    data = {
        '/MyPage1': [
            'Test <a href="http://example1.com">context</a> link 1.',
            ],
        '/MyPage2?xxx': [
            'Test <a href="http://example2.com">context</a> link 2.',
            ],
        '__sape_new_url__': '<!--12345-->',
        }

class MySapeArticlesIndexTestServer(SapeArticlesIndexTestServer):
    data = {
            'announcements': {
                '/MyPage1': [
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

class LinkExchangeMoinMoinXTestCaseMixin:
    moin_source = None
    source_path = [os.path.dirname(__file__), os.getcwd()]

    wikiserverconfig_16 = """
import os
from MoinMoin.server.server_standalone import StandaloneConfig
class Config(StandaloneConfig):
    name = 'moin'
    docs = os.path.join(%(moinpath)s, 'wiki', 'htdocs')
    port = %(port)s
    interface = %(host)s
"""
    wikiserverconfig_17 = """
from MoinMoin.script.server.standalone import DefaultConfig
class Config(DefaultConfig):
    port = %(port)s
    interface = %(host)s
"""
    wikiserverconfig_18 = wikiserverconfig_17
    wikiserverconfig_19 = """
from MoinMoin.script.server.standalone import DefaultConfig
class Config(DefaultConfig):
    hostname = %(host)s
    port = %(port)s
    debug = 'off'
"""
    wikiconfig_16 = """
import sys, os
from MoinMoin.config.multiconfig import DefaultConfig
class Config(DefaultConfig):
    moinmoin_dir = %(moinpath)s
    data_dir = os.path.join(moinmoin_dir, 'wiki', 'data')
    data_underlay_dir = os.path.join(moinmoin_dir, 'wiki', 'underlay')
    DesktopEdition = True
    acl_rights_default = u"All:read,write,delete,revert,admin"
    surge_action_limits = None
    sitename = u'MoinMoin DesktopEdition'
    logo_string = u'<img src="/moin_static160/common/moinmoin.png" alt="MoinMoin Logo">'
    page_front_page = u'FrontPage'
    page_credits = [
        '<a href="http://moinmo.in/">MoinMoin DesktopEdition Powered</a>',
        '<a href="http://moinmo.in/Python">Python Powered</a>',
    ]
"""
    wikiconfig_17 = """
import sys, os
from MoinMoin.config.multiconfig import DefaultConfig
class Config(DefaultConfig):
    moinmoin_dir = %(moinpath)s
    data_dir = os.path.join(moinmoin_dir, 'wiki', 'data')
    data_underlay_dir = os.path.join(moinmoin_dir, 'wiki', 'underlay')
    DesktopEdition = True
    acl_rights_default = u"All:read,write,delete,revert,admin"
    surge_action_limits = None
    sitename = u'MoinMoin DesktopEdition'
    page_front_page = u'FrontPage'
    secrets = 'This string is NOT a secret, please make up your own, long, random secret string!'
"""
    wikiconfig_18 = wikiconfig_17
    wikiconfig_19 = """
import sys, os
from MoinMoin.config import multiconfig, url_prefix_static
class Config(multiconfig.DefaultConfig):
    wikiconfig_dir = %(moinpath)s
    instance_dir = os.path.join(%(moinpath)s, 'wiki')
    data_dir = os.path.join(instance_dir, 'data', '')
    data_underlay_dir = os.path.join(instance_dir, 'underlay', '')
    DesktopEdition = True
    acl_rights_default = u"All:read,write,delete,revert,admin"
    surge_action_limits = None
    sitename = u'MoinMoin DesktopEdition'
    logo_string = u'<img src="%%s/common/moinmoin.png" alt="MoinMoin Logo">' %% url_prefix_static
    secrets = 'This string is NOT a secret, please make up your own, long, random secret string!'
"""
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

    modern_custom_py = """
from MoinMoin.theme.modern import Theme as ThemeBase
from MoinMoin import wikiutil
from MoinMoin.macro import Macro

class\x20Theme(ThemeBase):
    name = 'modern_custom'

    def footer(self, d, **keywords):
        html = [
            self.linkexchange_block(0, d),
            ThemeBase.footer(self, d, **keywords),
        ]
        return u''.join(html)

    def\x20linkexchange_block(self, num, d):
        request = self.request
        try:
            macro = d['macro']
        except KeyError:
            Parser = wikiutil.searchAndImportPlugin(request.cfg,
                    "parser", request.cfg.default_markup or 'wiki')
            parser = Parser(u'', request)
            macro = d['macro'] = Macro(parser)
        return macro.execute('LinkExchangeBlock', num)

    def send_title(self, text, **keywords):
        force_title = self.request.getPragma('title')
        if force_title:
            text = force_title
        ThemeBase.send_title(self, text, **keywords)
"""
    pages_content = [
            ('MyPage1', '\n'.join([
                "#format linkexchange_wiki",
                "",
                "= My Page 1 =",
                "Page content is: Test context link 1.",
                "And some other text."
                ])),
            ('MyPage2', '\n'.join([
                "#format wiki",
                "",
                "= My Page 2 =",
                "{{{#!linkexchange_wiki",
                "Page content is: Test context link 2.",
                "And some other text.",
                "}}}",
                ])),
            ('Question(3f)', '\n'.join([
                "= Test Question Sign =",
                ])),
            ('Unicode(20c2ab)Test(c2bb)', '\n'.join([
                "= Test Unicode =",
                ])),
            ('ArticleTemplate1', '\n'.join([
                "#pragma title {title}",
                "#pragma keywords {keywords}",
                "",
                "= {header} =",
                "{body}",
                ])),
            ]

    def setUpClass(cls):
        def make_page(pagename, content):
            pagedir = os.path.join('wiki', 'data', 'pages', pagename)
            os.mkdir(pagedir)
            os.mkdir(os.path.join(pagedir, 'cache'))
            os.mkdir(os.path.join(pagedir, 'revisions'))
            open(os.path.join(pagedir, 'current'), 'w').write("00000001")
            open(os.path.join(pagedir, 'revisions', '00000001'),
                    'w').write(content)
            open(os.path.join(pagedir, 'edit-log'), 'w').write("")

        # search for MoinMoin source archive
        moin_source_path = None
        for d in cls.source_path:
            p = os.path.join(d, cls.moin_source)
            if os.path.exists(p):
                moin_source_path = p
                break

        assert moin_source_path is not None

        # create test top directory
        cls.prevdir = os.getcwd()
        cls.topdir = tempfile.mkdtemp()
        os.chdir(cls.topdir)

        tar = tarfile.open(moin_source_path)
        for x in tar.getmembers():
            tar.extract(x)
        tar.close()

        # chdir into source top directory
        os.chdir(re.sub(r'\.tar(\.(gz|bz2))?$', '', cls.moin_source))

        # determine MoinMoin version
        moin_version = None
        for line in open('PKG-INFO'):
            if line.startswith('Version:'):
                moin_version = tuple([int(x) for x in line[8:].strip().split('.')])
                break
        assert moin_version is not None

        cls.sape_server = MySapeTestServer()
        cls.sape_context_server = MySapeContextTestServer()
        cls.sape_art_index_server = MySapeArticlesIndexTestServer(
                template_urls=[('1', '/ArticleTemplate1')])
        cls.sape_art_article_server = MySapeArticlesArticleTestServer()

        # write LinkExchange plugins
        macrodir = os.path.join('wiki', 'data', 'plugin', 'macro')
        open(os.path.join(macrodir, 'LinkExchangeBlock.py'), 'w').write(
                "from linkexchange.MoinMoin.macro.LinkExchangeBlock import *\n")

        parserdir = os.path.join('wiki', 'data', 'plugin', 'parser')
        open(os.path.join(parserdir, 'linkexchange_wiki.py'), 'w').write(
                "from linkexchange.MoinMoin.parser.linkexchange_wiki import *\n")

        actiondir = os.path.join('wiki', 'data', 'plugin', 'action')
        open(os.path.join(actiondir, 'LinkExchangeHandler.py'), 'w').write(
                "from linkexchange.MoinMoin.action.LinkExchangeHandler import *\n")

        themedir = os.path.join('wiki', 'data', 'plugin', 'theme')
        open(os.path.join(themedir, 'modern_custom.py'),
                'w').write(cls.modern_custom_py)

        # create wiki configuration file
        cfgdic = dict(
                moinpath=repr(os.path.normpath(os.getcwd())),
                host=repr('127.0.0.1'), port=repr(8000))
        cfg = open('wikiserverconfig.py', 'w')
        if moin_version < (1, 7):
            cfg.write(cls.wikiserverconfig_16 % cfgdic)
        elif moin_version < (1, 8):
            cfg.write(cls.wikiserverconfig_17 % cfgdic)
        elif moin_version < (1, 9):
            cfg.write(cls.wikiserverconfig_18 % cfgdic)
        elif moin_version >= (1, 9):
            cfg.write(cls.wikiserverconfig_19 % cfgdic)
        cfg.close()
        cfg = open('wikiconfig.py', 'w')
        if moin_version < (1, 7):
            cfg.write(cls.wikiconfig_16 % cfgdic)
        elif moin_version < (1, 8):
            cfg.write(cls.wikiconfig_17 % cfgdic)
        elif moin_version < (1, 9):
            cfg.write(cls.wikiconfig_18 % cfgdic)
        elif moin_version >= (1, 9):
            cfg.write(cls.wikiconfig_19 % cfgdic)
        cfg.write("    theme_default = 'modern_custom'\n")
        cfg.write("    linkexchange_config = %s\n" % (
            repr(os.path.join(os.path.normpath(os.getcwd()),
                'linkexchange.cfg'))))
        cfg.close()

        # create LinkExchange configuration file
        q = lambda s: s.replace('%', '%%')
        open('linkexchange.cfg', 'w').write(cls.linkexchange_cfg % {
            'sape_server': q(cls.sape_server.url),
            'sape_context_server': q(cls.sape_context_server.url),
            'sape_art_index_server': q(cls.sape_art_index_server.url),
            'sape_art_article_server': q(cls.sape_art_article_server.url),
            })

        for pagename, content in cls.pages_content:
            make_page(pagename, content)

        if moin_version < (1, 7):
            cls.moin_run = [sys.executable, 'moin.py']
        else:
            cls.moin_run = [sys.executable, 'wikiserver.py']
    setUpClass = classmethod(setUpClass)

    def tearDownClass(cls):
        del cls.sape_server
        del cls.sape_context_server
        os.chdir(cls.prevdir)
        shutil.rmtree(cls.topdir)
    tearDownClass = classmethod(tearDownClass)

    def testRun(self):
        success = False
        host, port = ('127.0.0.1', 8000)
        web_server = WebAppProcess(self.moin_run, (host, port))
        try:
            baseurl = 'http://%s:%d' % (host, port)

            body = urllib2.urlopen(baseurl + '/MyPage1').read()
            self.assertEqual('<html>' in body, True)

            self.assertEqual(
                    '<a href="http://example1.com">example text 1</a>' in body, True)
            self.assertEqual(
                    '<a href="http://example2.com">example text 2</a>' in body, True)
            self.assertEqual(
                    'Test <a href="http://example1.com">context</a> link 1.' in body, True)
            self.assertEqual(
                    'Test <a href="http://example2.com">context</a> link 2.' in body, False)
            self.assertEqual(
                    '<a href="/articles/1">example announcement link</a>' in body, True)

            body = urllib2.urlopen(baseurl + '/MyPage2?xxx').read()
            self.assertEqual(
                    '<a href="http://example3.com">example text 3</a>' in body, True)
            self.assertEqual(
                    '<a href="http://example4.com">example text 4</a>' in body, True)
            self.assertEqual(
                    'Test <a href="http://example1.com">context</a> link 1.' in body, False)
            self.assertEqual(
                    'Test <a href="http://example2.com">context</a> link 2.' in body, True)

            body = urllib2.urlopen(baseurl + '/Question%3f').read()
            self.assertEqual(
                    '<a href="http://example.com">question sign</a>' in body, True)

            body = urllib2.urlopen(baseurl + '/Unicode%20%C2%ABTest%C2%BB').read()
            self.assertEqual(
                    '<a href="http://example.com">Unicode</a>' in body, True)

            body = urllib2.urlopen(baseurl +
                    '/?action=LinkExchangeHandler&uri=/articles/1').read()
            search = lambda pat, s: bool(re.search(pat, s))
            self.assertEqual(
                    search(r'<title[^>]*>.*?The article title.*?</title>', body), True)
            self.assertEqual(
                    search('<h1[^>]*>The article header</h1>', body), True)
            self.assertEqual(
                    '<a href="http://example.com">' in body, True)

            success = True
        finally:
            if not success:
                time.sleep(3)
            sys.stdout.flush()
            web_server.terminate()
            retcode = web_server.wait()

if sys.version_info < (2, 6):
    class LinkExchangeMoinMoin16TestCase(LinkExchangeMoinMoinXTestCaseMixin,
            unittest.TestCase):
        moin_source = 'moin-1.6.0.tar.gz'

class LinkExchangeMoinMoin17TestCase(LinkExchangeMoinMoinXTestCaseMixin,
        unittest.TestCase):
    moin_source = 'moin-1.7.0.tar.gz'

class LinkExchangeMoinMoin18TestCase(LinkExchangeMoinMoinXTestCaseMixin,
        unittest.TestCase):
    moin_source = 'moin-1.8.8.tar.gz'

if sys.version_info >= (2, 4):
    class LinkExchangeMoinMoin19TestCase(LinkExchangeMoinMoinXTestCaseMixin,
            unittest.TestCase):
        moin_source = 'moin-1.9.3.tar.gz'
