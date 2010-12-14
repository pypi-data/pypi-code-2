"""
This is a simple producer taking a file in input and reading it with a descriptor
"""

from pyf.componentized.components import Producer
from pyf.componentized import ET

from pyjon.descriptors import Descriptor

import codecs
import decimal

import logging
from pyf.componentized.configuration.keys import SimpleKey, RepeatedKey,\
    CompoundKey
from pyf.componentized.configuration.fields import InputField

log = logging.getLogger(__name__)

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http.response.html import HtmlResponse
from scrapy.http.request import Request
from urllib2 import urlopen
from pyf.transport import Packet

class PyFSpider(BaseSpider):
    """ A spider that parses more values than the ones defined by scrapy.
    Must be overriden in another class. """
    
    already_checked = None
    
    def parse(self, response):
        if self.already_checked is None:
            self.already_checked = list()
            
        hxs = HtmlXPathSelector(response)
        items = hxs.select(self.item_selector)
        for item in items:
            yield Packet(dict([(key, item.select(getter).extract())
                               for key, getter in self.field_selectors.iteritems()]))
            
        if self.link_selector:
            for link in hxs.select(self.link_selector):
                if self.url_base:
                    link = self.url_base + link.extract()
                    
                if link not in self.already_checked:
                    self.already_checked.append(link)
                    yield Request(url=link)

class WebExtractor(Producer):
    """ This is a producer that will take urls and will output items based on xpath selectors.
    """
    name = "webextractor"
    configuration = [RepeatedKey('start_urls', 'start_url',
                                 default=[''],
                                 content=SimpleKey('start_url',
                                                   help_text='ex. "http://www.example.com/listing"')),
                     SimpleKey('item_selector',
                               label="Individual item XPath",
                               help_text="ex. '//ul[1]/li'"),
                     RepeatedKey('fields', 'field',
                                 default=[dict(name='', xpath='')],
                                 content=CompoundKey('field',
                                                     text_value='xpath',
                                                     attributes={'name': 'name'},
                                                     fields=[InputField('name', label="Attribute",
                                                                        help_text="Target attribute"),
                                                             InputField('xpath', label="Field XPath",
                                                                        help_text='Path to search (ex. "p/*/text()")')])),
                    SimpleKey('link_selector',
                              label="Other pages urls xpath",
                              help_text="ex \"p[@id='links']/a/@href\" (optionnal)"),
                    SimpleKey('url_base',
                              label="Base url for links",
                              help_text='ex. "http://wwww.example.com/"'),
                    SimpleKey('page_limit',
                              label="Limit to N Pages",
                              default='10')]
                        
    
    def __init__(self, config_node, process_name):
        """ Initialize the Descriptor Source Extractor
        @param config_node: Configuration
        @type config_node: ET instance

        @param process name: Current process name
        @type process name: string
        """
        super(WebExtractor, self).__init__(config_node, process_name)
        
        self.handled_pages = 0
        
    @property
    def DynamicSpider(self):
        return self.__create_spider_class('DynamicSpider',
                                          self.get_config_key('start_urls'),
                                          self.get_config_key('item_selector'),
                                          dict([(field.get('name'),
                                                 field.get('xpath'))
                                                for field in self.get_config_key('fields')]),
                                          self.get_config_key('link_selector') or None,
                                          self.get_config_key('url_base'))
        
    def __create_spider_class(self, name, start_urls, item_selector, field_selectors, link_selector, url_base):
        return type.__new__(type,
                            name.title().replace(' ', ''),
                            (PyFSpider,),
                            dict(name=name,
                                 start_urls=start_urls,
                                 item_selector=item_selector,
                                 field_selectors=field_selectors,
                                 link_selector=link_selector,
                                 url_base=url_base))
    
    def __handle_request(self, spider, request):
        if int(self.get_config_key('page_limit', 10)) != -1:
            if self.handled_pages >= int(self.get_config_key('page_limit', 10)):
                raise StopIteration
        self.handled_pages += 1
        
        log.debug('%s: checking %s' % (self.name, request.url))
        resbody = urlopen(request.url)
        res = HtmlResponse(request.url, body=resbody.read())
        
        for item in spider.parse(res):
            if isinstance(item, Request):
                for subitem in self.__handle_request(spider, item):
                    yield subitem
                    
            yield item
    
    def launch(self,
               progression_callback=None,
               message_callback=None,
               params=None):
        """
        Extracts the data from a file using the passed descriptor.
        If there is a data item in params, just yield it.
        
        Available params in params dict:
        - data: if provided: iterates over the lines in data and yield them.
        - descriptor: use this descriptor to read the data
        - source: use this file-like object as data source
        - source_filename: use this file as data source.
                           requires the source_encoding config key.
        """
        
        if not progression_callback:
            progression_callback = lambda x: log.debug('Progression : %s' % x)

        if not message_callback:
            message_callback = log.info
        
        progression_callback(0)
        
        spider = self.DynamicSpider()
        
        for req in spider.start_requests():
            for it in self.__handle_request(spider, req):
                yield it
        
        progression_callback(100)