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

from xml.sax import saxutils

class BaseFormatter(object):
    def __init__(self, count, client=None):
        """
        @param count: links count in the block (0 or None - catch all)
        @keyword client: catch links only from client
        """
        self.count = count
        self.client = client

    def format(self, tags, links):
        """
        Perform links formatting. tags is a list of unicode strings that don't
        contains '<a '. links is a list of unicode strings that contains links
        HTML code.

        @param tags: list of special tags
        @param links: list of links
        @return: HTML code
        """
        pass

    def _add_prefix(self, link, prefix):
        i = 0
        while not (prefix[:i] + link).startswith(prefix):
            i += 1
        link = prefix[:i] + link
        return link

    def _add_suffix(self, link, suffix):
        i = len(suffix)
        while not (link + suffix[i:]).endswith(suffix):
            i -= 1
        link += suffix[i:]
        return link

    def _format_container(self, tag, id, class_, content):
        html = u'<' + tag
        if id:
            html += u' id="%s"' % saxutils.escape(id)
        if class_:
            html += u' class="%s"' % saxutils.escape(class_)
        html += u'>'
        html += content
        html += u'</%s>' % tag
        return html

class InlineFormatter(BaseFormatter):
    def __init__(self, count,
            client=None,
            delimiter='',
            prefix='',
            suffix='',
            prolog='',
            epilog='',
            id=None,
            class_=None,
            class_for_empty=None,
            strip=False):
        """
        @param count: links count in the block (None - catch all)
        @keyword client: catch links only from client
        @keyword delimiter: links delimiter
        @keyword prefix: links prefix
        @keyword suffix: links suffix
        @keyword prolog: text before links
        @keyword epilog: text after links
        @keyword id: value for id attribute
        @keyword class_: CSS class for nonempty block
        @keyword class_for_empty: CSS class for empty block
        @keyword strip: skip DIV tag
        """
        super(InlineFormatter, self).__init__(count, client=client)
        self.delimiter = delimiter
        self.prefix = prefix
        self.suffix = suffix
        self.prolog = prolog
        self.epilog = epilog
        self.id = id
        self.class_ = class_
        self.class_for_empty = class_for_empty
        self.strip = strip

    def format(self, tags, links):
        def format_link(link):
            if self.prefix:
                link = self._add_prefix(link, self.prefix)
            if self.suffix:
                link = self._add_suffix(link, self.suffix)
            return link
        if links:
            css_class = self.class_
            content = self.prolog + self.delimiter.join(
                    map(format_link, links)) + self.epilog
        else:
            css_class = self.class_for_empty
            content = u''
        if self.strip:
            html = content
        else:
            html = self._format_container('div', self.id, css_class, content)
        html += u''.join(tags)
        return html

class ListFormatter(BaseFormatter):
    def __init__(self, count,
            client=None,
            prefix='',
            suffix='',
            id=None,
            class_=None,
            class_for_empty=None,
            li_class=None,
            tag_for_empty='span',
            strip=False):
        """
        @param count: links count in the block (None - catch all)
        @keyword client: catch links only from client
        @keyword prefix: links prefix
        @keyword suffix: links suffix
        @keyword id: value for id attribute
        @keyword class_: CSS class for nonempty block
        @keyword class_for_empty: CSS class for empty block
        @keyword li_class: CSS class for LI elements
        @keyword tag_for_empty: HTML tag for empty block
        @keyword strip: skip UL tag or empty tag
        """
        super(ListFormatter, self).__init__(count, client=client)
        self.prefix = prefix
        self.suffix = suffix
        self.id = id
        self.class_ = class_
        self.class_for_empty = class_for_empty
        self.li_class = li_class
        self.tag_for_empty = tag_for_empty
        self.strip = strip

    def format(self, tags, links):
        def format_link(link):
            if self.prefix:
                link = self._add_prefix(link, self.prefix)
            if self.suffix:
                link = self._add_suffix(link, self.suffix)
            if self.li_class:
                attrs = u' class="%s"' % saxutils.escape(self.li_class)
            else:
                attrs = u''
            link = u'<li%s>%s</li>' % (attrs, link)
            return link
        content = u''.join(map(format_link, links))
        if self.strip:
            html = content
        else:
            if links:
                css_class = self.class_
            else:
                css_class = self.class_for_empty
            html_tag = links and u'ul' or self.tag_for_empty
            html = self._format_container(html_tag, self.id,
                    css_class, content)
        html += u''.join(tags)
        return html
