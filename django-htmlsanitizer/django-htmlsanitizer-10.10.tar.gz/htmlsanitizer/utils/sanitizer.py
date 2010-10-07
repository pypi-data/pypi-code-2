from urlparse import urlparse

from django.utils.safestring import mark_safe, SafeData, EscapeData

from BeautifulSoup import BeautifulSoup, Tag, Comment, NavigableString

from htmlsanitizer.utils.escape import *


class Sanitizer(object):
    """
    """

    def __init__(self, whitelist={}, blacklist=[], comments=False):
        # normalize and optimize our lookup dict and lists.
        self.whitelist = {}
        for tag, attributes in whitelist.items():
            self.whitelist[tag.lower()] = frozenset(
                [a.lower() for a in attributes]
            )
        self.blacklist = frozenset([tag.lower() for tag in blacklist])
        self.attributes_with_urls = frozenset(['href', 'src', 'background'])
        self.comments = bool(comments)

    def get_soup(self, html):
        import copy, re
        massage = copy.copy(BeautifulSoup.MARKUP_MASSAGE)
        massage.append(
            (re.compile('<!-([^-])'),
             lambda match: '<!--' + match.group(1))
        )
        massage.append(
            (re.compile(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\xff]'),
             lambda match: '')
        )
        return BeautifulSoup(html, markupMassage=massage)

    def clean(self, html):
        # check if it is already escaped
        if isinstance(html, (SafeData, EscapeData)):
            return html

        soup = self.get_soup(html)

        # remove any content not a tag in root
        for c in soup.contents:
            if isinstance(c, NavigableString):
                soup.contents.remove(c)

        # remove comments
        if not self.comments:
            soup = self.remove_comments(soup)

        # clean tags
        for tag in soup.findAll(True):
            tname = tag.name.lower()
            if tname in self.blacklist:
                # remove blacklisted completely.
                tag.extract()
                continue
            elif tname not in self.whitelist:
                # just remove tag, content will be there.
                tag.hidden = True
            else:
                # whitelisted clean attributes
                attrs = []
                for attr, value in tag.attrs:
                    attr = attr.lower()
                    if attr in self.whitelist[tname]:
                        if attr in self.attributes_with_urls:
                            # check urls some more
                            if self.url_is_acceptable(value):
                                value = self.clean_tag_attr_url(value)
                            else:
                                continue
                        attrs.append((attr, self.clean_tag_attr_value(value)))
                tag.attrs = attrs
            self.__clean_tag_content(tag)

        return mark_safe(soup.renderContents().decode('utf8').strip())

    def remove_comments(self, soup):
        """
        Remove all comments from the soup
        """
        for c in soup.findAll(text=lambda text: isinstance(text, Comment)):
            c.extract()
        return soup

    def __clean_tag_content(self, tag):
        """Inner loop for Tag content cleaning.

        Don't override this method but use clean_tag_content instead.
        """
        assert isinstance(tag, Tag)
        for c in tag.contents:
            # check if this work as suspected
            if isinstance(c, NavigableString):
                value = c.__class__(value=self.clean_tag_content(unicode(c)))
                c.replaceWith(value)

    def clean_tag_content(self, value):
        """Clean up the content of a tag

        @TODO: unittest
        """

        return escape(value, {'"': "&quot;", "'": "&#39;"})

    def clean_tag_attr_value(self, value):
        """
        cleanup attribute value

        @TODO: unittest
        """
        return escapeattr(value, {':': '&#58;'})

    def url_is_acceptable(self, url):
        """Check if url is accetable for use.

        If it returns false it will be extracted from the html.
        @TODO: unittest
        """
        parsed = urlparse(url, allow_fragments=False)
        # first check netloc and path for special characters
        # @TODO: this check should be refactored.
        for c in ("\0", "\n", "\r", "\t"):
            if c in parsed.netloc or c in parsed.path:
                return False
        # we don't allow a empty scheme if netloc is set.
        if parsed.netloc and not parsed.scheme:
            return False
        # only allow url from certain schema's and relative
        return parsed.scheme in ('http', 'https', 'ftp', '')

    def clean_tag_attr_url(self, url):
        """Cleanup the url."""
        return urlparse(url).geturl()
