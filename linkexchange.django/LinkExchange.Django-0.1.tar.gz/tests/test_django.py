import unittest
import sys
import os
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
        '/': [
            'Test <a href="http://example1.com">context</a> link 1.',
            ],
        '/path/1': [
            'Test <a href="http://example2.com">context</a> link 2.',
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

class LinkExchangeDjangoTest(unittest.TestCase):
    settings_py = """
from os.path import dirname, join

DEBUG = True
TEMPLATE_DEBUG = DEBUG
ADMINS = ()
MANAGERS = ADMINS
DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = join(dirname(__file__), 'site.db')
TIME_ZONE = 'Europe/Kiev'
LANGUAGE_CODE = 'ru-ru'
SITE_ID = 1
USE_I18N = True
MEDIA_ROOT = join(dirname(__file__), 'static')
MEDIA_URL = '/static/'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'testprj.urls'

TEMPLATE_DIRS = (
    join(dirname(__file__), 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'linkexchange_django',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'linkexchange_django.context_processors.linkexchange',
    )

LINKEXCHANGE_CONFIG = join(dirname(__file__), 'linkexchange.cfg')
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
type = list
count = 2
class_ = linx
prefix = "-&nbsp;"
suffix = ". "

[formatter-2]
type = inline
count = 2
class_ = linx
delimiter = " | "
prolog = "| "
epilog = " |"

[formatter-3]
type = list
count = none
class_ = linx
prefix = "+&nbsp;"
suffix = ". "
"""
    urls_py = """
from django.conf.urls.defaults import *
urlpatterns = patterns('',
    (r'^articles/\d+$', 'linkexchange_django.views.handle_request'),
    (r'^.*', 'django.views.generic.simple.direct_to_template',
        {'template': 'test.html'}),
)
"""

    test_html = """
{% load linkexchange_tags %}
<html>
<body>

{% linkexchange_filter request %}
<p>
Test context link 1.
</p>
{% endlinkexchange_filter %}

{% with "Test context link 2." as text %}
<p>
{{ text|linkexchange_filter:request }}
</p>
{% endwith %}

<p>Location 1: {{ linkexchange_blocks.0|safe }}</p>
<p>Location 2: {{ linkexchange_blocks.1|safe }}</p>
<p>Location 3: {{ linkexchange_blocks.2|safe }}</p>

</body>
<html>
"""

    def setUpClass(cls):
        cls.prevdir = os.getcwd()
        cls.topdir = tempfile.mkdtemp()
        os.chdir(cls.topdir)

        # search for django-admin
        django_admin = None
        dirs = filter(lambda x: x, os.getenv('PATH', '').split(os.pathsep))
        dirs.append(os.path.dirname(sys.executable))
        dirs.append(os.path.join(os.path.dirname(sys.executable), 'Scripts'))
        files = ['django-admin.py', 'django-admin-script.py',
                'django-admin', 'django-admin.exe']
        for d in dirs:
            for f in files:
                p = os.path.join(d, f)
                if os.path.exists(p):
                    django_admin = p
                    break
            if django_admin:
                break
        assert django_admin
        if django_admin.endswith('.py'):
            django_admin_args = [sys.executable, django_admin]
        else:
            django_admin_args = [django_admin]

        # call django-admin startproject
        os.spawnv(os.P_WAIT, django_admin_args[0],
                django_admin_args + ['startproject', 'testprj'])

        cls.projectdir = os.path.join(cls.topdir, 'testprj')
        os.chdir(cls.projectdir)
        os.mkdir('templates')

        cls.sape_server = MySapeTestServer()
        cls.sape_context_server = MySapeContextTestServer()
        cls.sape_art_template_server = MySapeArticlesTemplateTestServer()
        template_urls = [('1', cls.sape_art_template_server.url)]
        cls.sape_art_index_server = MySapeArticlesIndexTestServer(
                template_urls=template_urls)
        cls.sape_art_article_server = MySapeArticlesArticleTestServer()

        open('settings.py', 'w').write(cls.settings_py)
        q = lambda s: s.replace('%', '%%')
        open('linkexchange.cfg', 'w').write(cls.linkexchange_cfg % {
            'sape_server': q(cls.sape_server.url),
            'sape_context_server': q(cls.sape_context_server.url),
            'sape_art_index_server': q(cls.sape_art_index_server.url),
            'sape_art_article_server': q(cls.sape_art_article_server.url),
            })
        open('urls.py', 'w').write(cls.urls_py)
        open(os.path.join('templates', 'test.html'), 'w').write(cls.test_html)

        cls.manage_py = [sys.executable, 'manage.py']
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

    def test_test(self):
        retcode = os.spawnv(os.P_WAIT, self.manage_py[0],
                self.manage_py + ['test', 'linkexchange_django'])
        self.assertEqual(retcode, 0)

    def test_validate(self):
        retcode = os.spawnv(os.P_WAIT, self.manage_py[0],
                self.manage_py + ['validate'])
        self.assertEqual(retcode, 0)

    def test_lxrefresh(self):
        retcode = os.spawnv(os.P_WAIT, self.manage_py[0],
                self.manage_py + ['syncdb', '--noinput'])
        self.assertEqual(retcode, 0)
        retcode = os.spawnv(os.P_WAIT, self.manage_py[0],
                self.manage_py + ['lxrefresh',
                    '--host=%s:%d' % (self.host, self.port)])
        self.assertEqual(retcode, 0)

    def test_run(self):
        os.spawnv(os.P_WAIT, self.manage_py[0],
                self.manage_py + ['syncdb', '--noinput'])

        success = False
        django_server = WebAppProcess(self.manage_py +
                ['runserver', str(self.port)], (self.host, self.port))
        try:
            baseurl = 'http://%s:%d' % (self.host, self.port)

            body = urllib2.urlopen(baseurl + '/').read()
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

            body = urllib2.urlopen(baseurl + '/path/1').read()
            self.assertEqual(
                    '<a href="http://example3.com">example text 3</a>' in body, True)
            self.assertEqual(
                    '<a href="http://example4.com">example text 4</a>' in body, True)
            self.assertEqual(
                    'Test <a href="http://example1.com">context</a> link 1.' in body, False)
            self.assertEqual(
                    'Test <a href="http://example2.com">context</a> link 2.' in body, True)

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
            django_server.terminate()
            django_server.wait()
