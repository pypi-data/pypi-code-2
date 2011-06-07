from node import *
import os
from parse import parsestr
# from pwifile import pathpush, pathpop
from common import warning, error
import sys

def _eval_tree (node):
    if not node:
        return

    to_pop = False

    if isinstance (node, TagNode):
        for k in node.attrs.keys ():
            root = EmptyNode ()
            root.child = node.attrs[k]
            _eval_tree (root)
            node.attrs[k] = root.child
            node.attrs[k].parent = None

    _eval_tree (node.child)
    _eval_tree (node.next)

    # We're Merging the Content Nodes.
    # This is important since some macros rely on that.
    if isinstance (node, ContentNode) and isinstance (node.next, ContentNode) and node.next.indent == -1:
        mergedNode = ContentNode (node.content + node.next.content)
        node.next.pop ()
        indent = node.indent
        mergedNode.replace (node)
        mergedNode.indent = indent

    if to_pop:
        node.pop ()


def eval_tree (root=None, exec_defered=True):
    '''
        Create a new tree from the parsed one, executing the command nodes.
        Also, execute the deferred functions.
        The resulting Tree will only be composed of EmptyNode, ContentNode and TagNodes
        and is meant to be processed by the output module's functions.
    '''
    make_root = False
    if not root.parent:
        make_root = True
        fake_root = EmptyNode ()
        fake_root.child = root
    else:
        fake_root = root # not very pretty.

    _eval_tree (fake_root)

    if make_root:
        root = fake_root.child
        root.parent = None
    return root

def eval_string (string=None):
    '''
        Parse a string then evaluate it.
    '''
    return eval_tree (parsestr (string))

