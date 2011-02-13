

class NodeIterator (object):
    ''' An iterator that iterates over a node's level. '''

    def __init__ (self, node, forward=True, real=False):
        self.__node = node
        self.__forward = forward
        self.__real = real

    def next (self):
        res = self.__node
        if not res:
            raise StopIteration
        if self.__forward:
            if self.__real:
                self.__node = self.__node.realnext
            else:
                self.__node = self.__node.next
        else:
            if self.__real:
                self.__node = self.__node.realprev
            else:
                self.__node = self.__node.prev
        return res

    def __iter__ (self):
        return self

class NodeLineIterator (object):
    ''' An iterator that iterates over a 'line' of nodes (see Node#lastInLine documentation) '''

    def __init__ (self, node, forward=True, real=False):
        self.__first = node
        self.__node = node
        self.__forward = forward
        self.__real = real

    def next (self):
        res = self.__node
        if not res or self.__node.indent != -1 and self.__node != self.__first:
            raise StopIteration
        if self.__forward:
            if self.__real:
                self.__node = self.__node.realnext
            else:
                self.__node = self.__node.next
        else:
            if self.__real:
                self.__node = self.__node.realprev
            else:
                self.__node = self.__node.prev
        return res

    def __iter__ (self):
        return self

class NodeDepthIterator (object):
    ''' 
        An iterator that recurses over the whole Node tree in depth-first order.

        It provides two useful methods : remove () and replace () that are to be used
        instead of Node#pop () and Node#replace () since these would most likely disrupt
        the iterator's process.
    '''

    def __init__ (self, node):
        self.__current_node = None
        self.__next_node = node

    def __compute_next (self):
        ''' Compute the next node in the iteration '''
        if not self.__current_node:
            return
        if self.__current_node.child:
            self.__next_node = self.__current_node.child
        elif self.__current_node.next:
            self.__next_node = self.__current_node.next
        else: # We have to backtrack
            tmp = self.__current_node.parent
            while tmp and not tmp.next:
                tmp = tmp.parent
            if tmp:
                self.__next_node = tmp.next
            else:
                self.__next_node = None

    def next (self):
        self.__compute_next ()
        if not self.__next_node:
            raise StopIteration ()
        self.__current_node = self.__next_node
        return self.__current_node

    def remove (self):
        ''' Removes the current node from the tree without affecting the iterator. '''
        if not self.__current_node:
            raise ValueError ('There is no current node')
        prev = self.__current_node.prev
        parent = self.__current_node.parent
        next = self.__current_node.pop ()

        # We first try to come back to previous nodes so that __compute_next ()
        # will go to the next node by itself.
        if prev:
            self.__current_node = prev
        elif parent: # The removed node was the first child on its level.
            self.__current_node = parent
        elif next: # The node was the first one at root level.
            self.__current_node = None
            self.__next_node = next
        else: # The tree is now empty.
            self.__current_node = None
            self.__next_node = None

    def replace (self, new):
        ''' Replace the current node (the last returned by next()) by a new one in the tree.
            The next node in the iteration will be the child (or the next) of the new one. '''
        if not self.__current_node:
            raise ValueError ('There is no current node')
        new.replace (self.__current_node)
        self.__current_node = new

    def __iter__ (self):
        return self

class Node (object):
    '''
        A Node tree is the intermediary data structure resulting from the parsing of a .pwi file.
        It consists of nodes that hold data (such as a html tag, content, or python code) that point to
        either, both or no child and next node.
    '''

    def __init__ (self):
        self.parent = None
        self.__next = None
        self.__prev = None
        self.__child = None

        # Here we cache the last brother to avoid looking it up everytime.
        self.__last = None 
        # Same for first.
        self.__first = None

        self.indent = -1
        self.line = None

    def __invalidateCache (self):
        '''
            When the tree structure changes in a significant way, we have to cancel the cache
            to avoid spurious .last or .first calls.
        '''
        self.__last = None
        self.__first = None

    # Pops an element from the siblings.
    def pop (self):
        '''
            Pops a node and its children out of its tree. This method sets the node's next 
            and prev to None in addition to removing it from the tree (updating its previous, 
            parent and next node if need be).
            Returns the next element (or None if there was no next)
        '''
        _next = self.__next
        _prev = self.__prev

        if _next:
            _next.__prev = _prev
        if _prev:
            _prev.__next = _next

        if self.parent and self.parent.child == self:
            self.parent.child = _next

        self.__next = None
        self.__prev = None
        self.parent = None
        
        self.__invalidateCache ()

        return _next
        
    def fixindent (self, indent, modifier=4):
        '''
            Fixes the indentation of a node to the 'indent' parameter.
            The modifier variable is for indentation incrementation for the children nodes.
            This function should be used whenever the tree structure changes in a significant
            way to ensure that the nodes stay correctly indented.
            Attention : The indentation doesn't affect how the tree is parsed. This is just
            for cosmetics and the pretty (indented) output.
        '''
        for sibling in self:
            if sibling.child:
                if indent == -1:
                    sibling.child.fixindent (indent, modifier)
                else:
                    sibling.child.fixindent (indent + modifier, modifier)
            if sibling.indent != -1: # inline nodes should not be affected.
                sibling.indent = indent

    def replace (self, node):
        '''
            Replaces the 'node' in its tree. The correct syntax is when one wants to replace 
            and 'old' node by a 'new' one : new.replace (old).
            The new node inserts its whole tree structure (children and following brothers 
            -- not previous ones).
        '''
        # prev, next, parent and parent.child are affected.
        if not node:
            return # We can't replace something that doesn't exist

        l = self.last
        l.__next = node.__next
        if node.__next:
            node.__next.__prev = l
        self.__prev = node.__prev
        if node.__prev:
            node.__prev.__next = self

        self.__invalidateCache ()

        self.parent = node.parent
        if node.parent and node.parent.child == node:
            node.parent.child = self

        for n in self:
            n.parent = node.parent

        # Some cleanup. Since the node is not part of the tree, it shouldn't have
        # dangling pointers.
        node.__next = None
        node.__prev = None
        node.__invalidateCache ()

    def appendChild (self, node):
        '''
            Appends a node to the children of this node.
            If there weren't any then the new node becomes the only child.
        '''
        if self.child:
            node.parent = self
            self.child.last.next = node
        else:
            self.child = node

    ###################################### PROPERTIES #######################################

    @property
    def next (self):
        ''' The next node on the same level. '''
        return self.__next

    @next.setter
    def next (self, val):
        self.__invalidateCache ()

        if self.__next:
            self.__next.__prev = None

        if val:
            _val_last = val.last

            for n in val:
                n.parent = self.parent

            val.__prev = self
            _val_last.__next = self.__next

            if self.__next:
                self.__next.__prev = _val_last
        self.__next = val

    @property
    def prev (self):
        ''' The previous node on the same level '''
        return self.__prev

    @prev.setter
    def prev (self, val):
        self.__invalidateCache ()
        if self.__prev:
            self.__prev.next = None
        if val:
            for n in val:
                n.parent = self.parent
            val.__next = self
            val.__prev = self.__prev
            if self.__prev:
                self.__prev.__next = val
            if self.parent and self.parent.child == self:
                self.parent.child = val
        else:
            if self.parent:
                self.parent.child = self
        self.__prev = val

    @property
    def child (self):
        ''' The first child of the node '''
        return self.__child
    @child.setter
    def child (self, val):
        if val:
            for n in val:
                n.parent = self
        self.__child = val

    @property
    def last (self):
        ''' The last brother of the node (its next of next of next...) '''
        if self.__last and not self.__last.next:
            # The last is already cached
            return self.__last
        cur = self.__last
        if not cur: # There was no cache
            cur = self
        while cur.next:
            cur = cur.next
        self.__last = cur
        return cur

    @property
    def lastInLine (self):
        ''' 
            The last brother of the node in the same line.
            A node is on the same line of another if in the source .pwi file
            the source code that led to their creation was on the same line.
            Ex: @p {toto} @p {titi}
            creates two 'p' nodes that are on the same line.
            In practice, a line always starts with a node with its .indent attribute
            >= 0, and subsequent nodes with a -1 indentation.
        '''
        tmp = self
        for n in self.lineIter ():
            tmp = n
        return tmp

    @property
    def first (self):
        '''
            The first node on the same level.
        '''
        if self.__first and not self.__first.prev:
            return self.__first # Cached
        cur = self.__first
        if not cur:
            cur = self
        while cur.prev:
            cur = cur.prev
        self.__first = cur
        return cur

    ############################### ITERATORS #############################

    def __iter__ (self):
        ''' An iterator on the node's sibling (including itself) '''
        return NodeIterator (self)

    def lineIter (self):
        ''' An iterator on the node's sibling that are on the same line (including itself) '''
        return NodeLineIterator (self)

    def forward (self):
        ''' An iterator on the node's sibling (including itself) '''
        return NodeIterator (self)

    def __reversed__ (self):
        ''' An iterator on the node's sibling (including itself) in reverse order. '''
        return NodeIterator (self, False)
    def reverse (self):
        ''' An iterator on the node's sibling (including itself) in reverse order. '''
        return NodeIterator (self, False)

    def treeIter (self):
        ''' An iterator on the node's whole tree in depth-first order (including itself) '''
        return NodeDepthIterator (self)


    ############################### CLONE #################################

    def clone (self):
        ''' Clones the current node and its children (deep copy) '''
        raise NotImplemented () # Has to be rederivated.

    def cloneChildren (self):
        ''' Clone the children of the current node (deep copy) '''
        children = EmptyNode ()
        if self.child:
            for c in self.child:
                children.last.next = c.clone ()
        return children.pop ()


class TagNode (Node):
    ''' A node holding an XML tag '''

    def __init__ (self, tag):
        Node.__init__ (self)
        if tag.startswith ('@'):# Removing the @
            tag = tag[1:]
        tag = tag.strip () 
        self.tag = tag

        self.self_closing = False
        if tag.startswith ('/'):
            self.tag = tag[1:]
            self.self_closing = True

        self.classes = []
        self.id = None
        self.attrs = {}
        self.inline = False

    def __repr__ (self):
        return "%s@%s" % (self.tag, id(self))

    def clone (self):
        ''' Clones the current node '''
        n = TagNode (self.tag)
        n.classes = self.classes
        n.id = self.id
        n.attrs = self.attrs
        n.child = self.cloneChildren ()
        n.indent = self.indent
        return n

class ContentNode (Node):
    ''' A node that holds text '''

    def __init__ (self, content):
        Node.__init__ (self)
        self.content = content
    def __repr__ (self):
        return "'%s'@%s" % (self.content, id(self))

    def clone (self):
        ''' Clones the current node '''
        n = ContentNode (self.content)
        n.child = self.cloneChildren ()
        n.indent = self.indent
        return n

class EmptyNode (Node):
    """ A Node that is empty. """
    def __init__ (self):
        Node.__init__ (self)
    def __repr__ (self):
        return "  --@%s" % (id(self))

    def clone (self):
        ''' Clones the current node '''
        n = EmptyNode ()
        n.child = self.cloneChildren ()
        n.indent = self.indent
        return n

