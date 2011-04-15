# -*- coding: utf-8 -*-
"""Minimalist XML library.

FluentXML provides a simple interface to parse, create, query, edit and
save XML with Python.
"""

#  Copyright (c) 2009, 2010, 2011 Anaël Verrier
#
#  Null class is based on pycawm.patterns.Null from PycaWM.
#  Copyright (c) 2007, 2008 Vincent Rasneur, Anaël Verrier
#  distributed under the terms of the GNU General Public License,
#  version 3 only. See http://pycawm.last-exile.org/
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, version 3 only.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from re import compile as re_compile
from xml.parsers.expat import ParserCreate


import sys

# Here are some hacks to allow the use of fluentxml with python 2.x
if sys.version_info < (3,):
    # we need codecs.open to specify the file encoding
    from codecs import open

    # next() does not exist in python 2.x
    def next(iterator):
        return iterator.next()

    # we only want unicode string
    str = unicode

    # when we create a new type, type function does not accept unicode
    old_type = type
    def type(name, bases=None, dict_=None):
        if bases is None and dict_ is None:
            return old_type(bases)

        return old_type(name.__str__(), bases, dict_)

    # pyexpat does not let us access to its Parser class, so we must
    # encapsulate it into your own class in order to fix an encoding bug
    # in its Parse method
    from xml.parsers import expat

    class ParserCreate(object):
        def __init__(self):
            self.__dict__['parser'] = expat.ParserCreate()

        def Parse(self, data, end):
            # encoding handling is brain-dead in pyexpat
            return self.parser.Parse(data.encode('utf-8'), end)

        def __getattr__(self, name):
            if name.startswith('__'):
                return object.__getattribute__(self, name)
            return getattr(self.__dict__['parser'], name)

        def __setattr__(self, name, value):
            setattr(self.__dict__['parser'], name, value)


__all__ = ['Parser', 'Node', 'Null']

_re_pi = re_compile('([^ ]*?)(?: *)=(?: *)"(.*?)"')


def attrs_string_to_dict(attrs):
    return dict(_re_pi.findall(attrs))


def _sanitize_string(string):
    return string.replace(
        '&', '&amp;').replace(
        '"', '&quot;').replace(
        '<', '&lt;').replace(
        '>', '&gt;')


class Null(object):
    """Null objects always and reliably do nothing.

    This class only creates one instance, to allow comparing by identity.

    This class is based on pycawm.patterns.Null from PycaWM.
    Copyright (c) 2007, 2008 Vincent Rasneur, Anaël Verrier.
    Distributed under the terms of the GNU General Public License,
    version 3 only. See http://pycawm.last-exile.org/)

    Slightly modified and extended from the Python Cookbook, 2nd edition.
    """

    def __new__(cls, *args, **kwargs):
        try:
            return cls.__dict__['_inst']
        except KeyError:
            # create only one instance
            inst = object.__new__(cls)
            cls._inst = inst
            return inst

    def __call__(self, *args, **kwargs):
        return self

    def __repr__(self):
        return 'Null()'

    def __bool__(self):
        return False

    def __len__(self):
        return 0

    def __iter__(self):
        return iter(())

    __str__ = __repr__
    __getattr__ = __call__
    __setattr__ = __call__
    __delattr__ = __call__
    __getitem__ = __call__
    __setitem__ = __call__
    __delitem__ = __call__

    #python 2.x
    __unicode__ = __repr__
    __nonzero__ = __bool__



class Node(object):

    # this attribute is a hack presently used by external libraries
    _deep_copy = False
    _node_class = dict()

    def __new__(cls, *args, **kwds):
        name = None
        if len(args):
            name = args[0]
        else:
            name = kwds.get('name')
        if name and ':' in name:
            _namespace_name, _name = name.split(':')
            cls = Node._get_class(_namespace_name)
        return object.__new__(cls)

    def __init__(self, name=None, attributes=None, children=None, parent=None,
                 node=None):
        if node:
            if self._deep_copy:
                Parser(data=str(node), root=self)
            else:
                self.__dict__['_name'] = node._name
                self._parent = None
                self.__dict__['_namespace_name'] = node._namespace_name
                self._attributes = node._attributes.copy()
                self._children = node._children[:]
        else:
            self.__dict__['_name'] = ''
            self.__dict__['_namespace_name'] = ''
            self._attributes = dict()
            self._children = list()
        if attributes:
            if not isinstance(attributes, dict):
                raise TypeError('attributes must be a dict')
            self._attributes.update(attributes)
        if children:
            if not isinstance(children, (list, tuple)):
                raise TypeError('children must be a list')
            for node in children:
                self += node
        if name is not None:
            self.__dict__['_name'] = name
        if parent:
            parent += self
        else:
            self._parent = None

    def _get_children(self, name=None, attributes=None):
        nodes = self.__dict__['_children']
        if name is not None:
            nodes = getattr(self, name)
            if nodes is None:
                return Null()

        if not attributes:
            return nodes

        if not nodes:
            return Null()

        result = list()
        for node in nodes:
            if attributes and isinstance(node, str):
                continue
            for attribute in attributes:
                if (node[attribute] is Null() or
                    (isinstance(attributes, dict) and
                    node[attribute] != attributes[attribute])):
                    break
            else:
                result.append(node)
        if result:
            return result
        return Null()

    def _iter_children(self, name=None, attributes=None):
        nodes = self.__dict__['_children']
        if name is not None:
            nodes = getattr(self, name)
            if nodes is None:
                return

        if attributes is None:
            attributes = list()
        for node in nodes:
            if attributes and isinstance(node, str):
                continue
            for attribute in attributes:
                if (isinstance(attributes, dict) and
                    node[attribute] != attributes[attribute]):
                    break
            else:
                yield node

    def _get_child(self, name=None, attributes=None):
        try:
            return next(self._iter_children(name, attributes))
        except StopIteration:
            return Null()

    def _del_children(self, name=None, attributes=None):
        to_del = list()
        for index, child in enumerate(self.__dict__['_children']):
            if isinstance(child, str):
                continue
            if not name or child._name == name:
                if attributes is None:
                    attributes = list()
                for attribute in attributes:
                    if (attribute not in child._attributes or
                        (isinstance(attributes, dict) and
                         child[attribute] != attributes[attribute])):
                        break
                else:
                    to_del.append(index)
        for index in to_del[::-1]:
            self.__dict__['_children'].pop(index)

    def _del_child(self, name=None, attributes=None):
        for index, child in enumerate(self.__dict__['_children']):
            if isinstance(child, str):
                continue
            if not name or child._name == name:
                if attributes is None:
                    attributes = list()
                for attribute in attributes:
                    if (attribute not in child._attributes or
                        (isinstance(attributes, dict) and
                         child[attribute] != attributes[attribute])):
                        break
                else:
                    self.__dict__['_children'].pop(index)
                    return

    def __getattr__(self, name):
        if name.startswith('_') and name != '_texts':
            if name == '_namespace':
                return self._lookup_namespace(self._namespace_name)
            if name not in self.__dict__:
                raise AttributeError(name)
            return self.__dict__['name']
        result = list()
        for node in self._children:
            if isinstance(node, Node):
                if node._name == name:
                    result.append(node)
            elif name == '_texts':
                result.append(node)
        if result:
            return result
        return Null()

    def __setattr__(self, name, value):
        if name.startswith('_'):
            if name == '_name' and ':' in value:
                _namespace_name, _name = value.split(':')
                object.__setattr__(self, '_namespace_name', _namespace_name)
                object.__setattr__(self, '_name', _name)
                object.__setattr__(self, '__class__',
                                   Node._get_class(_namespace_name))
                return
            if name == '_namespace_name':
                object.__setattr__(self, '__class__', Node._get_class(value))
            object.__setattr__(self, name, value)
            return

    def __delattr__(self, name):
        self._del_children(name)

    def __getitem__(self, name):
        return self.__dict__['_attributes'].get(name, Null())

    def __setitem__(self, name, value):
        self.__dict__['_attributes'][name] = value

    def __delitem__(self, name):
        del self.__dict__['_attributes'][name]

    def __add__(self, others):
        if not isinstance(others, (list, tuple)):
            others = [others]
        for other in others:
            if not isinstance(other, (Node, str)):
                raise TypeError('children must be Node or unicode')
            if other is self:
                other = Node(node=other)
            self._children.append(other)
            if isinstance(other, Node):
                other.__dict__['_parent'] = self
        return self

    def _str(self, pretty=False, level=0):
        attributes = list()
        children = list()

        margin_pre_open = ''
        margin_post_open = ''
        margin_pre_close = ''
        margin_post_close = ''
        if pretty:
            margin_pre_open = margin_pre_close = '  ' * level
            margin_post_open = margin_post_close = '\n'
        name = self._name
        if self._namespace_name:
            name = '%s:%s' % (self._namespace_name, name)

        for key, value in self._attributes.items():
            value = _sanitize_string(str(value))
            attributes.append(' %s="%s"' % (key, value))
        attributes = ''.join(attributes)
        if self._children:
            for child in self._children:
                if isinstance(child, str):
                    child = _sanitize_string(child)
                    margin_post_open = ''
                    margin_pre_close = ''
                else:
                    child = child._str(pretty, level + 1)
                children.append(child)
            children = ''.join(children)
            return '%s<%s%s>%s%s%s</%s>%s' % (
                margin_pre_open, name, attributes, margin_post_open,
                children,
                margin_pre_close, name, margin_post_close)
        return '%s<%s%s/>%s' % (margin_pre_open,
                                 name, attributes,
                                 margin_post_close)

    __str__ = _str

    #python 2.x
    __unicode__ = _str

    def __repr__(self):
        attributes, children = self._attributes, self._children
        parameters = ''
        if attributes:
            if children:
                parameters = ', %s, %s' % (attributes, children)
            else:
                parameters = ', %s' % attributes
        elif children:
            parameters = ', children=%s' % children
        return '%s(%r%s)' % (self.__class__.__name__, self._name, parameters)

    def __eq__(self, other):
        if isinstance(other, Node):
            return (self._children == other._children and
                    self._attributes == other._attributes)
        return NotImplemented

    def __ne__(self, other):
        return not self == other

    # See http://docs.python.org/reference/datamodel#object.__hash__
    __hash__ = object.__hash__

    def __iter__(self):
        return iter(())

    def _lookup_namespace(self, name=''):
        key = 'xmlns'
        if name:
            key = 'xmlns:%s' % name
        try:
            return self._attributes[key]
        except KeyError:
            if self._parent:
                return self._parent._lookup_namespace(name)
            return ''

    @classmethod
    def _get_class(cls, namespace_name):
        if not namespace_name:
            return Node
        if namespace_name not in cls._node_class:

            def node_init(self, name, *args, **kwargs):
                Node.__init__(self, name, *args, **kwargs)
                self.__dict__['_namespace_name'] = namespace_name
                if name and ':' in name:
                    name = name.split(':')[1]
                self.__dict__['_name'] = name

            class_name = '%sNode' % namespace_name.capitalize()
            cls._node_class[namespace_name] = type(str(class_name), (Node,),
                                                   {'__init__': node_init})
        return cls._node_class[namespace_name]


class Parser(object):
    pi_data_to_dict = False

    def __init__(self, data=None, root=None, dispatch_depth=-1,
                 delete_node_after_dispatch=True):
        self._parser = ParserCreate()
        self._parser.StartElementHandler = self.start
        self._parser.EndElementHandler = self.end
        self._parser.CharacterDataHandler = self.data
        if self.pi_data_to_dict:
            self._parser.ProcessingInstructionHandler = self._instruction
        else:
            self._parser.ProcessingInstructionHandler = self.instruction
        self._parser.buffer_text = True
        self.root = root
        self.current = None
        self.depth = 0
        self.dispatch_depth = dispatch_depth
        self.delete_node_after_dispatch = delete_node_after_dispatch
        if data:
            self.feed(data, True)

    def feed(self, data, end=False):
        self._parser.Parse(data, end)

    def close(self):
        self._parser = None

    def start(self, name, attributes):
        self.depth += 1
        if self.depth == 1:
            if not self.root:
                self.current = Node(name, attributes=attributes)
                self.root = self.current
            else:
                Node.__init__(self.root, name, attributes=attributes)
                self.current = self.root
            self.start_stream(self.root)
        else:
            self.current = Node(name, attributes=attributes,
                                parent=self.current)

    def end(self, name):
        self.depth -= 1
        new_current = self.current._parent
        if self.depth == self.dispatch_depth:
            self.dispatch(self.current)
            if self.delete_node_after_dispatch:
                if self.depth > 0:
                    self.current._parent._del_children()
                    self.current._parent = None
                else:
                    self.root = None
        elif not self.depth:
            self.end_stream()
        self.current = new_current

    def data(self, data):
        if (isinstance(self.current, Node) and
            self.current._children and
            not isinstance(self.current._children[-1], Node)):
            self.current._children[-1] += data
        else:
            self.current += data

    def _instruction(self, target, data):
        dict_ = attrs_string_to_dict(data)
        if not dict_:
            dict_ = data
        self.instruction(target, dict_)

    def instruction(self, target, data):
        pass

    def dispatch(self, node):
        pass

    def start_stream(self, node):
        pass

    def end_stream(self):
        pass


class ParserWOIndentationNode(Parser):
    def data(self, data):
        if data.strip():
            Parser.data(self, data)


class Document(object):
    def __init__(self, root=None, instructions=None, filename=None):
        self.root = root
        if instructions is None:
            self.instructions = list()
        else:
            self.instructions = instructions
        self.filename = filename

    @classmethod
    def load(cls, source, parser_class=Parser):
        if hasattr(source, 'read'):
            content = source.read()
            if hasattr(source, 'name'):
                filename = source.name
            else:
                filename = None
        else:
            file_ = open(source, 'r', 'utf-8')
            content = file_.read()
            file_.close()
            filename = source
        instructions = list()

        class MyParser(parser_class):
            def instruction(self, target, data):
                instructions.append((target, data))
                parser_class.instruction(self, target, data)

        parser = MyParser(content)
        return Document(parser.root, instructions, filename)

    def save(self, dest=None, pretty=False):
        if hasattr(dest, 'write'):
            file_ = dest
        else:
            if dest:
                filename = dest
            else:
                filename = self.filename
            file_ = open(filename, 'w', 'utf-8')
        file_.write('<?xml version="1.0"?>\n')
        for target, data in self.instructions:
            if isinstance(data, dict):
                file_.write('<?%s' % target)
                for key, value in data.items():
                    file_.write(' %s="%s"' % (key, value))
                file_.write('?>\n')
            else:
                file_.write('<?%s %s?>\n' % (target, data))
        if self.root:
            file_.write(self.root._str(pretty=pretty))
            if not pretty:
                file_.write('\n')
        if not hasattr(dest, 'write'):
            file_.close()
