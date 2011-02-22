#!/usr/bin/env python
# vim:fileencoding=utf-8

__author__ = 'zeus'
import re

from pbot import Bot
from lxml import html

import logging

class NoResponse(Exception):
    pass


BASE_URL_RE = re.compile('([^:/]+://[^/ ?]+)')

class Spider(Bot):
    '''
    Lxml powered crawler
    '''
    def __init__(self, *args, **kwargs):
        self.force_encoding = kwargs.pop('force_encoding', None)
        super(Spider, self).__init__(*args, **kwargs)
        self._tree = None
        self.base_url = None



    def open(self, *args, **kwargs):
        self._tree = None
        response = super(Spider, self).open(*args, **kwargs)
        self.base_url = BASE_URL_RE.search(self.url).group(0)
        return response

    @property
    def tree(self):
        '''
        Return lxml tree, if the're is no tree - parse current response
        '''
        if self._tree:
           return self._tree
        else:
            if self.response:
                if self.force_encoding:
                    parser = html.HTMLParser(encoding=self.force_encoding)
                    self._tree = html.parse(self.response, parser)
                else:
                    self._tree = html.parse(self.response)
                return self._tree
            else:
                raise NoResponse('Spider.response is empty or already readed')

    @property
    def xpath(self):
        return self.tree.xpath

    def submit(self, form):
        '''
        Submit lxml form, using self.base_url
        '''
        form.make_links_absolute(self.url)
        html.submit_form(form, open_http=self.open_http)

    @property
    def url(self):
        return self.response.geturl()

    def absolute_links(self):
        self.tree.getroot().make_links_absolute(self.url)

    def crawl(self, url=None, check_base=True, only_descendant=True, links=None, max_level=None,
              allowed_protocols=('http:', 'https:'), ignore_errors=True, ignore_starts=(), check_mime=()):
        '''
        Recursively crawl, returning lxml tree, dest_url and url
        Links cached, and link will be retrived only once, links = array of used links
        If check_base is True - check base_url to disallow outgoing links
        If only_descendant is True - crawl only links that starts from url
        '''
        if only_descendant is True:
            only_descendant = url
        logging.debug('Crawling url: %s' % url)
        if url:
            self.follow(url)
        if check_base is True:
            base = BASE_URL_RE.search(url).group(0)
        else:
            base = check_base
        if check_base and not self.url.startswith(base):
            logging.debug('External redirect dropped %s' % self.url)
            return
        if check_mime and (self.response.info().type not in check_mime):
            logging.debug('Response mime not allowed: %s on url %s' % (check_mime, self.url))
            return
        yield self.tree, url, self.url
        if links is None:
            links = set([])
        links.add(url)
        links.add(self.url)
        self.absolute_links()
        logging.debug('ignore starts: %s' % str(ignore_starts))
        urls = set([link.split('#')[0] for link in self.tree.xpath('//body//@href')
                if (BASE_URL_RE.search(link) and link.startswith(allowed_protocols) and not link.startswith(ignore_starts))])
        logging.debug('Found %s urls in page, %s urls in crawled list' % (len(urls), len(links)))


        if max_level is not None:
            if max_level == 0:
                logging.debug('max_deep reached')
                return
            next_max = max_level -1
        else:
            next_max = None
        logging.debug('Drilling down')
        for dest_url in urls:
            if check_base and not dest_url.startswith(base):
                logging.debug('External link dropped %s' % dest_url)
                continue
            if only_descendant and not dest_url.startswith(only_descendant):
                logging.debug('Not descendant link dropped %s' % dest_url)
                continue
            if dest_url in links:
                logging.debug('Link already crawled')
                continue
            try:
                for t, u, du in self.crawl(dest_url, base, only_descendant, links,
                                           next_max, allowed_protocols, ignore_errors, ignore_starts, check_mime):
                    yield t, u, du
            except Exception, ex:
                if ignore_errors:
                    logging.debug('Error during crawling', exc_info=ex)
                    continue
                else:
                    raise







