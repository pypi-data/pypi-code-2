"""Middleware"""

import lxml.html
import logging
import webob
from config import listify_param
from urlparse import urljoin
from resolver import ResolverList

logger = logging.getLogger("develjuice")
    
try:
    from repoze.xmliter import XMLSerializer
    XMLSerializer = XMLSerializer       #to satisfy pylint
except ImportError:
    def XMLSerializer(tree, serializer=lxml.html.tostring):
        return serializer(tree, pretty_print=True)


class JsProcessor(object):
    """Handler of the <script> rewrite"""
    
    @staticmethod
    def select_elements(tree):
        return tree.xpath('.//head/script[@src]')

    @staticmethod
    def fetch_url(element):
        return element.attrib['src']

    @staticmethod
    def resolve_method(resolver):
        return resolver.resolve_js
        
    @staticmethod
    def update_url(element, replace_url):
        element.attrib['src'] = replace_url

    @staticmethod
    def create_new_element(element, new_url):
        return element.makeelement('script', dict(
            type = 'text/javascript',
            src = new_url,
            ))


class CssProcessor(object):
    """Handlers of the <link> rewrite"""
    
    @staticmethod
    def select_elements(tree):
        return tree.xpath('.//head/link[@href]')

    @staticmethod
    def fetch_url(element):
        return element.attrib['href']

    @staticmethod
    def resolve_method(resolver):
        return resolver.resolve_css
        
    @staticmethod
    def update_url(element, replace_url):
        element.attrib['href'] = replace_url

    @staticmethod
    def create_new_element(element, new_url):
        return element.makeelement('link', dict(
            type = 'text/css',
            rel = 'stylesheet',
            href = new_url,
            ))






class DevelJuiceMiddleware(object):
    
    def __init__(self, app, global_conf,
            ResolverList=ResolverList,
            base_urls = '', 
            use_request_url = 'true',
            # config contains the followings: url_prefix=None, filepath=None, resources=None, extend_resources=None,
            **config
            ):
        self.app = app
        self.global_conf = global_conf
        self.base_urls = listify_param(base_urls)
        
        if use_request_url not in ('true', 'True', 'false', 'False'):
            raise ValueError('(`use_request_urls`) must be true or false.')
        if use_request_url in ('true', 'True'):
            self.base_urls.append(None)
        new = []
        for base_url in self.base_urls:
            if base_url and base_url[-1] == '/':
                base_url == base_url[:-1]
            new.append(base_url)
        self.base_urls = new
        self.resolver = ResolverList(self.base_urls)
        # Add the resources
        self.resolver.add_current_section(config, inifile=global_conf['__file__'], section_name=None)
        #check all the section
        for res in self.resolver:
            for resource in res.resources:
                for devel_resource in res.resources[resource]:
                    if devel_resource[1] is not None:
                        try:
                            self.resolver.sections[devel_resource[1], devel_resource[2]]
                        except KeyError:
                            raise ValueError, \
                                'Resource "%s" is imported from section "%s" in file "%s",' \
                                ' but this section is missing from extend_resources. Please include it!' \
                                % (devel_resource[0], devel_resource[2], devel_resource[1])                        

    def __call__(self, environ, start_response):
        #base_urls = list(self.base_urls)
        request_base_url = environ['wsgi.url_scheme'] + '://' + environ['REMOTE_ADDR'] + ':' + environ['SERVER_PORT']
        request = webob.Request(environ)
        response = request.get_response(self.app, catch_exc_info=True)
        content_type = response.content_type
        if content_type and content_type.startswith('text/html'):
            # Attempt to parse this, although the content type may be lying.
            body = response.body.strip()
            if body:
                tree = lxml.html.fromstring(body)
                changed = False
                # process js and css
                for processor in (JsProcessor, CssProcessor):
                    elements = processor.select_elements(tree)
                    for element in elements:
                        url =  processor.fetch_url(element)
                        # make a full url, even if relative
                        url = urljoin(request.url, url, True)
                        if url is not None:
                            replace_url_list = processor.resolve_method(self.resolver)(url, request_base_url)
                            replace_url = replace_url_list[-1]
                            dependencies = replace_url_list[:-1]
                            if replace_url != url:
                                changed = True
                                processor.update_url(element, replace_url)
                            if dependencies:
                                changed = True
                                for new_url in dependencies:
                                    new_el = processor.create_new_element(element, new_url)
                                    element.addprevious(new_el)
                # Regenerate html
                if changed:
                    response.body = XMLSerializer(tree)
        return response(environ, start_response)


def make_middleware(app, global_conf, **kw):
    assert 'Resolver' not in kw
    return DevelJuiceMiddleware(app, global_conf, **kw)
