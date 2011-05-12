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

import xml.sax
import xml.dom
import xml.dom.pulldom
import logging

from linkexchange.clients.sape import SapeLikeClient
from linkexchange.clients.sape import SapeLikeTestServer
from linkexchange.utils import is_plugin_specifier, load_plugin
from linkexchange.utils import normalize_uri

log = logging.getLogger('linkexchange.clients.linkfeed')

class LinkFeedClient(SapeLikeClient):
    """
    LinkFeed.ru client.
    """
    
    server_list = [
            'http://db.linkfeed.ru/%(user)s/%(host)s/UTF-8.xml']
    server_format = 'xml'

    def __init__(self, user, db_driver, **kw):
        """
        LinkFeedClient constructor.
        
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
        super(LinkFeedClient, self).__init__(user, **kw)
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
                        'no_query_string',
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

    def parse_param(self, name, value):
        if name == '__linkfeed_robots__':
            if type(value) == dict:
                value = value.values()
        return super(LinkFeedClient, self).parse_param(name, value)

    def get_links_new_page(self, data, request):
        if self.is_check_code_visible(data, request):
            if (data.get('__linkfeed_start__', '') +
                    data.get('__linkfeed_end__', '')):
                return ['']
        return []

    def get_delimiter(self, data, request):
        return data.get('__linkfeed_delimiter__', '')

    def is_bot(self, data, request):
        bot_ips = data.get('__linkfeed_robots__', [])
        return request.remote_addr and request.remote_addr in bot_ips

    def transform_code(self, data, request, code):
        if self.is_check_code_visible(data, request):
            start = data.get('__linkfeed_start__', '')
            end = data.get('__linkfeed_end__', '')
        else:
            start = end = u''
        if code:
            before_text = data.get('__linkfeed_before_text__', '')
            after_text = data.get('__linkfeed_after_text__', '')
        else:
            before_text = after_text = u''
        return start + before_text + code + after_text + end

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
                        if path == ['data', 'pages','page']:
                            events.expandNode(node)
                            path.pop()
                            uri = normalize_uri(node.getAttribute('url'))
                            link_nodes = node.getElementsByTagName('link')
                            yield (uri, [self.parse_link(node_text(x))
                                for x in link_nodes])
                        elif path == ['data', 'config', 'item']:
                            events.expandNode(node)
                            path.pop()
                            name = str(node.getAttribute('name'))
                            if name:
                                yield ("__linkfeed_%s__" % name,
                                        node_text(node))
                        elif path == ['data', 'bot_ips']:
                            events.expandNode(node)
                            path.pop()
                            ip_nodes = node.getElementsByTagName('ip')
                            yield ("__linkfeed_robots__",
                                    [node_text(x) for x in ip_nodes])
                    elif event == xml.dom.pulldom.END_ELEMENT:
                        path.pop()
            except xml.sax.SAXParseException, e:
                log.error("Could not parse XML data: %s: %s", str(e), url)
                raise ClientDataError('Could not parse XML data: %s' % str(e))

        if format == 'xml':
            return parse_xml(xml.dom.pulldom.parse(source))
        return super(LinkFeedClient, self).parse_data(source, url, format)

class LinkFeedTestServer(SapeLikeTestServer):
    """
    Test server to test LinkFeed client.
    """
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
        '/path/2': [
            'Plain text and <a href="url">link text</a>'],
        '__linkfeed_start__' : '<!--12345-->',
        '__linkfeed_end__' : '<!--12345-->',
        '__linkfeed_delimiter__' : '. ',
        '__linkfeed_before_text__' : '',
        '__linkfeed_after_text__' : '',
        '__linkfeed_robots__' : ['123.45.67.89'],
        }

    def format_data(self, data):
        def xml_make_page(uri, links):
            return '<page url="%s">%s</page>' % (uri,
                    ''.join(['<link><![CDATA[%s]]></link>' % s
                        for s in links]))

        if self.server_format == 'xml':
            pages = '\n'.join([xml_make_page(uri, links)
                for uri, links in data.items() if uri.startswith('/')])

            lines = [
                    '<?xml version="1.0" encoding="UTF-8"?>',
                    '<data>',
                    '<config>',
                    '<item name="start"><![CDATA[%s]]></item>' % data.get(
                        '__linkfeed_start__', ''),
                    '<item name="end"><![CDATA[%s]]></item>' % data.get(
                        '__linkfeed_end__', ''),
                    '<item name="delimiter"><![CDATA[%s]]></item>' % data.get(
                        '__linkfeed_delimiter__', ''),
                    '<item name="before_text"><![CDATA[%s]]></item>' % data.get(
                        '__linkfeed_before_text__', ''),
                    '<item name="after_text"><![CDATA[%s]]></item>' % data.get(
                        '__linkfeed_after_text__', ''),
                    '</config>',
                    '<pages>',
                    pages,
                    '</pages>',
                    '</data>',
                    ]
            return '\n'.join(lines)
        return super(LinkFeedTestServer, self).format_data(data)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
