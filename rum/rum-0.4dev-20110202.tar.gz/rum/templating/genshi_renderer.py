import os
import logging

from genshi.template import TemplateLoader, TemplateNotFound
from genshi.core import START, XML_NAMESPACE, QName

from rum import app
from rum import BaseRenderer

log = logging.getLogger(__name__)

class GenshiRenderer(BaseRenderer):
    method = 'xhtml'
    framework_name = 'genshi'
    def __init__(self, search_path=None, auto_reload=True, cache_dir=None,
                 method=method):
        super(GenshiRenderer, self).__init__(search_path, auto_reload,
                                             cache_dir)
        self.method = method or self.method
        self.loader = TemplateLoader(
            search_path = self.search_path,
            auto_reload = self.auto_reload,
            callback = lambda tpl: tpl.filters.insert(0, add_lang_attrs),
            )

    def render(self, data, possible_templates=[]):
        template =  self.load_template(possible_templates)
        return template.generate(**data).render(method=self.method,
                                                encoding=None)

    def load_template(self, possible_templates=[]):
        #XXX: this function could be memoized
        for template in possible_templates:
            try:
                template = self.loader.load(template.lstrip(os.path.sep))
                log.debug("Template found at %s", template)
                return template
            except TemplateNotFound, e:
                log.debug("Template not found at %s: %s", template, e)
        raise LookupError("None of the following templates could be loaded: " +
                          `possible_templates`)

class GenshiXMLRenderer(GenshiRenderer):
    method = 'xml'
    framework_name = 'genshi-xml'

xml_lang = XML_NAMESPACE['lang']
lang = QName('lang')
html_tags = (QName('http://www.w3.org/1999/xhtml}html'), QName('html'))

def add_lang_attrs(stream, ctxt=None, search_text=True, msgbuf=None):
    """
    A Genshi stream filter that adds the xml:lang and lang attributes to 'html'
    tag with the current locale.
    """
    locale = app.locale
    for kind, data, pos in stream:
        if kind is START:
            tag, attrs = data
            if tag in html_tags:
                # Append lang attrs
                data = tag, (attrs | [(xml_lang, locale), (lang, locale)])
                yield kind, data, pos
                # break now avoid performing more tests on the stream
                break
        yield kind, data, pos
    # Yield the rest of the stream
    for chunk in stream:
        yield chunk
