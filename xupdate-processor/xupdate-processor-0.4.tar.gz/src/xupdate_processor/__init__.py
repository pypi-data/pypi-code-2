# -*- coding: utf-8 -*-
from xuproc import applyXUpdate
from lxml import etree

def main():
  from optparse import OptionParser
  usage = "usage: %prog xupdate_path document_path"
  parser = OptionParser(usage=usage)

  options, args = parser.parse_args()

  if len(args) != 2:
    print parser.print_help()
    parser.error('incorrect number of arguments')

  xu_xml_name = args[0]
  doc_xml_name = args[1]

  print etree.tostring(applyXUpdate(xml_xu_filename=xu_xml_name,
                                    xml_doc_filename=doc_xml_name),
                       pretty_print=True)
