# -*- coding: utf-8 -*-
IndentSize= 4
DefaultSpan = True

class NodeIndex(object):
    def __init__(self, auto=True):
        self.subs = {}
        self.sn = 0

    def update(self, elem):
        self.subs.update(elem)

    def delete(self, key):
        del self.subs[key]

    def get(self, key):
        return self.subs[key]

    def gen_name(self):
        self.sn += 1
        return '_sn_name_%s' % self.sn


class Node(object):
    def __init__(self, name, span=DefaultSpan, data=None, as_root=False):
        self.name = name
        self.span = span
        self.data = data

        self.sup = None
        self.subs = []
        if as_root:
            self.sup = None
            self.indexer = NodeIndex()
            self.name = '_root_'
        else:
            self.indexer = None

    def __str__(self):
        if self.sup:
            sup_name = self.sup.name
        else:
            sup_name = ''
        subs_len = len(self.subs)
        return 'name:%s sup_name:%s span:%s subs_len:%s' % (
            self.name,  sup_name,  self.span,  subs_len)

    def root(self):
        cand = self
        while self.sup is not None:
            cand = self.sup
        return cand

    def is_root(self):
        return self.sup is None

    def is_leaf(self):
        return len(self.subs) == 0

    def my_index(self):
        if self.sup:
            return self.sup.subs.index(self)

    def apart(self):
        idx = self.my_index()
        if idx:
            return self.sup.subs.pop(idx)

    def auto_name(self):
        return self.indexer.gen_name()

    def insert(self, index, node):
        if node:
            #root = self.search('_root_')
            node.indexer = self.indexer
            self.subs.insert(index, node)
            node.sup = self
            node.do_index(1)

    def insert_before(self, e):
        if not self.is_root():
            self.insert(self.my_index(), e)

    def append(self, node):
        if node:
            #root = self.search('_root_')
            node.indexer = self.indexer
            self.subs.append(node)
            node.sup = self
            node.do_index(1)

    def add_sub_names(self, names): # ids is list of new ids
        for name in names:
            node = Node(name=name)
            node.indexer = self.indexer
            self.append(node)

    def add_subnodes(self, subs):
        for node in subs:
            self.append(node)

    def prin(self, tabs=0, name_only=True):
        spaces = u''
        for i in range(tabs):
            spaces += u' '

        if name_only:
            print '%s%s' % (spaces, self.name)
        else:
            print '%s%s' % (spaces, self)

        if self.span:
            for n in self.subs:
                n.prin(tabs=tabs + IndentSize, name_only=name_only)

    def do_index(self, sign):
        if not self.indexer:   # TEST
            return

        if sign >= 0:
            self.indexer.update({self.name: self})
        else:
            self.indexer.delete(self.name)

        for n in self.subs:
            n.do_index(sign)

    # TODO: 'str' object has no  attribute 'sup'
    def search(self, name):  # do not search the root
        #print '@@ search started'
        root = self
        cnt = 0
        while self.sup != None and cnt <= 1000:
            root = root.sup
            cnt += 1
        if cnt > 1000:
            raise ValueError('root not found')
        return root.indexer.get(name)

    def extract(self, name): # to cut a subtree
        n = self.search(name)
        n.do_index(-1)
        index = n.sup.subs.index(n)
        return (index, n.sup.subs.pop(index))

    def get_index_for_name(self, name):
        node = self.search(name)
        return node.sup.subs.index(node)

    def number_of_siblings(self, name):
        node = self.search(name)
        return len(node.sup.subs)

    def move_up(self, name): # among siblings
        idx = self.get_index_for_name(name)
        if idx == 0:
            return
        t = self.extract(name)
        index = t[0]
        node = t[1]
        node.sup.insert(index - 1, node)

    def move_down(self, name):   # among siblings
        idx = self.get_index_for_name(name)
        if idx == self.number_of_siblings(name) -1:
            return
        t = self.extract(name)
        index = t[0]
        node = t[1]
        node.sup.insert(index + 1, node)

