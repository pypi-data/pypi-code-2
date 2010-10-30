# -*- coding: utf-8 -*-
import unittest
import xml_marshaller
from xml_marshaller.xml_marshaller import load, loads, dump, dumps, dump_ns,\
                                          dumps_ns
from StringIO import StringIO
from lxml import etree
import pkg_resources

class _A:
  def __repr__(self):
    return '<A instance>'

class _B(object):
  def __repr__(self):
    return '<B instance>'

class _C(object):
  def __init__(self, attr1, attr2=None):
    self.attr1 = attr1
    self.attr2 = attr2
  def __getinitargs__(self):
    return (self.attr1, )
  def __repr__(self):
    return '<C instance>'

xsd_resource_file = pkg_resources.resource_stream(
                            xml_marshaller.xml_marshaller.__name__,
                            "doc/xml_marshaller.xsd")
xmlschema_doc = etree.parse(xsd_resource_file)
xmlschema = etree.XMLSchema(xmlschema_doc)

class TestXMLMarhsaller(unittest.TestCase):
  """
  """
  use_namespace_uri = False

  def _checkXML(self, xml_data):
    """Check generated XML against XSD
    """
    if self.use_namespace_uri:
      # Disabled for xml with namespaces.
      # Because URI is not predictable
      return
    if not isinstance(xml_data, str):
      xml_string = xml_data.read()
      xml_data.seek(0)
    else:
      xml_string = xml_data

    document_tree = etree.fromstring(xml_string)
    is_validated = xmlschema.validate(document_tree)
    log = xmlschema.error_log
    error = log.last_error
    self.assertTrue(is_validated, error)

  def test_string_serialisation(self):
    """
    """
    data_list = [None, 1, pow(2, 123L), 19.72, 1+5j,
                 "here is a string & a <fake tag>",
                 (1, 2, 3),
                 ['alpha', 'beta', 'gamma', [None, 1, pow(2, 123L), 19.72,
                                             1+5j, "& a <fake tag>"]],
                 {'key': 'value', 1: 2},
                 'éàù^ç'.decode('utf-8'),
                 set(('a', 1,)),
                 True,
                 False,
                ]
    if self.use_namespace_uri:
      dumper = dumps_ns
    else:
      dumper = dumps
    for item in data_list:
      dumped = dumper(item)
      self._checkXML(dumped)
      self.assertEquals(item, loads(dumped))

  def test_file_serialisation(self):
    """
    """
    data_list = [None, 1, pow(2, 123L), 19.72, 1+5j,
                 "here is a string & a <fake tag>",
                 (1, 2, 3),
                 ['alpha', 'beta', 'gamma', [None, 1, pow(2, 123L), 19.72,
                                             1+5j, "& a <fake tag>"]],
                 {'key': 'value', 1: 2},
                 'éàù^ç'.decode('utf-8'),
                 set(('a', 1,)),
                 True,
                 False,
                ]
    if self.use_namespace_uri:
      dumper = dump_ns
    else:
      dumper = dump
    for item in data_list:
      file_like_object = StringIO()
      dumper(item, file_like_object)
      file_like_object.seek(0)
      self._checkXML(file_like_object)
      self.assertEquals(item, load(file_like_object))

  def test_class_serialisation(self):
    """
    """
    instance = _A()
    instance.subobject = _B()
    instance.subobject.list_attribute=[None, 1, pow(2, 123L), 19.72, 1+5j,
                                      "here is a string & a <fake tag>"]
    instance.self = instance

    if self.use_namespace_uri:
      dumper = dumps_ns
    else:
      dumper = dumps

    dumped = dumper(instance)
    self._checkXML(dumped)
    new_instance = loads(dumped)
    self.assertEquals(new_instance.__class__, _A)
    self.assertEquals(instance.subobject.list_attribute,
                       new_instance.subobject.list_attribute)

    c_instance = _C('value1', attr2='value2')
    c_instance.attr3 = 'value3'
    nested_instance = _C('somevalue', 'someother')
    nested_instance.attr3 = "stillanother"
    c_instance.nested_instance = nested_instance
    c_marshalled = dumps(c_instance)
    self._checkXML(c_marshalled)
    c_unmarshalled = loads(c_marshalled)
    self.assertEquals(c_unmarshalled.attr3, c_instance.attr3)
    self.assertEquals(c_unmarshalled.attr2, c_instance.attr2)
    self.assertEquals(c_unmarshalled.attr1, c_instance.attr1)
    self.assertEquals(c_unmarshalled.__class__, _C)
    self.assertEquals(c_unmarshalled.nested_instance.__class__, _C)
    self.assertEquals(c_unmarshalled.nested_instance.attr1,
                      nested_instance.attr1)
    self.assertEquals(c_unmarshalled.nested_instance.attr2,
                      nested_instance.attr2)
    self.assertEquals(c_unmarshalled.nested_instance.attr3,
                      nested_instance.attr3)

class TestXMLMarhsallerWithNamespace(TestXMLMarhsaller):
  """
  """
  use_namespace_uri = True

if __name__ == '__main__':
  unittest.main()
