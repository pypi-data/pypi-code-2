import isodate

import datetime

class XPathProperty(object):
    """Returns a property for getting a scalar value described by an xpath property.
    
    The nodes for the value must exist in the etree. This class will not
    attempt to create them if they are missing. The xpath should not include a
    text(), etc. Don't try to use this to set attributes."""
    
    def __init__(self, xpath, namespaces, fetree=None):
        self.namespaces = namespaces
        self.xpath = xpath
        self.fetree = fetree or (lambda instance: instance.etree)
    
    def etree(self, f):
        self.fetree = f
        return self
    
    def _get_node(self, instance):
        instance_etree = self.fetree(instance)
        nodes = instance_etree.xpath(self.xpath, namespaces=self.namespaces)
        if len(nodes) == 0:
            raise AttributeError('%s has no node matching xpath %s' % (instance, self.xpath))
        if len(nodes) > 1:
            raise ValueError('%s has more than one node matching xpath %s' % (instance, self.xpath))
        return nodes[0]
    
    def __get__(self, instance, owner):
        if instance == None:
            return self
        return self._get_node(instance)

class XPathValueProperty(XPathProperty):
    def __init__(self, xpath, namespaces, datatype='xsd:string',
             fetree=None, read_only=False):
        super(XPathValueProperty, self).__init__(xpath=xpath,
                                                 namespaces=namespaces,
                                                 fetree=fetree)
        self.datatype = datatype
        self.read_only = read_only

    def datatype():
        def fget(self):
            return self._datatype
        
        def fset(self, value):
            if value not in ('xsd:string', 'xsd:dateTime'):
                raise ValueError('Unsupported dataType %s' % (self.datatype))
            self._datatype = value
        
        return locals()
    
    datatype = property(**datatype())

    def _deserialize_datatype(self, value):
        if self.datatype == 'xsd:dateTime':
            return isodate.parse_datetime(value)
        elif self.datatype == 'xsd:string':
            return value

    def _serialize_datatype(self, value):
        if self.datatype == 'xsd:dateTime':
            assert(isinstance(value, datetime.datetime))
            if value.tzname() != 'UTC':
                raise TypeError("Must supply UTC-zoned datetime to %s" % self.xpath)
            return value.isoformat()
        elif self.datatype == 'xsd:string':
            return value
    
    def __get__(self, instance, owner):
        if instance == None:
            return self
        node = self._get_node(instance)
        return self._deserialize_datatype(node.text)
    
    def __set__(self, instance, value):
        if self.read_only:
            raise AttributeError('Cannot write to %s' % (self.xpath))
        node = self._get_node(instance)
        node.text = self._serialize_datatype(value)

class XPathAttributeProperty(XPathValueProperty):
    def __init__(self, xpath, attribute, namespaces, datatype='xsd:string',
                 fetree=None, read_only=False):
        self.attribute = attribute
        super(XPathAttributeProperty, self).__init__(
            xpath, namespaces, datatype, fetree, read_only)
    
    def __get__(self, instance, owner):
        if instance == None:
            return self
        node = self._get_node(instance)
        return self._deserialize_datatype(node.get(self.attribute))
    
    def __set__(self, instance, value):
        if self.read_only:
            raise AttributeError('Cannot write to %s' % (self.xpath))
        node = self._get_node(instance)
        node.set(self.attribute, self._serialize_datatype(value))
