# -*- coding: utf-8 -*-
##############################################################################
#
# Yoshinori OKUJI <yo@nexedi.com>
#
# Copyright (C) 2003 Nexedi SARL
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. ?See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA ?02111-1307, USA.
#
##############################################################################

from lxml import etree
parser = etree.XMLParser(remove_blank_text=True)

import sys
import getopt
import os
try:
  from cStringIO import StringIO
except ImportError:
  from StringIO import StringIO
import re
import codecs
from copy import deepcopy
from interfaces.erp5diff import IERP5Diff
import zope.interface

def isNodeEquals(old, new):
  if old.tag != new.tag or old.attrib != new.attrib:
    return False
  if old.text != new.text or old.tail != new.tail:
    return False
  if len(old) != len(new):
    return False
  for old_child, new_child in zip(old, new):
    if not isNodeEquals(old_child, new_child):
      return False
  return True

class ERP5Diff:
  """
    Make a difference between two XML documents using XUpdate.
    Use some assumptions in ERP5's data representation.

    The strategy is:
      1. Find a matching element among elements of the other XML document at the same depth.
      2. Use the first matching element, even if there can be other better elements.
      3. Assume that two elements are matching, if the tag names are identical. If either of
         them has an attribute 'id', the values of the attributes 'id' also must be identical.
      4. Don't use xupdate:rename for elements. It should be quite rare to rename tag names
         in ERP5, and it is too complicated to support this renaming.
      5. Ignore some types of nodes, such as EntityReference and Comment, because they are not
         used in ERP5 XML documents.
  """

  # Declarative interfaces
  zope.interface.implements(IERP5Diff,)

  __version__ = '0.8.1'

  def __init__(self):
    """
      Initialize itself.
    """
    self._verbose = 0
    self._result = None
    self._ns = 'http://www.xmldb.org/xupdate'

  def setVerbosity(self, verbose):
    """
      Set the verbosity.
    """
    self._verbose = verbose

  def _p(self, msg):
    """
      Print a message only if being verbose.
    """
    if self._verbose:
      sys.stderr.write(str(msg) + os.linesep)

  def _makeDocList(self, *args):
    """
      Make a list of Document objects.
    """
    doc_list = []
    for a in args:
      if isinstance(a, str):
        doc_list.append(etree.fromstring(a, parser))
      else:
        element_tree = etree.parse(a, parser)
        doc_list.append(element_tree.getroot())
    return doc_list

  def _concatPath(self, p1, p2, separator='/'):
    """
      Concatenate 'p1' and 'p2'. Add a separator between them,
      only if 'p1' does not end with a separator.
    """
    if p1.endswith(separator):
      return p1 + p2
    return p1 + separator + p2

  def _getResultRoot(self):
    """
      Return the root element of the result document.
    """
    return self._result
    #return self._result.getroottree()

  def _hasChildren(self, element):
    """
      Check whether the element has any children
    """
    return bool(len(element))

  def _getQName(self, element, attr_name):
    """Return qualified name compatible with xpath
    """
    if '{' == attr_name[0]:
      #This is a Qualified attribute
      index = attr_name.index('}')
      local_name = attr_name[index+1:]
      namespace_uri = attr_name[1:index]
      if namespace_uri == 'http://www.w3.org/XML/1998/namespace':
        prefix = 'xml'
      else:
        prefix = [t[0] for t in element.nsmap.iteritems() if t[1] == namespace_uri][0]
      return '%s:%s' % (prefix, local_name,), namespace_uri
    else:
      return attr_name, None

  def _xupdateAppendAttributes(self, attr_dict, path, nsmap=None):
    """
      Append attrib to the element at 'path'.
    """
    root = self._getResultRoot()
    append_element = etree.Element('{%s}append' % self._ns, nsmap=root.nsmap)
    append_element.attrib['select'] = path
    key_list = attr_dict.keys()
    key_list.sort()
    for name in key_list:
      val = attr_dict[name]
      attr_element = etree.Element('{%s}attribute' % self._ns, nsmap=nsmap)
      name, namespace_uri = name
      attr_element.attrib['name'] = name
      if namespace_uri:
        attr_element.attrib['namespace'] = namespace_uri
      attr_element.text = val
      append_element.append(attr_element)
    root.append(append_element)

  def _xupdateRemoveAttribute(self, name, path, nsmap=None):
    """
      Remove an attribute from the element at 'path'.
    """
    root = self._getResultRoot()
    remove_element = etree.Element('{%s}remove' % self._ns, nsmap=nsmap)
    remove_element.attrib['select'] = self._concatPath(path, 'attribute::' + name[0])
    root.append(remove_element)

  def _xupdateUpdateAttribute(self, name, val, path, nsmap=None):
    """
      Update the value of an attribute of the element at 'path'.
    """
    root = self._getResultRoot()
    update_element = etree.Element('{%s}update' % self._ns, nsmap=nsmap)
    update_element.attrib['select'] = self._concatPath(path, 'attribute::' + name[0])
    update_element.text = val
    root.append(update_element)

  def _xupdateRenameElement(self, name, path, nsmap=None):
    """
      Rename an existing element at 'path'.
    """
    root = self._getResultRoot()
    rename_element = etree.Element('{%s}rename' % self._ns, nsmap=nsmap)
    rename_element.attrib['select'] = path
    rename_element.text = name
    root.append(rename_element)

  def _xupdateUpdateElement(self, element, path, nsmap=None):
    """
      Update the contents of an element at 'path' to that of 'element'.
    """
    root = self._getResultRoot()
    update_element = etree.Element('{%s}update' % self._ns, nsmap=nsmap)
    update_element.attrib['select'] = path 
    if self._hasChildren(element):
      for child in element:
        clone_node = deepcopy(child)
        update_element.append(clone_node)
    else:
      update_element.text = element.text
    root.append(update_element)

  def _xupdateRemoveElement(self, path, nsmap=None):
    """
      Remove an element at 'path'.
    """
    root = self._getResultRoot()
    remove_element = etree.Element('{%s}remove' % self._ns, nsmap=nsmap)
    remove_element.attrib['select'] = path
    root.append(remove_element)

  def _xupdateAppendElements(self, element_list, path):
    """
      Append elements to the element at 'path'.
      xupdate:append
      xupdate:insert-before
      xupdate:insert-after
    """
    root = self._getResultRoot()
    if not element_list:
      return
    parent_element = element_list[0].getparent()
    len_total_child_list = len(parent_element)
    last_append_element = None
    for element in element_list:
      # get only elements not something else (PI and comments are ignored)
      # XXX May be support of PI and Comments should be added
      # in this case fallback to previous code
      # relative_next = element.getnext()
      relative_next_list = element.xpath('following-sibling::*[1]')
      if relative_next_list:
        relative_next = relative_next_list[0]
      else:
        relative_next = None
      relative_previous_list = element.xpath('preceding-sibling::*[1]')
      if relative_previous_list:
        relative_previous = relative_previous_list[0]
      else:
        relative_previous = None
      if relative_previous in element_list:
        #reuse same container as preceding
        append_element = last_append_element
      elif relative_next is not None and relative_next not in element_list:
        append_element = etree.SubElement(root, '{%s}insert-before' % self._ns, nsmap=element.nsmap)
        path_list = self._makeRelativePathList([relative_next], before=1)
        next_sibling_path = self._concatPath(path, path_list[0])
        append_element.attrib['select'] = next_sibling_path
      elif relative_previous is not None and relative_previous not in element_list:
        append_element = etree.SubElement(root, '{%s}insert-after' % self._ns, nsmap=element.nsmap)
        path_list = self._makeRelativePathList([relative_previous])
        preceding_sibling_path = self._concatPath(path, path_list[0])
        append_element.attrib['select'] = preceding_sibling_path
      else:
        #xupdate:append by default
        append_element = etree.SubElement(root, '{%s}append' % self._ns, nsmap=element.nsmap)
        if parent_element.index(element) == 0:
          child = 'first()'
        elif parent_element.index(element) == (len_total_child_list -1):
          child = 'last()'
        else:
          child = '%d' % (len_total_child_list - parent_element.index(element) + 1)
        append_element.attrib.update({'select': path,
                                      'child': child})
      child_element = etree.SubElement(append_element, '{%s}element' % self._ns, nsmap=root.nsmap)
      child_element.attrib['name'] = element.xpath('name()')
      namespace_uri = element.xpath('namespace-uri()')
      if namespace_uri:
        child_element.attrib['namespace'] = namespace_uri
      attr_map = element.attrib
      for name, value in attr_map.items():
        attr_element = etree.SubElement(child_element, '{%s}attribute' % self._ns, nsmap=child_element.nsmap)
        name, namespace_uri = self._getQName(element, name)
        attr_element.attrib['name'] = name
        if namespace_uri:
          attr_element.attrib['namespace'] = namespace_uri
        attr_element.text = value
      for child in element:
        clone_node = deepcopy(child)
        child_element.append(clone_node)
      if self._hasChildren(child_element) and element.text is not None:
        child_element[-1].tail = element.text
      else:
        child_element.text = element.text
      last_append_element = append_element

  def _xupdateMoveElements(self, misplaced_node_dict, path, nsmap=None):
    """
    """
    root = self._getResultRoot()
    to_remove_node_list = []
    for element_list in misplaced_node_dict.values():
      for element_tuple in element_list:
        to_remove_node_list.append(element_tuple[0])
    child_path_list = self._makeRelativePathList(to_remove_node_list)
    for child_path in child_path_list:
      to_remove_path = self._concatPath(path, child_path)
      self._xupdateRemoveElement(to_remove_path)
    for previous, element_tuple_list in misplaced_node_dict.items():
      if previous is None:
        append_element = etree.SubElement(root, '{%s}append' % self._ns, nsmap=nsmap)
        append_element.attrib['child'] = 'first()'
      else:
        append_element = etree.SubElement(root, '{%s}insert-after' % self._ns, nsmap=nsmap)
        path_list = self._makeRelativePathList([previous])
        preceding_sibling_path = self._concatPath(path, path_list[0])
        append_element.attrib['select'] = preceding_sibling_path
      for element_tuple in element_tuple_list:
        element = element_tuple[1]
        child_element = etree.SubElement(append_element, '{%s}element' % self._ns, nsmap=root.nsmap)
        child_element.attrib['name'] = element.xpath('name()')
        namespace_uri = element.xpath('namespace-uri()')
        if namespace_uri:
          child_element.attrib['namespace'] = namespace_uri
        attr_map = element.attrib
        for name, value in attr_map.items():
          attr_element = etree.SubElement(child_element, '{%s}attribute' % self._ns, nsmap=child_element.nsmap)
          name, namespace_uri = self._getQName(element, name)
          attr_element.attrib['name'] = name
          if namespace_uri:
            attr_element.attrib['namespace'] = namespace_uri
          attr_element.text = value
        for child in element:
          clone_node = deepcopy(child)
          child_element.append(clone_node)
        if self._hasChildren(child_element) and element.text is not None:
          child_element[-1].tail = element.text
        else:
          child_element.text = element.text

  def _testElements(self, element1, element2):
    """
      Test if two given elements are matching. Matching does not mean that they are identical.
    """
    # Make sure that they are elements.
    if type(element1) !=  type(element2) or type(element1) != etree._Element:
      return False

    if element1.tag != element2.tag:
      return False

    id_list = []
    for attr_map in (element1.attrib, element2.attrib):
      if 'id' in attr_map:
        id_list.append(attr_map['id'])

    if len(id_list) == 0:
      return True
    if len(id_list) == 1:
      return False
    return (id_list[0] == id_list[1])

  def _testAttributes(self, element1, element2, path):
    """
      Test attrib of two given elements. Add differences, if any.
    """
    # Make a list of dictionaries of the attributes.
    dict_list = []
    for element in (element1, element2):
      d = {}
      for name, value in element.attrib.items():
        name, namespace_uri = self._getQName(element, name)
        d[(name, namespace_uri)] = value
      dict_list.append(d)
    dict1, dict2 = dict_list

    # Find all added or removed or changed attrib.
    #sort key list to stick expected output
    key_list1 = dict1.keys()
    key_list1.sort()
    for name1 in key_list1:
      val1 = dict1[name1]
      if name1 in dict2:
        if val1 != dict2[name1]:
          # The value is different.
          self._xupdateUpdateAttribute(name1, dict2[name1], path, nsmap=element.nsmap)
        # Mark this attribute.
        dict2[name1] = None
      else:
        # This attribute is removed.
        self._xupdateRemoveAttribute(name1, path, nsmap=element.nsmap)
    d = {}
    for name2, val2 in dict2.iteritems():
      if val2 is not None:
        # This attribute is added.
        d[name2] = val2
    if d != {}:
      self._xupdateAppendAttributes(d, path, nsmap=element.nsmap)

  def _checkEmptiness(self, element):
    """
      Check if an element has Element or Text nodes
    """
    for child in element:
      if type(child) == etree._Element:
        return False
    if element.text is not None:
      return False
    return True

  def _checkIgnoreText(self, element):
    """
      Determine if text should be ignored by heuristics,
      because ERP5 does not define any schema at the moment.
      We ignore white-space text nodes between elements.
      pseudo code:
      tree = parse("
      <node>
         </node>")
      tree.node.text == '\n    '
    """
    return not [text for text in element.xpath('text()') if text.strip()]

  def _makeRelativePathList(self, element_list, before=0):
    """
      Make a list of relative paths from a list of elements.
    """

    path_list = []
    for element in element_list:
      # Check if this element has an attribute 'id'.s
      id_val = None
      attr_map = element.attrib
      for name, value in attr_map.items():
        if name in ('id', 'gid',):
          id_val = value
          id_of_id = name
          break

      if id_val is not None:
        # If an attribute 'id' or 'gid' is present, uses the attribute for convenience.
        position_predicate = ''
        len_all_similar_sibling = len(element.xpath('../*[@%s = "%s"]' %\
                                                           (id_of_id, id_val)))
        if len_all_similar_sibling > 1:
          position = len_all_similar_sibling - \
              element.xpath('count(following-sibling::%s[@%s = "%s"])' %\
                                   (element.xpath('name()'), id_of_id, id_val),
                                                      namespaces=element.nsmap)
          position_predicate = '[%i]' % position
        path_list.append("%s[@%s='%s']%s" % (element.xpath('name()'), id_of_id,
                                                  id_val, position_predicate,))
        # Increase the count, for a case where other elements with the same tag name do not have
        # 'id' attrib.
      else:
        len_all_similar_sibling = len(element.findall('../%s' % element.tag))
        if len_all_similar_sibling > 1:
          position = len_all_similar_sibling - len(list(element.itersiblings(tag=element.tag)))
          path_list.append('%s[%d]' % (element.xpath('name()'), position-before or 1))
        else:
          path_list.append(element.xpath('name()'))

    return path_list

  def _aggregateElements(self, element):
    """
      Aggregate child elements of an element into a list.
    """
    return [child for child in element if type(child) == etree._Element]

  def _aggregateText(self, element):
    """
      Aggregate child text nodes of an element into a single string.
    """
    return '%s' % element.xpath('string(.)')

  def _removeStrictEqualsSubNodeList(self, old_list, new_list):
    """Remove inside list all elements which are similar
    by using c14n serialisation
    This script returns the same list of nodes whithout twins from other list
    and a dictionary with nodes whose position has changed.
    misplaced_node_dict :
      key = anchor_node (node from which the moving node_list will be append)
      value = list of tuple:
                  -old_element (to remove)
                  -new_element (to insert)
    """
    old_candidate_list = old_list[:]
    new_candidate_list = new_list[:]
    misplaced_node_dict = {}
    misplaced_node_dict_after = {}
    misplaced_node_dict_before = {}
    old_new_index_mapping = {}
    for old_index, old_element in enumerate(old_list):
      if old_element not in old_candidate_list:
        continue
      for new_element in new_list:
        new_index = new_list.index(new_element)
        if new_element not in new_candidate_list:
          continue
        node_equality = isNodeEquals(old_element, new_element)
        if node_equality:
          index_key_on_new_tree = new_element.getparent().index(new_element)
          old_new_index_mapping[index_key_on_new_tree] = old_element
          new_start = new_index + 1
          if new_element in new_candidate_list:
            new_candidate_list.remove(new_element)
          if old_element in old_candidate_list:
            old_candidate_list.remove(old_element)
          if old_index == new_index:
            break
          elif old_index < new_index:
            misplaced_node_dict = misplaced_node_dict_after
          else:
            misplaced_node_dict = misplaced_node_dict_before
          previous_new_element = new_element.getprevious()
          for key, preceding_value_list in misplaced_node_dict.items():
            for element_tuple in preceding_value_list:
              if previous_new_element == element_tuple[1]:
                #reuse the same previous as much as possible
                if key is not None:
                  previous_new_element = previous_new_element.getparent()[key]
                else:
                  previous_new_element = None
                break
          if previous_new_element is not None:
            index_key_on_new_tree = previous_new_element.getparent().index(previous_new_element)
          else:
            index_key_on_new_tree = None
          misplaced_node_dict.setdefault(index_key_on_new_tree, []).append((old_element, new_element))
          break

    # Chosse the lighter one to minimise diff
    after_dict_weight = sum(len(i) for i in misplaced_node_dict_after.values())
    before_dict_weight = sum(len(i) for i in misplaced_node_dict_before.values())
    if after_dict_weight > before_dict_weight and before_dict_weight:
      misplaced_node_dict = misplaced_node_dict_before
    elif after_dict_weight <= before_dict_weight and after_dict_weight:
      misplaced_node_dict = misplaced_node_dict_after
    else:
      misplaced_node_dict = {}

    for k, v in misplaced_node_dict.items():
      if k in old_new_index_mapping:
        value = misplaced_node_dict[k]
        misplaced_node_dict[old_new_index_mapping[k]] = value
      if k is not None:
        #if the element which suppose to support insert-after does not exist in old_tree,
        #its just an added node not an moving
        #None means that the node will become first child, so keep it
        del misplaced_node_dict[k]
    return old_candidate_list, new_candidate_list, misplaced_node_dict


  def _compareChildNodes(self, old_element, new_element, path):
    """
      Compare children of two elements, and add differences into the result, if any.
      Call itself recursively, if these elements have grandchilden.
    """
    self._p("Comparing %s with %s at %s..." % (repr(old_element), repr(new_element), path))

    # First, determine if they are empty.
    old_is_empty = self._checkEmptiness(old_element)
    new_is_empty = self._checkEmptiness(new_element)

    if old_is_empty and new_is_empty:
      # Nothing to do.
      self._p("Both are empty.")
      pass
    else:
      # Second, determine if text should be ignored.
      old_ignore_text = self._checkIgnoreText(old_element)
      new_ignore_text = self._checkIgnoreText(new_element)

      if old_ignore_text != new_ignore_text:
        # This means that the semantics of this element is quite different.
        self._p("One of them has only text and the other does not, so just update all the contents.")
        self._xupdateUpdateElement(new_element, path, nsmap=new_element.nsmap)
      elif not old_ignore_text:
        # The contents are only text.
        self._p("Both have only text.")
        old_text = self._aggregateText(old_element)
        new_text = self._aggregateText(new_element)
        if old_text != new_text:
          self._p("They differ, so update the elements.")
          self._xupdateUpdateElement(new_element, path, nsmap=new_element.nsmap)
      else:
        # The contents are elements.
        self._p("Both have elements.")
        old_list = self._aggregateElements(old_element)
        new_list = self._aggregateElements(new_element)
        old_list, new_list, misplaced_node_dict = self._removeStrictEqualsSubNodeList(old_list, new_list)
        path_list = self._makeRelativePathList(old_list)
        new_start = 0
        new_len = len(new_list)
        # Usefull set to detect orphan in new_list
        new_object_left_index_set = set()
        for old_node, node_path in zip(old_list, path_list):
          child_path = self._concatPath(path, node_path)
          for new_current in range(new_start, new_len):
            new_node = new_list[new_current]
            if self._testElements(old_node, new_node):
              self._testAttributes(old_node, new_node, child_path)
              self._compareChildNodes(old_node, new_node, child_path)
              new_start = new_current + 1
              if new_current in new_object_left_index_set:
                new_object_left_index_set.remove(new_current)
              break
            else:
              new_object_left_index_set.add(new_current)
          else:
            # There is no matching node. So this element must be removed.
            self._xupdateRemoveElement(child_path, old_node.nsmap)
        if new_len > new_start:
          # There are remaining nodes in the new children.
          self._xupdateAppendElements(new_list[new_start:new_len], path)
          # if New children are allready added, clean up new_object_left_index_set
          [new_object_left_index_set.remove(index)\
           for index in range(new_start, new_len) if\
           index in new_object_left_index_set]
        if new_object_left_index_set:
          self._xupdateAppendElements([new_list[index] for index \
                                           in new_object_left_index_set], path)
        if misplaced_node_dict:
          self._xupdateMoveElements(misplaced_node_dict, path)

  def compare(self, old_xml, new_xml):
    """
      Compare two given XML documents.
      If an argument is a string, it is assumed to be a XML document itself.
      Otherwise, it is assumed to be a file object which contains a XML document.
    """
    old_doc, new_doc = self._makeDocList(old_xml, new_xml)
    old_root_element = old_doc.getroottree().getroot()
    new_root_element = new_doc.getroottree().getroot()
    try:
      if self._result is not None:
        self._result = None 
      self._result = etree.Element('{%s}modifications' % self._ns, nsmap={'xupdate': self._ns})
      self._result.set('version', '1.0')
      if self._testElements(old_root_element, new_root_element):
        qname = old_root_element.xpath('name()')
        self._testAttributes(old_root_element, new_root_element, '/%s' % qname)
        self._compareChildNodes(old_root_element, new_root_element, '/%s' % qname)
      else:
        # These XML documents seem to be completely different...
        if old_root_element.tag != new_root_element.tag:
          nsmap = old_root_element.nsmap
          nsmap.update(new_root_element.nsmap)
          self._xupdateRenameElement(new_root_element.xpath('name()'), '/%s' % old_root_element.xpath('name()'), nsmap)
        qname = new_root_element.xpath('name()')
        self._testAttributes(old_root_element, new_root_element, '/%s' % qname)
        self._compareChildNodes(old_root_element, new_root_element, '/%s' % qname)
    finally:
      del old_doc
      del new_doc

  def output(self, output_file=None):
    """
      Output the result of parsing XML documents to 'output_file'.
      If it is not specified, stdout is assumed.
    """
    if output_file is None:
      output_file = sys.stdout
    # stream
    xml = etree.tostring(self._result, encoding='utf-8', pretty_print=True)
    output_file.write(xml)

  def outputString(self):
    """
      Return the result as a string object.
    """
    io = StringIO()
    self.output(io)
    ret = io.getvalue()
    io.close()
    return ret

def main():
  """
    The main routine of ERP5Diff.
  """
  try:
    opts, args = getopt.getopt(sys.argv[1:], "ho:v", ["help", "output=", "verbose"])
  except getopt.GetoptError, msg:
    print msg
    print "Try ``erp5diff --help'' for more information."
    sys.exit(2)
  output = None
  verbose = 0
  for o, a in opts:
    if o == "-v":
      verbose = 1
    elif o in ("-h", "--help"):
      print '''Usage: erp5diff [OPTION]... OLD_XML NEW_XML
Make a difference between two XML documents in XUpdate format.

    -h, --help          display this message and exit
    -o, --output=FILE   output the result to the file FILE
    -v, --verbose       print verbose messages

Report bugs to <yo@nexedi.com>.'''
      sys.exit()
    elif o in ("-o", "--output"):
      output = a

  if len(args) != 2:
    if len(args) > 2:
      print "Too many arguments."
    else:
      print "Too few arguments."
    print "Try ``erp5diff --help'' for more information."
    sys.exit(2)

  d = ERP5Diff()
  d.setVerbosity(verbose)

  old_xml = open(args[0])
  new_xml = open(args[1])
  d.compare(old_xml, new_xml)
  old_xml.close()
  new_xml.close()

  try:
    if output is not None:
      file = open(output, 'w')
    else:
      file = None
    d.output(file)
  except:
    if output is not None:
      file.close()
      os.remove(output)
    raise
  else:
    if file is not None:
      file.close()

  sys.exit()

if __name__ == '__main__':
  main()
