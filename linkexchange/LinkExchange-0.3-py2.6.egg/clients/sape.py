# LinkExchange - Universal link exchange service client
# Copyright (C) 2009 Konstantin Korikov
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# NOTE: In the context of the Python environment, I interpret "dynamic
# linking" as importing -- thus the LGPL applies to the contents of
# the modules, but make no requirements on code importing these
# modules.

import os.path
import random
import urllib2
import urlparse
import datetime
import re
import xml.sax
import xml.sax.saxutils
import xml.dom
import xml.dom.pulldom
import StringIO
import HTMLParser
import htmlentitydefs
import logging

try:
    set
except NameError:
    from sets import Set as set

import mimetypes
if not mimetypes.inited:
  mimetypes.init()

try:
    import phpserialize
except ImportError:
    phpserialize = None

from linkexchange.clients.base import BaseClient, SimpleFileTestServer
from linkexchange.clients.base import ClientError, \
        ClientNetworkError, ClientDataError, ClientDataAccessError
from linkexchange.clients.base import PageResponse
from linkexchange.utils import is_plugin_specifier, load_plugin
from linkexchange.utils import urlopen_with_timeout, urlopen_errors
from linkexchange.utils import default_user_agent, normalize_uri

log = logging.getLogger('linkexchange.clients.sape')

class SapeLikeTestServer(SimpleFileTestServer):
    data = None
    extra_data = None
    server_format = 'xml'

    def __init__(self, filename=None, data=None, extra_data=None,
            server_format=None):
        if data is not None:
            self.data = data
        if extra_data is not None:
            self.extra_data = extra_data
        if self.extra_data:
            self.data.update(self.extra_data)
        if server_format is not None:
            self.server_format = server_format
        if self.server_format == 'xml':
            raw_data = self.format_data_xml(self.data)
        else:
            raw_data = self.format_data(self.data)
        super(SapeLikeTestServer, self).__init__(filename = filename,
                raw_data = raw_data)

    def format_data(self, data):
        return phpserialize.dumps(data)

    def format_data_xml(self, data):
        return ''

class SapeLikeClient(BaseClient):
    """
    Base class for Sape-like clients.
    """
    db_lifetime = datetime.timedelta(seconds = 3600)
    db_reloadtime = datetime.timedelta(seconds = 600)
    socket_timeout = 6
    force_show_code = True
    server_charset = 'utf-8'
    user_agent = default_user_agent

    def __init__(self, user, **kw):
        """
        SapeLikeClient constructor.
        
        The user is hash code string that assigned to user on link exchange
        service.

        The db_lifetime keyword argument specifies database lifetime. Database
        older than this time interval will be updated be calling refresh_db().
        Value can be datetime.timedelta object or number of seconds as integer
        or float value. None value disables database refreshing, but refreshing
        will occur if database is not exist even if db_lifetime is None.

        The db_reloadtime specifies the time interval during which the database
        refreshing is not happens if the previous attempt to refreshing was
        failed. This prevents remote server overloading when problem on client
        side. Value can be datetime.timedelta object or number of seconds as
        integer or float value. None value means that db_lifetime value should
        be used.

        The socket_timeout is socket timeout for remote connections in seconds.

        @param user: user hash code string on link exchange service
        @keyword db_lifetime: DB lifetime as datetime.timedelta object or
                              number of seconds as numeric value or None
        @keyword db_reloadtime: DB reload time as datetime.timedelta object or
                              number of seconds as numeric value or None
        @keyword socket_timeout: socket timeout in seconds
        @keyword force_show_code: if True force to show check code
        @keyword server_charset: server data charset
        @keyword user_agent: user agent string
        """
        self.user = user
        for param in ('db_lifetime', 'db_reloadtime', 'socket_timeout',
                'force_show_code', 'server_charset', 'user_agent'):
            if param in kw:
                setattr(self, param, kw[param])
        for param in ('db_lifetime', 'db_reloadtime'):
            value = getattr(self, param)
            if type(value) in (int, long, float):
                setattr(self, param, datetime.timedelta(seconds = value))

    def normalize_host(self, request):
        host = request.host.lower()
        if host.startswith('www.'):
            host = host[len('www.'):]
        return host

    def load_data(self, db_driver, server_list, format, request):
        def save_error(host, data, error):
            new_data = {}
            new_data.update(data)
            new_data['__error_time__'] =  datetime.datetime.now()
            new_data['__error_value__'] = error
            return db_driver.save(host, new_data, blocking = False)

        host = self.normalize_host(request)
        data = None
        force_refresh = False
        try:
            data = db_driver.load(host)
        except KeyError:
            log.debug("No existing database found, creating new one")
        if data is not None and self.db_lifetime is not None:
            reloadtime = self.db_reloadtime
            if reloadtime is None:
                reloadtime = self.db_lifetime
            try:
                refresh_after = data['__error_time__'] + reloadtime
            except KeyError:
                refresh_after = (db_driver.get_mtime(host) +
                        self.db_lifetime)
            if refresh_after <= datetime.datetime.now():
                log.debug("The database too old, refreshing")
                force_refresh = True
        if data is None:
            try:
                self.refresh_data(db_driver, server_list, format, request)
            except ClientError, e:
                if not save_error(host, {}, e):
                    raise e
            data = db_driver.load(host)
        elif force_refresh:
            try:
                self.refresh_data(db_driver, server_list, format, request)
            except ClientDataAccessError:
                pass
            except ClientError, e:
                save_error(host, data, e)
            data = db_driver.load(host)
        return data

    def get_links(self, data, request):
        try:
            return data[str(request.uri)]
        except KeyError:
            return self.get_links_new_page(data, request)

    def get_links_new_page(self, data, request):
        return []

    def get_delimiter(self, data, request):
        return ''

    def is_bot(self, data, request):
        return False

    def transform_code(self, data, request, code):
        return code

    def load_links_data(self, request):
        return None

    def get_raw_links(self, request):
        log.debug("Getting raw links for: %s", request.url())
        data = self.load_links_data(request)
        links = self.get_links(data, request)
        return [self.transform_code(data, request, code) for code in links]

    def get_html_links(self, request):
        log.debug("Getting HTML links for: %s", request.url())
        data = self.load_links_data(request)
        links = self.get_links(data, request)
        delim = self.get_delimiter(data, request)
        html = delim.join(links)
        return self.transform_code(data, request, html)

    def parse_link(self, link):
        if type(link) == str:
            link = unicode(link, self.server_charset)
        return link

    def parse_data(self, source, url, format):
        if format == 'php':
            raw_data = source.read()
            if raw_data.startswith('FATAL ERROR:'):
                log.error("Server error: %s: %s", raw_data, url)
                raise ClientError(raw_data)
            try:
                data = phpserialize.loads(raw_data)
            except ValueError, e:
                log.error("Could not deserialize response from server: %s: %s", str(e), url)
                raise ClientDataError('Could not deserialize response '
                        'from server: %s' % str(e))
            for key, value in data.items():
                if key.startswith('/'):
                    if type(value) == dict:
                        value = value.values()
                    yield (normalize_uri(key), map(self.parse_link, value))
                else:
                    if type(value) == str:
                        value = unicode(value, self.server_charset)
                    yield (key, value)

    def fetch_data(self, url, format):
        req = urllib2.Request(url)
        req.add_header('User-Agent', self.user_agent)
        req.add_header('Accept-Charset', self.server_charset)
        try:
            log.debug("Fetching: %s", url)
            f = urlopen_with_timeout(req, self.socket_timeout)
            return self.parse_data(f, url, format)
        except urlopen_errors, e:
            log.error("Network error: %s: %s", str(e), url)
            raise ClientNetworkError('Network error: %s' % str(e))

    def refresh_data(self, db_driver, server_list, format, request):
        host = self.normalize_host(request)
        server_list = server_list[:]
        random.shuffle(server_list)
        server_list = iter(server_list)
        data = None
        error = None
        while data is None:
            try:
                server = server_list.next()
                url = server % dict(user=self.user, host=host)
                data = self.fetch_data(url, format)
            except StopIteration:
                raise error
            except ClientError, e:
                error = e
                continue
        if not db_driver.save(host, data, blocking=False):
            log.warning("Other process/tread is currently writes to the database")
            raise ClientDataAccessError(
                    "Other process/tread is currently writes to the database")

class SapeTestServer(SapeLikeTestServer):
    filename = 'sape_test_server_data.txt'
    data = {
        '/': [
            '<a href="url1">link1</a>',
            '<a href="url2">link2</a>'],
        '/path/1': [
            '<a href="url1">link1</a>',
            '<a href="url2">link2</a>',
            '<a href="url3">link3</a>',
            '<a href="url4">link4</a>'],
        '/path/2': [
            'Plain text and <a href="url">link text</a>'],
        '__sape_new_url__': '<!--12345-->',
        '__sape_delimiter__': '. ',
        }

    def format_data_xml(self, data):
        def make_page(uri, links):
            return '<page uri="%s">%s</page>' % (uri,
                    ''.join(['<link><![CDATA[%s]]></link>' % s
                        for s in links]))

        pages = '\n'.join([make_page(uri, links)
            for uri, links in data.items() if uri.startswith('/')])

        lines = [
                '<?xml version="1.0" encoding="UTF-8"?>',
                '<sape delimiter="%s">' % data.get('__sape_delimiter__', ''),
                pages,
                '<page uri="*"><![CDATA[%s]]></page>' % data.get(
                    '__sape_new_url__', ''),
                '</sape>']
        return '\n'.join(lines)

class SapeClient(SapeLikeClient):
    """
    Sape.ru client.

    >>> from linkexchange.clients.base import PageRequest
    >>> test_server = SapeTestServer()
    >>> cl = SapeClient(user='user123456789', db_driver=('mem',),
    ...                 server_list=[test_server.url], server_format='xml')
    >>> lx = cl.get_raw_links(PageRequest(url = 'http://example.com/'))
    >>> lx[0]
    u'<a href="url1">link1</a>'
    >>> lx[1]
    u'<a href="url2">link2</a>'
    >>> cl = SapeClient(user='user123456789', db_driver=('mem',),
    ...                 server_list=['file:///does_not_exists'], server_format='xml')
    >>> cl.get_raw_links(PageRequest(url = 'http://example.com/'))
    []
    >>> cl.get_raw_links(PageRequest(url = 'http://example.com/'))
    []
    """

    server_list = [
            'http://dispenser-01.sape.ru/code.php?user=%(user)s&host=%(host)s&charset=utf-8&as_xml=1',
            'http://dispenser-02.sape.ru/code.php?user=%(user)s&host=%(host)s&charset=utf-8&as_xml=1']
    server_format = 'xml'

    def __init__(self, user, db_driver, **kw):
        """
        SapeClient constructor.
        
        The user is hash code string that assigned to user on link exchange
        service.

        The db_driver argument is multihash database driver instance or plugin
        specifier. In second case plugin specifier is used to create new
        instance. The database driver instance is used to store links database.

        @param user: user hash code string on link exchange service
        @param db_driver: multihash database driver instance or plugin specifier
        @keyword server_list: list of servers URLs
        @keyword server_format: server output data format 'xml' or 'php'
        """
        super(SapeClient, self).__init__(user, **kw)
        if is_plugin_specifier(db_driver):
            db_driver = load_plugin('linkexchange.multihash_drivers', db_driver)
        self.db_driver = db_driver
        for param in ('server_list', 'server_format'):
            if param in kw:
                setattr(self, param, kw[param])
        if 'use_xml' in kw:
            log.warning("The use_xml parameter is depricated!")
            self.server_format = kw['use_xml'] and 'xml' or 'php'
        if 'xml_server_list' in kw:
            log.warning("The xml_server_list parameter is depricated!")
            self.server_list = kw['xml_server_list']
        log.debug("New %s instance:\n%s",
                self.__class__.__name__,
                '\n'.join(["    %s: %s" % (x, repr(getattr(self, x)))
                    for x in (
                        'user',
                        'db_driver',
                        'db_lifetime',
                        'db_reloadtime',
                        'socket_timeout',
                        'force_show_code',
                        'server_list',
                        'server_format',
                        'server_charset',
                        'user_agent')]))

    def load_links_data(self, request):
        return self.load_data(self.db_driver, self.server_list,
                self.server_format, request)

    def refresh_db(self, request):
        self.refresh_data(self.db_driver, self.server_list,
                self.server_format, request)

    def get_links_new_page(self, data, request):
        if self.is_bot(data, request) or self.force_show_code:
            try:
                return [data['__sape_new_url__']]
            except KeyError:
                pass
        return []

    def get_delimiter(self, data, request):
        return data.get('__sape_delimiter__', '')

    def is_bot(self, data, request):
        return request.cookies.get('sape_cookie') == self.user

    def transform_code(self, data, request, code):
        if self.is_bot(data, request):
            code = '<sape_noindex>%s</sape_noindex>' % code
        return code

    def parse_data(self, source, url, format):
        def node_text(node):
            return u''.join([sn.nodeValue for sn in node.childNodes
                if sn.nodeType == xml.dom.Node.TEXT_NODE])

        def parse_xml(events):
            path = []
            try:
                for (event, node) in events:
                    if event == xml.dom.pulldom.START_ELEMENT:
                        path.append(node.tagName)
                        if path == ['sape', 'page']:
                            events.expandNode(node)
                            path.pop()
                            uri = node.getAttribute('uri')
                            if uri == '*':
                                yield ('__sape_new_url__', node_text(node))
                            else:
                                uri = normalize_uri(uri)
                                link_nodes = node.getElementsByTagName('link')
                                yield (uri, [self.parse_link(node_text(x))
                                    for x in link_nodes])
                        elif path == ['sape', 'sape_ips']:
                            events.expandNode(node)
                            path.pop()
                            ip_nodes = node.getElementsByTagName('ip')
                            yield ('__sape_ips__',
                                    [node_text(x) for x in ip_nodes])
                        elif path == ['sape']:
                            delimiter = node.getAttribute('delimiter')
                            if delimiter:
                                yield ('__sape_delimiter__', delimiter)
                    elif event == xml.dom.pulldom.END_ELEMENT:
                        path.pop()
            except xml.sax.SAXParseException, e:
                log.error("Could not parse XML data: %s: %s", str(e), url)
                raise ClientDataError('Could not parse XML data: %s' % str(e))

        if format == 'xml':
            return parse_xml(xml.dom.pulldom.parse(source))
        return super(SapeClient, self).parse_data(source, url, format)

class ContextLinksGenerator(HTMLParser.HTMLParser):
    def __init__(self, out, links,
            is_fragment, show_code, new_url_code,
            force_body_sape_index = False,
            exclude_tags = None,
            include_tags = None):
        HTMLParser.HTMLParser.__init__(self)
        self.out = out
        self.char_buf = []
        self.links = links
        self.is_fragment = is_fragment
        self.show_code = show_code
        self.new_url_code = new_url_code
        self.force_body_sape_index = force_body_sape_index
        self.exclude_tags = (exclude_tags or set()) | set(['a',
            'textarea', 'select', 'script', 'style',
            'label', 'noscript' , 'noindex', 'button'])
        self.exclude_ctx = []
        self.include_tags = include_tags or set()
        self.include_ctx = []

    def handle_starttag(self, tag, attrs):
        self.handle_realdata()
        if self.is_fragment:
            ignore = tag in ('html', 'body')
        else:
            ignore = not self.show_code and tag == 'sape_index'
        if not ignore:
            self.out.write(u'<' + tag)
            for k, v in attrs:
                self.out.write(' %s="%s"' % (k, xml.sax.saxutils.escape(v)))
            self.out.write(u'>')
        if tag == 'body' and self.show_code:
            if ((not self.is_fragment and self.force_body_sape_index) or
                    self.is_fragment):
                self.out.write('<sape_index>')
        if tag in self.exclude_tags:
            self.exclude_ctx.append(tag)
        elif tag in self.include_tags:
            self.include_ctx.append(tag)

    def handle_endtag(self, tag):
        self.handle_realdata()
        if tag == 'body' and self.show_code:
            if ((not self.is_fragment and self.force_body_sape_index) or
                    self.is_fragment):
                self.out.write('</sape_index>')
                if self.new_url_code:
                    self.out.write(self.new_url_code)
        if self.is_fragment:
            ignore = tag in ('html', 'body')
        else:
            ignore = not self.show_code and tag == 'sape_index'
        if not ignore:
            self.out.write('</%s>' % tag)
            if tag == 'sape_index' and self.show_code and self.new_url_code:
                self.out.write(self.new_url_code)
        if tag in self.exclude_tags:
            self.exclude_ctx.pop()
        elif tag in self.include_tags:
            self.include_ctx.pop()

    def handle_startendtag(self, tag, attrs):
        self.handle_realdata()
        self.out.write(u'<' + tag)
        for k, v in attrs:
            self.out.write(' %s="%s"' % (k, xml.sax.saxutils.escape(v)))
        self.out.write(u'/>')

    def handle_data(self, data):
        self.char_buf.append(data)

    def handle_charref(self, name):
        self.char_buf.append('&#%s;' % name)

    def handle_entityref(self, name):
        self.char_buf.append('&%s;' % name)

    def handle_realdata(self):
        content = ''.join(self.char_buf)
        self.char_buf[:] = []
        if not self.exclude_ctx:
            if set(self.include_ctx) == self.include_tags:
                for sentence_re, link in self.links:
                    content = sentence_re.sub(link, content, count = 1)
        self.out.write(content)

    def handle_comment(self, data):
        self.char_buf.append('<!--%s-->' % data)

    def handle_decl(self, data):
        self.char_buf.append('<!%s>' % data)

    def handle_pi(self, data):
        self.char_buf.append('<?%s>' % data)

class SapeContextClient(SapeClient):
    """
    Sape.ru client for context links.

    >>> from linkexchange.clients.base import PageRequest
    >>> test_server = SapeTestServer()
    >>> cl = SapeContextClient(user='user123456789', db_driver=('mem',),
    ...                 server_list=[test_server.url],
    ...                 force_show_code=False)
    >>> html = lambda x: u'<html>\\n<body>\\n%s\\n</body>\\n</html>' % x
    >>> req = PageRequest(url = 'http://example.com/',
    ...                   cookies = dict(sape_cookie = cl.user))
    >>> print cl.content_filter(req, u'This&#x20;text contains the link1.')
    <sape_index>This&#x20;text contains the <a href="url1">link1</a>.</sape_index><!--12345-->
    >>> print cl.content_filter(req, u'foo <textarea>link1 bar</textarea>')
    <sape_index>foo <textarea>link1 bar</textarea></sape_index><!--12345-->
    >>> print cl.content_filter(req, html(u'Text link2'))
    <html>
    <body><sape_index>
    Text <a href="url2">link2</a>
    </sape_index><!--12345--></body>
    </html>
    >>> print cl.content_filter(req, html(u'<sape_index>Text link1</sape_index> &amp; Text link2.'))
    <html>
    <body>
    <sape_index>Text <a href="url1">link1</a></sape_index><!--12345--> &amp; Text link2.
    </body>
    </html>
    >>> req = PageRequest(url = 'http://example.com/',
    ...                   cookies = dict())
    >>> print cl.content_filter(req, u'This&#x20;text contains the link1.')
    This&#x20;text contains the <a href="url1">link1</a>.
    >>> print cl.content_filter(req, u'foo <textarea>link1 bar</textarea>')
    foo <textarea>link1 bar</textarea>
    >>> print cl.content_filter(req, html(u'Text link2'))
    <html>
    <body>
    Text <a href="url2">link2</a>
    </body>
    </html>
    >>> print cl.content_filter(req, html(u'<sape_index>Text link1</sape_index> &amp; Text link2.'))
    <html>
    <body>
    Text <a href="url1">link1</a> &amp; Text link2.
    </body>
    </html>
    """

    force_show_code = False
    server_list = [
            'http://dispenser-01.sape.ru/code_context.php?user=%(user)s&host=%(host)s&charset=utf-8&as_xml=1',
            'http://dispenser-02.sape.ru/code_context.php?user=%(user)s&host=%(host)s&charset=utf-8&as_xml=1']
    server_format = 'xml'

    def __init__(self, user, db_driver, **kw):
        super(SapeContextClient, self).__init__(user, db_driver, **kw)
        self.tags_re = re.compile(r'<[^>]*>')
        self.start_doc_re = re.compile(r'^\s*<(\?xml|!DOCTYPE|html|HTML)\b', re.S)

    def get_raw_links(self, request):
        return []

    def get_html_links(self, request):
        return u''

    def content_filter(self, request, content):
        data = self.load_links_data(request)
        show_code = self.is_bot(data, request) or self.force_show_code
        links = data.get(str(request.uri), [])
        force_body_sape_index = False
        include_tags = set()
        if self.start_doc_re.match(content):
            is_fragment = False
            include_tags = set(['body'])
            if '<sape_index>' not in content:
                force_body_sape_index = True
            else:
                include_tags |= set(['sape_index'])
        else:
            is_fragment = True
            content = '<html><body>%s</body></html>' % content
        out = StringIO.StringIO()
        generator = ContextLinksGenerator(out, links,
                is_fragment = is_fragment,
                show_code = show_code,
                new_url_code = data.get('__sape_new_url__', ''),
                force_body_sape_index = force_body_sape_index,
                include_tags = include_tags)
        generator.feed(content)
        generator.close()
        return out.getvalue()

    def parse_link(self, link):
        link = super(SapeContextClient, self).parse_link(link)
        sentence = re.escape(xml.sax.saxutils.unescape(
            self.tags_re.sub('', link)))
        sentence.replace(' ', r'(\s|(&nbsp;))+')
        return (re.compile(sentence, re.S + re.UNICODE), link)

class SapeArticlesIndexTestServer(SapeLikeTestServer):
    filename = 'sape_articles_index_test_server_data.txt'
    server_format = 'php'
    data = {
            'announcements': {
                '/': [
                    '<a href="/articles/1">ann link1</a>',
                    '<a href="/articles/1">ann link2</a>'],
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
                    'url': 'sape_articles_template_test_server_data.txt',
                    },
                },
            'template_fields': [
                'title', 'keywords', 'header', 'body',
                ],
            'template_required_fields': [
                'title', 'keywords', 'header', 'body',
                ],
            'ext_links_allowed': [],
            'checkCode': '<!-- announcements place -->',
            'announcements_delimiter': '|',
            }

class SapeArticlesArticleTestServer(SapeLikeTestServer):
    filename = 'sape_articles_article_test_server_data.txt'
    server_format = 'php'
    data = {
            'date_updated': '0',
            'title': 'The article title',
            'keywords': 'The keywords',
            'header': 'The article header',
            'body': '<p>The article <a href="http://example.com">body</a>.</p>',
            }

class SapeArticlesTemplateTestServer(SimpleFileTestServer):
    filename = 'sape_articles_template_test_server_data.txt'
    raw_data = """
    <html>
      <head>
        <title>{title}</title>
        <meta name="keywords" content="{keywords}"/>
      </head>
    <body>
      <h1>{header}</h1>
      {body}
      <div id="footer">
        <a href="http://external-link.com">External link</a>
      </div>
    </body>
    </html>
    """

class ArticleTemplateLinksCutter(HTMLParser.HTMLParser):
    def __init__(self, out, allowed_domains):
        HTMLParser.HTMLParser.__init__(self)
        self.out = out
        self.char_buf = []
        self.allowed_domains = allowed_domains
        self.exclude_tags = set(['script', 'noindex'])
        self.exclude_ctx = []
        self.anchor_needs_noindex = []

    def handle_starttag(self, tag, attrs):
        self.handle_realdata()
        if not self.exclude_ctx:
            if tag == 'a':
                self.anchor_needs_noindex.append(False)
                href = ''
                for k, v in attrs:
                    if k == 'href': href = v
                if href.startswith('http'):
                    url = urlparse.urlsplit(href)
                    if not url[1] or url[1] not in self.allowed_domains:
                        self.out.write(u'<noindex>')
                        self.anchor_needs_noindex[-1] = True
                        attrs = ([(k, v) for k, v in attrs if k != 'rel'] +
                                [('rel', 'nofollow')])
        self.out.write(u'<' + tag)
        for k, v in attrs:
            self.out.write(' %s="%s"' % (k, xml.sax.saxutils.escape(v)))
        self.out.write(u'>')
        if tag in self.exclude_tags:
            self.exclude_ctx.append(tag)

    def handle_endtag(self, tag):
        self.handle_realdata()
        self.out.write('</%s>' % tag)
        if not self.exclude_ctx:
            if tag == 'a':
                if self.anchor_needs_noindex.pop():
                    self.out.write(u'</noindex>')
        if tag in self.exclude_tags:
            self.exclude_ctx.pop()

    def handle_startendtag(self, tag, attrs):
        self.handle_realdata()
        self.out.write(u'<' + tag)
        for k, v in attrs:
            self.out.write(' %s="%s"' % (k, xml.sax.saxutils.escape(v)))
        self.out.write(u'/>')

    def handle_data(self, data):
        self.char_buf.append(data)

    def handle_charref(self, name):
        self.char_buf.append('&#%s;' % name)

    def handle_entityref(self, name):
        self.char_buf.append('&%s;' % name)

    def handle_realdata(self):
        content = ''.join(self.char_buf)
        self.char_buf[:] = []
        self.out.write(content)

    def handle_comment(self, data):
        self.char_buf.append('<!--%s-->' % data)

    def handle_decl(self, data):
        self.char_buf.append('<!%s>' % data)

    def handle_pi(self, data):
        self.char_buf.append('<?%s>' % data)

class SapeArticlesClient(SapeLikeClient):
    """
    Sape.ru articles client.

    >>> import re
    >>> from linkexchange.clients.base import PageRequest
    >>> index_test_server = SapeArticlesIndexTestServer()
    >>> article_test_server = SapeArticlesArticleTestServer()
    >>> template_test_server = SapeArticlesTemplateTestServer()
    >>> cl = SapeArticlesClient(user='user123456789',
    ...                 index_db_driver=('mem',),
    ...                 article_db_driver=('mem',),
    ...                 image_db_driver=('mem',),
    ...                 template_db_driver=('mem',),
    ...                 index_server_list=[index_test_server.url],
    ...                 article_server_list=[article_test_server.url],
    ...                 )
    >>> lx = cl.get_raw_links(PageRequest(url='http://example.com/'))
    >>> lx[0]
    u'<a href="/articles/1">ann link1</a>'
    >>> lx[1]
    u'<a href="/articles/1">ann link2</a>'
    >>> resp = cl.handle_request(PageRequest(url='http://example.com/articles/1'))
    >>> resp.status
    200
    >>> resp.headers['Content-Type'].split(';')[0]
    'text/html'
    >>> '<title>The article title</title>' in resp.body
    True
    >>> '<p>The article ' in resp.body
    True
    >>> test_re = re.compile(r'<noindex><a[^>]+href='
    ...   r'"http://external-link.com"[^>]*>External link</a></noindex>', re.S)
    >>> m = test_re.search(resp.body)
    >>> m is not None
    True
    >>> 'rel="nofollow"' in m.group(0)
    True
    >>> cl.refresh_db(PageRequest(url='http://example.com/'))
    >>>
    """

    force_show_code = False
    index_server_list = [
            ('http://dispenser.articles.sape.ru/?'
                'user=%(user)s&host=%(host)s&rtype=index'),
            ]
    article_server_list = [
            ('http://dispenser.articles.sape.ru/?'
                'user=%(user)s&host=%(host)s&rtype=article&'
                'artid=%(article_id)s'),
            ]
    image_server_list = [
            ('http://dispenser.articles.sape.ru/'),
            ]
    output_charset = 'utf-8'

    _template_charset_re = re.compile(r'<meta\s+http-equiv="Content-Type"\s+'
            r'content="text/html;\s*charset=(?P<charset>[\w-]+)"\s*/?>',
            re.I + re.S)

    def __init__(self, user, index_db_driver, article_db_driver,
            image_db_driver, template_db_driver, **kw):
        """
        SapeClient constructor.
        
        The user is hash code string that assigned to user on link exchange
        service.

        The index_db_driver, article_db_driver, image_db_driver and
        template_db_driver arguments is multihash database drivers instances or
        plugin specifiers. In second case plugin specifier is used to create
        new instance. The database drivers instances is used to store index,
        articles, images and templates databases.

        @param user: user hash code string on link exchange service
        @param index_db_driver: multihash databases driver instance or plugin
                                specifier used to store index
        @param article_db_driver: multihash databases driver instance or plugin
                                  specifier used to store articles
        @param image_db_driver: multihash databases driver instance or plugin
                                specifier used to store images
        @param template_db_driver: multihash databases driver instance or
                                   plugin specifier used to store templates
        @param index_server_list: list of servers URLs to get index
        @param article_server_list: list of servers URLs to get articles
        @param image_server_list: list of servers URLs to get images
        """
        super(SapeArticlesClient, self).__init__(user, **kw)
        if is_plugin_specifier(index_db_driver):
            index_db_driver = load_plugin('linkexchange.multihash_drivers',
                    index_db_driver)
        self.index_db_driver = index_db_driver
        if is_plugin_specifier(article_db_driver):
            article_db_driver = load_plugin('linkexchange.multihash_drivers',
                    article_db_driver)
        self.article_db_driver = article_db_driver
        if is_plugin_specifier(image_db_driver):
            image_db_driver = load_plugin('linkexchange.multihash_drivers',
                    image_db_driver)
        self.image_db_driver = image_db_driver
        if is_plugin_specifier(template_db_driver):
            template_db_driver = load_plugin('linkexchange.multihash_drivers',
                    template_db_driver)
        self.template_db_driver = template_db_driver
        for param in ('index_server_list', 'article_server_list',
                'image_server_list', 'output_charset'):
            if param in kw:
                setattr(self, param, kw[param])
        log.debug("New %s instance:\n%s",
                self.__class__.__name__,
                '\n'.join(["    %s: %s" % (x, repr(getattr(self, x)))
                    for x in (
                        'user',
                        'db_lifetime',
                        'db_reloadtime',
                        'socket_timeout',
                        'force_show_code',
                        'user_agent',
                        'index_db_driver',
                        'article_db_driver',
                        'image_db_driver',
                        'template_db_driver',
                        'index_server_list',
                        'article_server_list',
                        'image_server_list',
                        'server_charset',
                        'output_charset')]))

    def load_links_data(self, request):
        return self.load_data(self.index_db_driver, self.index_server_list,
                'php', request)

    def load_data2(self, db_driver, host):
        while True:
            try:
                return db_driver.load(host)
            except KeyError:
                log.debug("No existing database found, creating new one")
                db_driver.save(host, {}, blocking=False)
                continue

    def fetch_template(self, host, template_url, template_id, index):
        template = {'id': template_id,
                'date_updated': datetime.datetime.now()}
        if '/' in template_url:
            url = list(urlparse.urlsplit(template_url))
            url[0:2] = ['http', host]
            url = urlparse.urlunsplit(url)
        else:
            url = 'file://%s' % os.path.realpath(template_url)

        log.debug("Fetching template %s: %s", template_id, url)
        try:
            f = urlopen_with_timeout(url, self.socket_timeout)
            raw_data = f.read()
            f.close()
        except urlopen_errors, e:
            log.error("Network error: %s: %s", str(e), url)
            raise ClientNetworkError('Network error: %s' % str(e))

        charset = None
        content_type = f.info().getheader('Content-Type')
        if content_type:
            for x in content_type.split(';'):
                if x.lstrip().startswith('charset='):
                    charset = x.strip()[len('charset='):]
        if not charset:
            m = self._template_charset_re.search(raw_data)
            if m:
                charset = m.group('charset')

        template['body'] = unicode(raw_data, charset or 'ascii')

        for field in index.get('template_required_fields', []):
            if '{%s}' % field not in template['body']:
                raise ClientDataError('Missing template field: %s' % field)

        allowed_domains = set(index['ext_links_allowed'] +
                [host, 'www.' + host])
        out = StringIO.StringIO()
        cutter = ArticleTemplateLinksCutter(out, allowed_domains)
        cutter.feed(template['body'])
        cutter.close()
        template['body'] = out.getvalue()

        return template

    def load_template(self, request, template_meta, template_id, index):
        now = datetime.datetime.now()
        host = self.normalize_host(request)
        data = self.load_data2(self.template_db_driver, host)
        try:
            template = data[str(template_meta['url'])]
        except KeyError:
            template = None
        else:
            if (self.db_lifetime is not None and
                    now - template['date_updated'] > template_meta['lifetime']):
                template = None
        if template is None:
            template = self.fetch_template(host,
                    template_meta['url'], template_id, index)
            self.template_db_driver.modify(host,
                    {str(template_meta['url']): template})
        return template

    def fetch_article(self, host, article_id):
        def do_fetch_article(url):
            log.debug("Fetching article %s: %s", article_id, url)
            try:
                f = urlopen_with_timeout(url, self.socket_timeout)
                raw_data = f.read()
                f.close()
            except urlopen_errors, e:
                log.error("Network error: %s: %s", str(e), url)
                raise ClientNetworkError('Network error: %s' % str(e))
            if raw_data.startswith('FATAL ERROR:'):
                log.error("Server error: %s: %s", raw_data, url)
                raise ClientError(raw_data)
            try:
                return phpserialize.loads(raw_data)
            except ValueError, e:
                log.error("Could not deserialize response from server: %s: %s",
                        str(e), url)
                raise ClientDataError('Could not deserialize response '
                        'from server: %s' % str(e))

        server_list = self.article_server_list[:]
        random.shuffle(server_list)
        server_list = iter(server_list)
        article = None
        while article is None:
            try:
                server = server_list.next()
                url = server % dict(user=self.user, host=host,
                        article_id=article_id)
                article = do_fetch_article(url)
                if 'date_updated' in article:
                    article['date_updated'] = datetime.datetime.fromtimestamp(
                            int(article['date_updated']))
                for k in article.keys():
                    if type(article[k]) == str:
                        article[k] = unicode(article[k], self.server_charset)
            except StopIteration:
                raise error
            except ClientError, e:
                error = e
                continue
        return article

    def load_article(self, request, article_meta):
        now = datetime.datetime.now()
        host = self.normalize_host(request)
        data = self.load_data2(self.article_db_driver, host)
        article_url = request.uri
        try:
            article = data[str(article_url)]
        except KeyError:
            article = None
        else:
            if self.db_lifetime is not None:
                if ('date_updated' not in article or
                        article['date_updated'] != article_meta['date_updated']):
                    article = None
        if article is None:
            article = self.fetch_article(host, article_meta['id'])
            self.article_db_driver.modify(host,
                    {str(article_url): article})
        return article

    def fetch_image(self, host, dispenser_path):
        def do_fetch_image(url):
            log.debug("Fetching image: %s", url)
            try:
                f = urlopen_with_timeout(url, self.socket_timeout)
                raw_data = f.read()
                f.close()
            except urlopen_errors, e:
                log.error("Network error: %s: %s", str(e), url)
                raise ClientNetworkError('Network error: %s' % str(e))
            if raw_data.startswith('FATAL ERROR:'):
                log.error("Server error: %s: %s", raw_data, url)
                raise ClientError(raw_data)
            return {'date_updated': datetime.datetime.now(),
                    'image': raw_data}
        server_list = self.image_server_list[:]
        random.shuffle(server_list)
        server_list = iter(server_list)
        image = None
        while image is None:
            try:
                server = server_list.next()
                url = server % dict(user=self.user, host=host)
                if url.endswith('/') and dispenser_path.startswith('/'):
                    url = url[:-1]
                url += dispenser_path
                image = do_fetch_image(url)
                mime, enc = mimetypes.guess_type('file.' + image_meta['ext'])
                image['mime'] = mime or 'image/jpeg'
            except StopIteration:
                raise error
            except ClientError, e:
                error = e
                continue
        return image

    def load_image(self, request, image_meta):
        now = datetime.datetime.now()
        host = self.normalize_host(request)
        data = self.load_data2(self.image_db_driver, host)
        image_url = request.uri
        try:
            image = data[str(image_url)]
        except KeyError:
            image = None
        else:
            if self.db_lifetime is not None:
                if ('date_updated' not in image or
                        image['date_updated'] < image_meta['date_updated']):
                    image = None
        if image is None:
            image = self.fetch_image(host, image_meta['dispenser_path'])
            self.image_db_driver.modify(host,
                    {str(image_url): image})
        return image

    def refresh_db(self, request):
        # refresh index
        self.refresh_data(self.index_db_driver, self.index_server_list,
                'php', request)

        index = self.load_links_data(request)
        now = datetime.datetime.now()
        host = self.normalize_host(request)

        # refresh templates cache
        data = self.load_data2(self.template_db_driver, host)
        new_data = {}
        for template_url, template in data.items():
            template_meta = index['template_' + str(template['id'])]
            if now - template['date_updated'] > template_meta['lifetime']:
                try:
                    new_data[template_url] = self.fetch_template(host,
                            template_meta['url'], template['id'], index)
                except ClientError:
                    pass
        if new_data:
            self.template_db_driver.modify(host, new_data)

        # refresh articles
        data = self.load_data2(self.article_db_driver, host)
        new_data = {}
        for article_url, article in data.items():
            article_meta = index['article_' + str(article_url)]
            if ('date_updated' not in article or
                    article['date_updated'] != article_meta['date_updated']):
                try:
                    new_data[article_url] = self.fetch_article(host,
                            article_meta['id'])
                except ClientError:
                    pass
        if new_data:
            self.article_db_driver.modify(host, new_data)

        # refresh images
        data = self.load_data2(self.image_db_driver, host)
        new_data = {}
        for image_url, image in data.items():
            image_meta = index['image_' + str(image_url)]
            if ('date_updated' not in image or
                    image['date_updated'] < image_meta['date_updated']):
                try:
                    new_data[image_url] = self.fetch_image(host,
                            image_meta['dispenser_path'])
                except ClientError:
                    pass
        if new_data:
            self.image_db_driver.modify(host, new_data)

    def get_links(self, data, request):
        try:
            links = data['announcement_' + str(request.uri)]
        except KeyError:
            links = []
        if self.is_bot(data, request) or self.force_show_code:
            if len(links) == 0:
                links.append(u'')
            links[0] = data.get('checkCode', '') + links[0]
        return links

    def get_delimiter(self, data, request):
        return data.get('announcements_delimiter', '')

    def is_bot(self, data, request):
        return request.cookies.get('sape_cookie') == self.user

    def transform_code(self, data, request, code):
        if self.is_bot(data, request):
            code = '<sape_noindex>%s</sape_noindex>' % code
        return code

    def parse_data(self, source, url, format):
        if format == 'php':
            raw_data = source.read()
            if raw_data.startswith('FATAL ERROR:'):
                log.error("Server error: %s: %s", raw_data, url)
                raise ClientError(raw_data)
            try:
                data = phpserialize.loads(raw_data)
            except ValueError, e:
                log.error("Could not deserialize response from server: %s: %s", str(e), url)
                raise ClientDataError('Could not deserialize response '
                        'from server: %s' % str(e))
            for uri, links in data.pop('announcements').items():
                if type(links) == dict:
                    links = links.values()
                yield ('announcement_' + normalize_uri(uri),
                        map(self.parse_link, links))
            for uri, article_meta in data.pop('articles').items():
                article_meta['date_updated'] = datetime.datetime.fromtimestamp(
                        int(article_meta['date_updated']))
                yield ('article_' + normalize_uri(uri), article_meta)
            for uri, image_meta in data.pop('images').items():
                image_meta['date_updated'] = datetime.datetime.fromtimestamp(
                        int(image_meta['date_updated']))
                yield ('image_' + normalize_uri(uri), image_meta)
            for tpl_id, template_meta in data.pop('templates').items():
                template_meta['lifetime'] = datetime.timedelta(0,
                        int(template_meta['lifetime']))
                yield ('template_' + str(tpl_id), template_meta)
            list_keys = set(['template_fields', 'template_required_fields',
                'ext_links_allowed'])
            for key, value in data.items():
                if type(value) == str:
                    value = unicode(value, self.server_charset)
                elif type(value) == dict:
                    if key in list_keys:
                        value = value.values()
                yield (str(key), value)

    def handle_request(self, request):
        def return_article(index, article_meta):
            template_id = article_meta['template_id']
            try:
                template_meta = index['template_' + template_id]
            except KeyError:
                log.error("Template not found in template index: %s",
                        template_id)
                raise ClientDataError('Template not found in template '
                        'index: %s' % template_id)
            template = self.load_template(request, template_meta,
                    template_id, index)
            article = self.load_article(request, article_meta)
            article_body = template['body']
            article_body = article_body.replace('{meta_charset}',
                    self.output_charset)
            for field in index['template_fields']:
                article_body = article_body.replace(
                        '{%s}' % field, article.get(field, ''))
            if self.is_bot(index, request):
                article_body += '<!--sape_noindex-->'
            content_type = 'text/html; charset=%s' % self.output_charset
            return PageResponse(status=200,
                    body=article_body.encode(self.output_charset),
                    headers={'Content-Type': content_type})

        def return_image(index, image_meta):
            image = self.load_image(request, image_meta)
            return PageResponse(status=200, body=image['image'],
                    headers={'Content-Type': image['mime']})

        index = self.load_links_data(request)
        try:
            article_meta = index['article_' + str(request.uri)]
        except KeyError:
            pass
        else:
            return return_article(index, article_meta)
        try:
            image_meta = index['image_' + str(request.uri)]
        except KeyError:
            pass
        else:
            return return_image(index, image_meta)
        if self.is_bot(index, request):
            return PageResponse(status=200,
                    body=index.get('checkCode', '') + '<!--sape_noindex-->',
                    headers={'Content-Type': 'text/html'})
        return PageResponse(status=404)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
