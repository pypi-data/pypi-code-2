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

try:
    set
except NameError:
    from sets import Set as set

from linkexchange.utils import is_plugin_specifier, load_plugin
from linkexchange.clients.base import ClientError, PageRequest, PageResponse
from linkexchange.clients.sape import SapeTestServer

class RawLink(object):
    def __init__(self, link_code, client, client_no):
        self.link_code = link_code
        self.client = client
        self.client_no = client_no

    def __unicode__(self):
        return self.link_code

class SapeTestServer1(SapeTestServer):
    filename = 'sape_test_server1_data.txt'
    data = {
        '/': [
            '<a href="url1">xlink1</a>',
            '<a href="url2">xlink2</a>'],
        '/path/1': [
            '<a href="url1">xlink1</a>',
            '<a href="url2">xlink2</a>',
            '<a href="url3">xlink3</a>',
            '<a href="url4">xlink4</a>'],
        '/path/2': [
            'Plain text and <a href="url">link text</a>'],
        '__sape_new_url__': '<!--x12345-->',
        '__sape_delimiter__': '. ',
        }

class SapeTestServer2(SapeTestServer):
    filename = 'sape_test_server2_data.txt'
    data = {
        '/': [
            '<a href="url1">ylink1</a>'],
        '__sape_new_url__': '<!--y12345-->',
        '__sape_delimiter__': '. ',
        }

class Platform(object):
    """
    Platform combines various clients into one object. It have methods to get
    total list of raw links, to get links divided by blocks with custom
    formatting rules.

    >>> srv1 = SapeTestServer1()
    >>> srv2 = SapeTestServer2()
    >>> clients = [('sape', [], dict(user='user123456789',
    ...              db_driver=('mem',), server_list=[srv1.url])),
    ...            ('sape', [], dict(user='user123456789',
    ...              db_driver=('mem',), server_list=[srv2.url]))]
    >>> pl = Platform(clients=clients)
    >>> lx = pl.get_raw_links('http://example.com/')
    >>> unicode(lx[0])
    u'<a href="url1">xlink1</a>'
    >>> unicode(lx[1])
    u'<a href="url2">xlink2</a>'
    >>> unicode(lx[2])
    u'<a href="url1">ylink1</a>'
    >>> formatters = [('inline', [2], dict(
    ...                 class_='links', class_for_empty='empty', suffix='. ')),
    ...               ('list', [None], dict(id='links'))]
    >>> bx = pl.get_blocks('http://example.com/', formatters)
    >>> bx[0]
    u'<div class="links"><a href="url1">xlink1</a>. <a href="url2">xlink2</a>. </div>'
    >>> bx[1]
    u'<ul id="links"><li><a href="url1">ylink1</a></li></ul>'
    >>> bx = pl.get_blocks('http://example.com/notexists', formatters)
    >>> bx[0]
    u'<div class="empty"></div><!--x12345--><!--y12345-->'
    >>> bx[1]
    u'<span id="links"></span>'
    >>> bx = pl.get_blocks('http://example.com/path/1', formatters)
    >>> bx[0]
    u'<div class="links"><a href="url1">xlink1</a>. <a href="url2">xlink2</a>. </div>'
    >>> bx[1]
    u'<ul id="links"><li><a href="url3">xlink3</a></li><li><a href="url4">xlink4</a></li></ul><!--y12345-->'
    >>> formatters = [('inline', [None], dict()),
    ...               ('inline', [None], dict(client=1))]
    >>> bx = pl.get_blocks('http://example.com/', formatters)
    >>> bx[0]
    u'<div><a href="url1">ylink1</a></div>'
    >>> bx[1]
    u'<div><a href="url1">xlink1</a><a href="url2">xlink2</a></div>'
    """

    def __init__(self, clients = None):
        """
        @param clients: list of clients instances or clients specifiers

        """
        self.clients = []
        if clients:
            for cl in clients:
                self.add_client(cl)

    def add_client(self, client):
        """
        Add link exchange service client to the platform.

        The client parameter is instance of BaseClient or client specifier.
        Client specifier is (name, args, kwargs) tuple where name is client
        name (link exchange service name), args and kwargs is list of
        positional arguments and dictionary of keyword arguments for the client
        constructor respectively.

        @param client: instance of BaseClient or client specifier
        """
        if is_plugin_specifier(client):
            client = load_plugin('linkexchange.clients', client)
        self.clients.append(client)

    def get_raw_links(self, request):
        """
        Returns list of links to place on page identified by request. Catches
        clients errors and use HTML comments for errors reporting.

        @param request: PageRequest object or URL string
        @return: list of links as RawLink objects
        """
        if isinstance(request, basestring):
            request = PageRequest(url = request)
        result = []
        cl_no = 0
        for cl in self.clients:
            cl_no += 1
            try:
                links = cl.get_raw_links(request)
            except ClientError, e:
                links = [u'<!-- %s -->' % str(e)]
            raw_links = [RawLink(link_code=l,
                client=cl, client_no=cl_no) for l in links]
            result.extend(raw_links)
        return result

    def get_blocks(self, request, formatters):
        """
        Returns links grouped by blocks. Catches clients errors and use HTML
        comments for errors reporting.

        The request parameter is a PageRequest object or URL string. The
        formatters parameter is a sequence of BaseFormatter instances. The
        result is list of unicode strings with HTML formatted blocks of links.

        @param request: PageRequest object or URL string
        @param formatters: sequence of blocks formatters
        @return: list of links blocks as unicode strings
        """
        def load_formatter(fmt):
            if is_plugin_specifier(fmt):
                return load_plugin('linkexchange.formatters', fmt)
            return fmt

        def allocate_link(link, tag_list, link_list):
            link = unicode(link)
            if '<a ' in link:
                link_list.append(link)
            else:
                tag_list.append(link)

        formatters = map(load_formatter, formatters)
        links_pool = self.get_raw_links(request)
        blocks = [None for fmt in formatters]

        for i in range(len(formatters)):
            fmt = formatters[i]
            if fmt.client is None:
                continue
            if isinstance(fmt.client, basestring):
                client_no_set = set([int(x.strip())
                    for x in fmt.client.split(',')])
            else:
                client_no_set = set([fmt.client])
            tag_list = []
            link_list = []
            j = 0
            while j < len(links_pool) and ((fmt.count and
                len(link_list) < fmt.count) or (not fmt.count)):
                if links_pool[j].client_no in client_no_set:
                    allocate_link(links_pool.pop(j), tag_list, link_list)
                    continue
                j += 1
            blocks[i] = fmt.format(tag_list, link_list)

        for i in range(len(formatters)):
            if blocks[i] is not None:
                continue
            fmt = formatters[i]
            tag_list = []
            link_list = []
            while links_pool and ((fmt.count and
                len(link_list) < fmt.count) or (not fmt.count)):
                allocate_link(links_pool.pop(0), tag_list, link_list)
            blocks[i] = fmt.format(tag_list, link_list)

        return blocks

    def content_filter(self, request, content):
        """
        @param request: PageRequest object or URL string
        @param content: HTML content (full page or fragment) as unicode string
        @return: filtered content as unicode string
        """
        if isinstance(request, basestring):
            request = PageRequest(url = request)
        for cl in self.clients:
            try:
                content = cl.content_filter(request, content)
            except ClientError, e:
                pass
        return content

    def handle_request(self, request):
        """
        @param request: PageRequest object or URL string
        @return: PageResponse object
        """
        if isinstance(request, basestring):
            request = PageRequest(url=request)
        for cl in self.clients:
            try:
                response = cl.handle_request(request)
            except ClientError, e:
                continue
            if response.status != 404:
                return response
        return PageResponse(status=404)

    def refresh_db(self, request):
        """
        Force to refresh clients databases.

        @param request: PageRequest object or URL string
        """
        if isinstance(request, basestring):
            request = PageRequest(url = request)
        for cl in self.clients:
            try:
                cl.refresh_db(request)
            except ClientError, e:
                pass

if __name__ == "__main__":
    import doctest
    doctest.testmod()
