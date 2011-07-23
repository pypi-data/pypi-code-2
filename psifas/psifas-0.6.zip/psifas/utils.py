# Copyright 2010 Oren Zomer <oren.zomer@gmail.com>
#
# This file is part of pypsifas.

# pypsifas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# pypsifas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with pypsifas.  If not, see <http://www.gnu.org/licenses/>.

from datatypes.abstract import *
from datatypes.sparse import *
from datatypes.pretty import Pretty
from datatypes.deque import deque
from copy import deepcopy
from itertools import izip, izip_longest, imap, tee, islice, starmap
import operator
from collections import defaultdict
import thread
from functools import wraps
from os import SEEK_CUR
from weakref import WeakValueDictionary
try:
    from io import BytesIO
except ImportError:
    from cStringIO import StringIO as BytesIO
from recursion_lock import recursion_lock
    

if not hasattr(__builtins__, 'next'):
    def next(iterator, *args):
        # args should have 0 or 1 arguments
        try:
            iterator.next(*args[1:])
        except StopIteration:
            if len(args) == 0:
                raise
            return args[0]

from psifas_exceptions import *

from imerge import imerge

def pairwise(iterable):
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)

def pairwise_longest(iterable):
    a, b = tee(iterable)
    next(b, None)
    return izip_longest(a, b)
    
    
class Finished(Singleton):
    def __iadd__(self, other):
        return self

class Path(object):
    __slots__ = ['_elements', '__weakref__']

    # This deque exists inorder to keep the last 10**4 paths "alive", even
    # if noone holds their instance. This makes their recreation faster.
    _last_paths = deque(maxlen = 10**4)

    _from_string = WeakValueDictionary()
    _from_elements = WeakValueDictionary()

    _special_elements = frozenset(('', '.', '..', '...'))

    @property
    def elements(self):
        return self._elements

    @classmethod
    def _from_simplified_elements(cls, elements):
        """
        This constructor simply creates a new instance, without
        updating the maps (_from_string, _from_elements).

        Assumes elements is a tuple.
        """
        instance = super(Path, cls).__new__(cls)
        instance._elements = elements
        cls._last_paths.append(instance)
        return instance

    @classmethod
    def _simplify(cls, elements):
        parent_level = 0
        simplified_elements = []
        for element in reversed(elements):
            if element in cls._special_elements:
                if element == '..':
                    parent_level += 1
                elif element == '...':
                    simplified_elements += ['..'] * parent_level
                    simplified_elements.append('...')
                    parent_level = 0
            elif parent_level > 0:
                parent_level -= 1
            else:
                simplified_elements.append(element)
        simplified_elements += ['..'] * parent_level
        simplified_elements.reverse()
        return simplified_elements

    @classmethod
    def from_elements(cls, elements):
        """
        This constructor tries to retrieve the path from the _from_elements
        mapping. On failure, updates the mapping with the new instance.
        """
        elements = tuple(elements)
        instance = cls._from_elements.get(elements, None)
        if instance is None:
            simplified_elements = tuple(cls._simplify(elements))
            instance = cls._from_elements.get(simplified_elements, None)
            if instance is None:
                cls._from_elements[simplified_elements] = instance = cls._from_simplified_elements(simplified_elements)
            cls._from_elements[elements] = instance
        return instance

    def __new__(cls, path_string=''):
        """
        This constructor tries to retrieve the path from the _from_string
        mapping. On failure, updates the mapping with the new instance.
        """
        instance = cls._from_string.get(path_string, None)
        if instance is None:
            cls._from_string[path_string] = instance = cls.from_elements(path_string.split('/'))
        return instance

    def __deepcopy__(self, memo):
        return self

    def join(self, other):
        """
        This constructor acts like from_elements.
        However, because we know that self._elements and other._elements are already simplified
        we can simplifiy their concatenation in a faster way.
        """
        elements = self._elements + other._elements
        instance = self._from_elements.get(elements, None)
        if instance is None:
            # a faster way to simplify the sum
            index = 0
            for index, (parent, other_element) in enumerate(izip(reversed(self._elements), other._elements)):
                if (other_element != '..') or (parent in ('..', '...')):
                    break
            if index > 0:
                simplified_elements = self._elements[:-index] + other._elements[index:]
                instance = self._from_elements.get(simplified_elements, None)
                if instance is None:
                    self._from_elements[simplified_elements] = instance = self._from_simplified_elements(simplified_elements)
            else:
                # already simplified
                instance = self._from_simplified_elements(elements)
        self._from_elements[elements] = instance
        return instance

    def to_string(self):
        return ('/'.join(self._elements)) or '.'

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.to_string())

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, Path):
            return super(Path, self) == other
        return self._elements == other._elements
    
    def __hash__(self):
        return hash(self._elements)

class Link(Path):
    _from_string = WeakValueDictionary()
    _from_elements = WeakValueDictionary()
    
    def is_broken(self, context):
        try:
            if context.sub_context(self).value is not Bottom:
                return False
        except DereferenceException:
            pass
        return True

class Context(object):
    __slots__ = ['value', 'value_locations', 'spiritual', 'files', 'parent_stack', 'is_link']

    max_visited_links = 100

    @classmethod
    def _increase_max_visited_links(cls):
        cls.max_visited_links *= 2

    def __init__(self, parent = None):
        super(Context, self).__init__()

        self.value = Bottom
        self.value_locations = []
        if parent is not None:
            self.parent_stack = (parent,) + parent.parent_stack
        else:
            self.parent_stack = ()
        self.spiritual = False
        self.files = {'.': self}
        self.is_link = False

    @classmethod
    def from_value(cls, value):
        context = cls()
        context.value = value
        return context

    def get_file(self, name):
        result = self.files.get(name, None)
        if result is None:
            self.files[name] = result = Context(self)
        return result

    def iterkeys(self):
        return self.sub_context(Path('.')).files.iterkeys()

    def set_value(self, value, value_location):
        if (value is Bottom) or (value is AcceptAll):
            return

        if value_location not in self.value_locations:
            value_location.proceed()
            self.value_locations.append(value_location)
            
        try:
            self.value = value_location.imerge(self.value, value)
            if isinstance(self.value, Link):
                self.is_link = True
                # for debugging, we don't allow links to contain files at all.
                del self.files
        except MergeException:
            raise Contradiction("new value %r found from %s contradicts old value %r found from: %s" %
                                (value,
                                 value_location,
                                 self.value,
                                 ', '.join(str(vl) for vl in self.value_locations if vl is not value_location)))

    def _deref(self, visited_links):
        # assert self.is_link
        if len(visited_links) > self.max_visited_links:
            if self in visited_links:
                raise InfiniteRecursionException("Links point to each other and create infinite dereference loop", self)
            else:
                # the max_visited_links estimation was too low
                self._increase_max_visited_links()
        visited_links.append(self)
        return self.parent_stack[0]._sub_context(self.value, visited_links)

    # the following function do not receive "self" in purpose.

    def _normal_parent(parent_stack, target, element, visited_links):
        return parent_stack.popleft()

    def _spiritual_parent(parent_stack, target, element, visited_links):
        while not target.spiritual:
            target = parent_stack.popleft()
        return target

    @staticmethod
    def _normal_element(parent_stack, target, element, visited_links):
        parent_stack.appendleft(target)

        target = target.get_file(element)
        if target.is_link:
            return target._deref(visited_links)
        return target

    _sub_context_func = {'..': _normal_parent,
                         '...': _spiritual_parent}

    def sub_context(self, full_path):
        try:
            return self._sub_context(full_path, [])
        except IndexError, e:
            raise DereferenceException("cannot deref to: %s" % (full_path,), e)

    def _sub_context(self, full_path, visited_links):
        if self.is_link:
            target = self._deref(visited_links)
        else:
            target = self

        parent_stack = deque(self.parent_stack)

        for element in full_path.elements:
            target = self._sub_context_func.get(element, self._normal_element)(parent_stack,
                                                                               target,
                                                                               element,
                                                                               visited_links)
        return target

    @recursion_lock(lambda indent, indent_string, recursive: "(RECURSION IN TREE!)", exclude = (0, 'indent', 1, 'indent_string'))
    def ls_iter(self, indent = 0, indent_string = '   ', recursive = False):
        """
        Aid function to iterate over the textual format of the child-contexts.
        """
        if not hasattr(self, 'files'):
            yield '<link does not have files>'
            return
        for name, sub_context in sorted(self.files.iteritems()):
            if name == '.':
                continue
            spiritual = '*' if sub_context.spiritual else ''
            if isinstance(sub_context.value, Link):
                yield '%s%s%s -> %s%s' % ((indent_string * indent), name, spiritual,
                                          sub_context.value.to_string(), ' ???' if sub_context.value.is_broken(self) else '')
            else:
                yield '%s%s%s: %r' % ((indent_string * indent), name, spiritual, sub_context.value)
                if recursive:
                    for line in sub_context.ls_iter(indent + 1, indent_string, recursive):
                        yield line

    def ls(self, indent_string = '   ', recursive = False):
        """
        Aid function to return a tuple of the textual format of the child-contexts.
        If you want a recurisve ls without indentations, use indent_string = ''.
        """
        return tuple(self.ls_iter(indent_string = indent_string, recursive = recursive))

    def tree(self):
        """
        Joins a recursive ls to a string
        """
        return '\n'.join(self.ls_iter(recursive = True))

    def name(self):
        """
        Gets the name of the context from its parent context.
        This is a heavy operation.
        """
        if len(self.parent_stack) == 0:
            return ''
        for name, value in getattr(self.parent_stack[0], 'files', {}).iteritems():
            if value is self:
                return name
        return "<not found in parent's files>"

    @recursion_lock(lambda self: '%s(...)' % (self.__class__.__name__,))
    def __repr__(self):
        return '%s(%r%s)' % (self.__class__.__name__, self.value,
                             ''.join(map(', %s = %r'.__mod__,
                                         sorted((name, value) for (name, value) in
                                                getattr(self, 'files', {}).iteritems()
                                                if name != '.'))))

    @recursion_lock(lambda self: '%s(...)' % (self.__class__.__name__,))
    def __str__(self):
        try:
            return '%s(%s/%s)' % (self.__class__.__name__,
                                  '/'.join(parent.name() for parent in reversed(self.parent_stack)),
                                  self.name())
        except AttributeError:
            # If someone illegally played with the parent_stack, we still want to
            # be able to do str()
            return super(Context, self).__str__()

class _Location(list):
    """
    In this partial class _context is not set.
    When TopLocation is initialized, it creates a new Context.
    When Location is initialized, it creates a sub-context from its parent.
    """
    __slots__ = ['parent', 'index', 'full_name', '_context',
                 'process', 'payload', 'payload_offset', 'try_copy',
                 'location_deciphered', 'payload_deciphered']

    def __init__(self, index, full_name, parent):
        super(_Location, self).__init__()

        # assert '/' not in full_name
        # assert full_name not in ('', '..')

        self.parent = parent
        self.index = index
        self.full_name = full_name

        self.process = 0
        self.payload = SparseString()
        self.payload_offset = MaybeNumberType
        
        self.location_deciphered = False

        # a place for the Try class to save the tree-copy
        self.try_copy = None

    def parent_payload(self):
        raise NotImplementedError

    def reload_location(self, location):
        self._context = location._context
        self.process = location.process
        self.process += (-1)
        self.payload = location.payload
        self.payload_offset = location.payload_offset
        
        self.location_deciphered = location.location_deciphered
        self.payload_deciphered = location.payload_deciphered

        self.try_copy = location.try_copy

        del self[len(location):]

        for self_child, child in izip(self, location):
            self_child.reload_location(child)

    def create_sublocations(self, creator, fields):
        """
        If the sub-locations does not exist - automatically creates them.
        """
        current_len = len(self)
        if current_len < len(fields):
            # adds the new fields
            self.extend(Location(current_len + index, field.full_name(creator, self), self) for index, field
                        in enumerate(fields[current_len:]))
            self.proceed()

    def get_field(self, index, full_name = '.'):
        """
        If the number of sub-locations is smaller then 'index',
        creates new ones with the given name (Usually only one).
        """
        current_len = len(self)
        if current_len > index:
            return self[index]
        self.extend(Location(new_index, full_name, self) for new_index in xrange(current_len, index + 1))
        self.proceed()
        return self[-1]

    def iter_names(self):
        """
        iterator on the sub_locations' names
        """
        return (sub_location.full_name for sub_location in self)

    def names(self):
        """
        returns a list of the sub-locations' names
        """
        return list(self.iter_names())

    @recursion_lock(lambda self: '%s(%r, ...)' % (self.__class__.__name__, self.full_name))
    def __repr__(self):
        return '%s(%r%s)' % (self.__class__.__name__, self.full_name,
                             (', process = %s' % (self.process,) if self.process is not Finished else ''))

    def __str__(self):
        return '%s(/%s)' % (self.__class__.__name__,
                            '/'.join('%s:%s' % (parent.index, parent.full_name)
                                     for parent in self.parent_stack()[1:]))

    def find_iter(self, full_name):
        """
        finds the sub-locations with the given name
        """
        for sub_location in self:
            if sub_location.full_name == full_name:
                yield sub_location

    def find(self, full_name):
        return list(self.find_iter(full_name))

    def imerge(self, a, b):
        result, change_flag = imerge(a, b)
        if change_flag:
            self.proceed()
        return result

    def set_payload(self, payload):
        try:
            self.payload = self.imerge(self.payload, payload)
        except MergeException:
            raise Contradiction("in %s: new payload %r contradicts old payload %r" %
                                (self,
                                 payload,
                                 self.payload))

    def set_payload_offset(self, payload_offset):
        try:
            self.payload_offset = self.imerge(self.payload_offset, payload_offset)
        except MergeException:
            raise Contradiction("in %s: new payload offset %r contradicts old payload offset %r" %
                                (self,
                                 payload_offset,
                                 self.payload_offset))
        
    def proceed(self):
        self.process += 1

    def context(self, rel_path_str = None):
        if rel_path_str is None:
            return self._context
        return self._context.sub_context(Path(rel_path_str))

    def set_context_value(self, value, rel_path_str = None):
        return self.context(rel_path_str).set_value(value, self)

    def parent_stack(self):
        stack = [self]
        current = self.parent
        while current is not None:
            stack.append(current)
            current = current.parent
        stack.reverse()
        return stack
                                 
    def top_parent(self):
        current = self
        while current.parent is not None:
            current = current.parent
        return current


class Location(_Location):
    def __init__(self, index, full_name, parent):
        super(Location, self).__init__(index, full_name, parent)
        self._context = parent._context.get_file(full_name.split('$', 1)[0])
        self.payload_deciphered = False

    def parent_payload(self):
        return self.parent.payload

class TopLocation(_Location):
    __slots__ = _Location.__slots__ + ['ghosts']

    def __init__(self, payload = None, full_name = '.'):
        super(TopLocation, self).__init__(0, full_name, None)
        self._context = Context()
        self.ghosts = []
        if payload is not None:
            self.set_payload(payload)
        self.set_payload_offset(None)
        self.payload_deciphered = True

    def create_ghost(self):
        current_ghosts = self.ghosts
        try:
            del self.ghosts
            current_ghosts.append(deepcopy(self))
            return len(current_ghosts) - 1
        finally:
            self.ghosts = current_ghosts

    def load_ghost(self, index):
        pre_process = self.process
        self.reload_location(self.ghosts[index])
        self.process = pre_process

    def parent_stream(self):
        return None


