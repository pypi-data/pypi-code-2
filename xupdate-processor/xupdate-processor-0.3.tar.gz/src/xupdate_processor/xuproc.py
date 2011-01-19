#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.sax
from lxml import etree
from cStringIO import StringIO
from content_handler import XUpdateHandler

def applyXUpdate(xml_xu_file=None,
                 xml_doc_file=None,
                 xml_xu_string=None,
                 xml_doc_string=None,
                 xml_xu_filename=None,
                 xml_doc_filename=None):
  etree_parser = etree.XMLParser(remove_blank_text=True)
  if xml_xu_file:
    xml_xu = xml_xu_file
  if xml_xu_string:
    xml_xu = StringIO(xml_xu_string)
  if xml_xu_filename:
    xml_xu = xml_xu_filename
  if xml_doc_file:
    xml_doc = xml_doc_file
  if xml_doc_string:
    xml_doc = StringIO(xml_doc_string)
  if xml_doc_filename:
    xml_doc = xml_doc_filename
  original_tree = etree.parse(xml_doc, etree_parser)
  parser = xml.sax.make_parser()
  parser.setFeature(xml.sax.handler.feature_namespaces, True)
  parser.setFeature(xml.sax.handler.feature_namespace_prefixes, True)
  parser.setContentHandler(XUpdateHandler(original_tree=original_tree))
  parser.parse(xml_xu)
  content_handler = parser.getContentHandler()
  return content_handler.result_tree

if __name__ == '__main__':
  import sys
  doc_xml_name = sys.argv[1]
  xu_xml_name = sys.argv[2]
  print etree.tostring(applyXUpdate(xml_xu_filename=xu_xml_name, xml_doc_filename=doc_xml_name), pretty_print=True)
