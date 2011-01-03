from __future__ import with_statement
import xmlwitch
from StringIO import StringIO
from xml.sax import saxutils

__all__ = ['Builder', 'Element']
__license__ = 'BSD'
__version__ = '0.2'
__author__ = "Jonas Galvez <http://jonasgalvez.com.br/>"

class Builder(xmlwitch.Builder):

    def __init__(self, encoding='utf-8', indent=' '*2, version=None):
        self._document = StringIO()
        self._document.write('<!doctype html>\n')
        self._encoding = encoding
        self._indent = indent
        self._indentation = 0
    
    def _element_class_from_element_name(self, name):
        element_class_name = '%sElement' % name.capitalize()
        element_class = globals().get(element_class_name, None)
        return element_class
        
    def __getattr__(self, name):
        element_class = self._element_class_from_element_name(name)
        if element_class is not None:
            return element_class(name, self)
        return Element(name, self)

    __getitem__ = __getattr__

class Element(xmlwitch.Element):
    
    def __call__(*args, **kargs):
        """Add a child element to the document"""
        if len(args) > 1:
            self, value = args
        else:
            self, value = args[0], Element._child_elements
        self.attributes.update(kargs)
        if value is None:
            self.builder.write_indented('<%s%s>' % (
                self.name, self._serialized_attrs()
            ))
        elif value != Element._child_elements:
            value = saxutils.escape(value)
            self.builder.write_indented('<%s%s>%s</%s>' % (
                self.name, self._serialized_attrs(), value, self.name
            ))
        return self
    
class HeadElement(Element):
    """Add a <head> element to the document"""

    def __enter__(self):
        self.builder.write_indented('<%s%s>' % (
            self.name, self._serialized_attrs()
        ))
        self.builder._indentation += 1
        self.builder.write_indented('<meta charset="%s">' % (
            self.builder._encoding
        ))
        
class ScriptElement(Element):
    """Add a single <script> element to the document"""
    
    def __call__(self, value, **kargs):
        self.attributes.update(kargs)
        if value is None:
            value = ''
        self.builder.write_indented('<script%s>%s</script>' % (
            self._serialized_attrs(), value
        ))


class ScriptsElement(Element):
    """Adds one or mroe <script> elements to the document"""

    def __enter__(self):
        def src(url, **kwargs):
            attrs = {'src': url}
            attrs.update(kwargs)
            self.builder.script(None, **attrs)
        return src

    def __call__(self):
        pass

    def __exit__(self, type, value, tb):
        pass

class LinksElement(Element):
    """Adds one or mroe <link> elements to the document"""

    def __enter__(self):
        def href(url, **kwargs):
            attrs = {'href': url}
            attrs.update(kwargs)
            self.builder.link(None, **attrs)
        return href
        
    def __call__(self):
        pass

    def __exit__(self, type, value, tb):
        pass
