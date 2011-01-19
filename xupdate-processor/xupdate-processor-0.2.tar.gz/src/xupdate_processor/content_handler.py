# -*- coding: utf-8 -*-
from lxml import etree
from lxml.etree import Element, _ElementTree, ProcessingInstruction, Comment
from xml.sax.handler import ContentHandler
from xml.sax import SAXParseException
from copy import deepcopy
import re

attribute_axes_regex = re.compile(r'(?P<parent_node>^.*(?=/(attribute::|@)))(?P<attribute_axes>/(attribute::|@))(?P<attribute_id>[\w\-:]*)$')

XUPDATE_NS = 'http://www.xmldb.org/xupdate'

class XUpdateValidationException(SAXParseException):
  pass

class XUpdateHandler(ContentHandler):
  """
  Handler to parse xupdate documents
  """

  def __init__(self, original_tree=None):
    """
    original_tree: lxml tree
    """
    ContentHandler.__init__(self)
    if not isinstance(original_tree, _ElementTree):
      original_tree = original_tree.getroottree()
    self._modification_starts = False
    self.result_tree = deepcopy(original_tree)
    self.nsmap = {}

    self._variable_dict = {}

    self._node_stack = []
    self._current_position_string_stack = []
    self._string_stack = []
    self._to_remove_node_list = []
    self._parent_node_append_stack = []
    self._current_position_to_append_stack = []
    self._attr_name_stack = []

  def startPrefixMapping(self, prefix, uri):
    self.nsmap[prefix] = uri

  def startElementNS(self, name, qname, attrs):
    uri, localname = name
    #store position of current string_stack
    #to join all characters contents for the current element only
    self._current_position_string_stack.append(len(self._string_stack))
    if uri == XUPDATE_NS:
      #This is an xupdate action
      if localname == 'modifications':
        if self._modification_starts:
          raise XUpdateValidationException('{%s}modifications already read' % XUPDATE_NS)
        else:
          self.modification_starts = True
      elif localname == 'update':
        #get the node fromp xpath expression
        xpath_expression = attrs.getValueByQName('select')
        matched_re = attribute_axes_regex.match(xpath_expression)
        if matched_re is not None:
          #Unfortunately, etree manage attributes as smart_string results (they known their parents)
          # But they do not know in which attribute they are linked
          #so, use a workaround to update attribute nodes like dictionaries 
          #('/attribute::' or '/@' axes)
          #XXX This code will be removed after release of lxml 2.2.4
          parent_node_expression = matched_re.group('parent_node')
          attribute_id = matched_re.group('attribute_id')
          if ':' in attribute_id:
            prefix, local_name = attribute_id.split(':')
            uri = self.nsmap[prefix]
            attribute_id = '{%s}%s' % (uri, local_name,)
          node = self.result_tree.xpath(parent_node_expression, namespaces=self.nsmap)[0]
          self._node_stack.append((node, attribute_id))
          self._current_position_to_append_stack.append(len(self._node_stack))
        else:
          node = self.result_tree.xpath(xpath_expression, namespaces=self.nsmap)[0]
          self._node_stack.append(node)
          self._current_position_to_append_stack.append(len(self._node_stack))
      elif localname == 'remove':
        xpath_expression = attrs.getValueByQName('select')
        matched_re = attribute_axes_regex.match(xpath_expression)
        if matched_re is not None:
          parent_node_expression = matched_re.group('parent_node')
          attribute_id = matched_re.group('attribute_id')
          node = self.result_tree.xpath(parent_node_expression, namespaces=self.nsmap)[0]
          if ':' in attribute_id:
            attr_prefix, local_name = attribute_id.split(':')
            uri = self.nsmap[attr_prefix]
            attribute_id = '{%s}%s' %  (uri, local_name,)
          del node.attrib[attribute_id]
        else:
          node = self.result_tree.xpath(xpath_expression, namespaces=self.nsmap)[0]
          self._to_remove_node_list.append(node)
      elif localname == 'append':
        node = self.result_tree.xpath(attrs.getValueByQName('select'))[0]
        self._parent_node_append_stack.append(node)
        xpath_position = attrs.getValueByQName('child')
        self._current_position_to_append_stack.append((xpath_position, len(self._node_stack)))
      elif localname == 'element':
        tag_name = attrs.getValueByQName('name')
        nsmap = {}
        if ':' in tag_name:
          prefix, local_name = tag_name.split(':')
          uri = attrs.getValueByQName('namespace')
          tag_name = '{%s}%s' % (uri, local_name,)
          nsmap[prefix] = uri
        node = Element(tag_name, nsmap=nsmap)
        self._node_stack.append(node)
        self._current_position_to_append_stack.append(len(self._node_stack))
      elif localname == 'attribute':
        node = self._node_stack[-1]
        self._node_stack.append(node)
        attr_name = attrs.getValueByQName('name')
        if ':' in attr_name:
          uri = attrs.getValueByQName('namespace')
          prefix, local_name = attr_name.split(':')
          attr_name = '{%s}%s' % (uri, local_name,)
        self._attr_name_stack.append(attr_name)
      elif localname == 'insert-before':
        node = self.result_tree.xpath(attrs.getValueByQName('select'), namespaces=self.nsmap)[0]
        self._current_position_to_append_stack.append(len(self._node_stack))
        self._node_stack.append(node)
      elif localname == 'insert-after':
        node = self.result_tree.xpath(attrs.getValueByQName('select'), namespaces=self.nsmap)[0]
        self._current_position_to_append_stack.append(len(self._node_stack))
        self._node_stack.append(node)
      elif localname == 'rename':
        node = self.result_tree.xpath(attrs.getValueByQName('select'), namespaces=self.nsmap)[0]
        self._node_stack.append(node)
      elif localname == 'processing-instruction':
        node_name = attrs.getValueByQName('name')
        node = ProcessingInstruction(node_name)
        self._node_stack.append(node)
      elif localname == 'comment':
        node = Comment()
        self._node_stack.append(node)
      elif localname == 'variable':
        name = attrs.getValueByQName('name')
        node = self.result_tree.xpath(attrs.getValueByQName('select'), namespaces=self.nsmap)[0]
        self._variable_dict[name] = node
      elif localname == 'value-of':
        select = attrs.getValueByQName('select')
        if select[0] == '$':
          #This is a variable
          node = self._variable_dict[select[1:]]
        else:
          #This is an xpath expression
          node = self.result_tree.xpath(select, namespaces=self.nsmap)[0]
        self._node_stack.append(deepcopy(node))
      else:
        raise NotImplementedError(localname)
    else:
      nsmap = {}
      if uri:
        localname = '{%s}%s' % (uri, localname)
        nsmap = {qname.split(':', 1)[0]: uri}
      new_node = Element(localname, nsmap=nsmap)
      new_attr_dict = {}
      for attr_key, value in attrs.items():
        uri, attr_name = attr_key
        if uri:
          attr_name = '{%s}%s' % (uri, attr_name)
        new_attr_dict[attr_name] = value
      new_node.attrib.update(new_attr_dict)
      self._node_stack.append(new_node)
      self._current_position_to_append_stack.append(len(self._node_stack))

  def characters(self, content):
    if content.strip():
      self._string_stack.append(content)

  def endElementNS(self, name, qname):
    uri, localname = name
    last_position = self._current_position_string_stack.pop()
    token_list = [self._string_stack.pop() for token in self._string_stack[last_position:]]
    token_list.reverse()
    content = ''.join(token_list)
    if not content.strip():
      content = None
    if uri == XUPDATE_NS:
      #This is an xupdate action
      if localname == 'modifications':
        pass
      elif localname == 'update':
        #get the node fromp xpath expression
        node_stack_position = self._current_position_to_append_stack.pop()
        node_to_append_list = [self._node_stack.pop() for node in self._node_stack[node_stack_position:]]
        node = self._node_stack.pop()
        if isinstance(node, tuple):
          #This is a attribute update
          node, attribute_id = node
          node.attrib.update({attribute_id: content})
        else:
          node.extend(node_to_append_list)
          if len(node):
            node[-1].tail = content
          else:
            node.text = content
      elif localname == 'remove':
        pass
      elif localname == 'append':
        xpath_position, node_stack_position = self._current_position_to_append_stack.pop()
        parent_node = self._parent_node_append_stack.pop()
        node_to_append_list = [self._node_stack.pop() for node in self._node_stack[node_stack_position:]]
        if xpath_position == 'first()':
          for node in node_to_append_list:
            parent_node.insert(0, node)
        else:
          #Include last()
          node_to_append_list.reverse()
          parent_node.extend(node_to_append_list)
      elif localname == 'element':
        node_stack_position = self._current_position_to_append_stack.pop()
        node_to_append_list = [self._node_stack.pop() for node in self._node_stack[node_stack_position:]]
        node_to_append_list.reverse()
        node = self._node_stack[-1]
        node.extend(node_to_append_list)
        if len(node):
          node[-1].tail = content
        else:
          node.text = content
      elif localname == 'attribute':
        node = self._node_stack.pop()
        attr_name = self._attr_name_stack.pop()
        node.attrib.update({attr_name: content})
      elif localname == 'insert-before':
        node_stack_position = self._current_position_to_append_stack.pop()
        node_to_append_list = [self._node_stack.pop() for node in self._node_stack[node_stack_position+1:]]
        node_to_append_list.reverse()
        sibling_node = self._node_stack.pop()
        for node in node_to_append_list:
          sibling_node.addprevious(node)
      elif localname == 'insert-after':
        node_stack_position = self._current_position_to_append_stack.pop()
        node_to_append_list = [self._node_stack.pop() for node in self._node_stack[node_stack_position+1:]]
        sibling_node = self._node_stack.pop()
        for node in node_to_append_list:
          sibling_node.addnext(node)
      elif localname == 'rename':
        node = self._node_stack.pop()
        if ':' in content:
          #Transform QName to compatible Tag name for lxml
          prefix, localname = content.split(':')
          uri = self.nsmap.get(prefix)
          content = '{%s}%s' % (uri, localname)
          #Update nsmap of existing node is forbiden,
          #So create a new node and replace it
          new_node = Element(content, nsmap={prefix: uri})
          for child in node:
            new_node.append(deepcopy(child))
          new_node.text = node.text
          new_node.tail = node.tail
          for k, v in node.attrib.items():
            new_node.attrib[k] = v
          parent = node.getparent()
          if parent is not None:
            node.getparent().replace(node, new_node)
          else:
            #if root Element
            self.result_tree._setroot(new_node)
        else:
          node.tag = content
      elif localname == 'processing-instruction':
        #Stay orphans do not remove from stack
        node = self._node_stack[-1]
        node.text = content
      elif localname == 'comment':
        #Stay orphans do not remove from stack
        node = self._node_stack[-1]
        node.text = content
      elif localname == 'variable':
        pass
      elif localname == 'value-of':
        pass
      else:
        raise NotImplementedError(localname)
    else:
      node_stack_position = self._current_position_to_append_stack.pop()
      node_to_append_list = [self._node_stack.pop() for node in self._node_stack[node_stack_position:]]
      #Stay orphans do not remove from stack
      node = self._node_stack[-1]
      node.extend(node_to_append_list)
      if len(node):
        node[-1].tail = content
      else:
        node.text = content

  def endDocument(self):
    [node.getparent().remove(node) for node in self._to_remove_node_list]
