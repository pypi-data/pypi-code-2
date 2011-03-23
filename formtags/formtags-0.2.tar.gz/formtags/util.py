"""
Utility functions and classes
"""
import re

import webhelpers.html.builder

# Decorator                            
def html_tag(func):
    """
    Decorator for html tags. Converts the given extra attributes to a
    HTMLAttributes instance.
    """
    def wrapper(cls, attribute_name, *args, **kwargs):
        """ Convert kwargs to a html attributes dict """
        for key, value in kwargs.iteritems():
            if key.endswith('_'):
                kwargs.pop(key)
                kwargs[key[:-1]] = value
        
        attributes = HTMLAttributes()
        attributes.update(kwargs)
        attributes.overwrite('class', CSSAttribute(attributes.get('class', '')))
        
        return func(cls, attribute_name, *args + (attributes,))
    return wrapper

# Decorator
def literal(func):
    """ 
    Wrap the returned data in a webhelpers.html.builder.literal class
    """
    def wrapper(*args, **kwargs):
        """ wrapper method """
        result = func(*args, **kwargs)
        return webhelpers.html.builder.literal(result)
    return wrapper

def walk_object(base, name):
    """
    Walk over an object given as obj.property.property
    """
    nodes = name.split('.')
    pointer = base
    for node in nodes:
        if hasattr(pointer, node):
            pointer = getattr(pointer, node)
        else:
            raise AttributeError('Attribute "%s" does not exist.' %
                     name)
    return pointer
    
class CSSAttribute(set):
    """
    Small wrapper around the set type.
    """
    _re_split = re.compile('\s+')
    def __init__(self, value=None):
        """
        Value should be a string with css classes
        """
        super(CSSAttribute, self).__init__()
        if value:
            self.update(self._re_split.split(value))
        
        
    def __str__(self):
        """
        Return the css classes as a string
        """
        return ' '.join(self)


class HTMLAttributes(dict):
    """
    Small wrapper around the dict type. This class doesn't allow by default
    to overwrite an already existing key.
    """    
    def __setitem__(self, key, value):
        """
        Set the html attribute key to the given value. Only works if the
        html attribute isn't defined already.
        """
        if key not in self:
            dict.__setitem__(self, key, value)
    
    def overwrite(self, key, value):
        """
        Overwrite a previous given html attribute.
        """
        dict.__setitem__(self, key, value)
    
    def __str__(self):
        """
        Return a HTML formatted string with all the attributes.
        """
        attr = ' '.join('%s="%s"' % (key, self._escape(value)) for key, value
                                     in self.iteritems() if value is not None)
        return attr
    
    def space_string(self):
        """
        Return the HTML formatted string (see __str__) prepended with a space
        if the string contains data.
        """
        string = str(self)
        if string:
            return ' '+string
        return ''
        
    def _escape(self, value):
        """
        Escape the given value using webhelpers.html.builder.escape
        """
        return webhelpers.html.builder.escape(value)