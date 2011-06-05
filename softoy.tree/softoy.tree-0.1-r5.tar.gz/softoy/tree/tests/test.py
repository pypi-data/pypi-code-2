# -*- coding: utf-8 -*-
from softoy.tree.tree import Node

def tree_test():
    root = Node('a', as_root=True)
    d = Node('d')
    root.append(d)
    root.append(Node('e'))
    root.append(Node('f'))
    root.append(Node('g'))
    f = root.search('f')

    f.add_sub_names(['fa', 'fb'])

    root.move_up('f')
    root.move_down('d')

    root.prin()


tree_test()


