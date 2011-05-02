from node import *
import os
from common import warning, error
import sys

###################### TREE WALK GENERATOR #######################

ENTER = 0
LEAVE = 1

def gen_treewalk (node):
    if not node:
        return
    stack = [node]

    while stack:
        yield ENTER, node
        if node.child:
            stack.append (node)
            node = node.child
            continue

        if node.next:
            yield LEAVE, node
            node = node.next
            continue

        while stack and not node.next:
            yield LEAVE, node
            node = stack.pop ()
        if not stack:
            break
        yield LEAVE, node
        node = node.next

##########################################################

from cStringIO import StringIO
import traceback

# Write the opening of a TagNode
def tag_opening (node):
    id = ""
    if node.id:
        id = ' id=\"%s\"' % node.id

    classes = ""
    # If there are classes, compute the class attribute
    if node.classes:
        first = True
        for c in node.classes:
            if not first:
                classes += " %s" % c
            else:
                classes += c
                first = False
        classes = " class=\"%s\"" % (classes)

    attrs = ""
    if node.attrs:
        for k in node.attrs:
            buf = StringIO ()
            output_flat (node.attrs[k], buf)
            attrs += " %s=%s" % (k, buf.getvalue ())
    if node.self_closing and not node.child:
        return "<%s%s%s%s/>" % (node.tag, id, classes, attrs)
    return "<%s%s%s%s>" % (node.tag, id, classes, attrs)

# The XML closing part of a tag.
def tag_closing (node):
    if node.self_closing and not node.child:
        return ""
    return "</%s>" % (node.tag)

###################### REAL OUTPUT ########################

from evaluate import eval_tree

def tree_to_string (root, evaluator):
    return output_flat_to_string (eval_tree (root, evaluator))

def output_flat_to_string (root):
    buf = StringIO ()
    output_flat (root, buf)
    return buf.getvalue ()

def output_indented (root, out=sys.stdout):
    last_newline = True

    for status, node in gen_treewalk (root):
        istag = isinstance (node, TagNode)
        isempty = isinstance (node, EmptyNode)
        iscontent = isinstance (node, ContentNode)

        if status == ENTER:
            if node.indent != -1:
                if not isempty and not last_newline:
                    out.write ('\n')
                if not isempty:
                    out.write (' ' * node.indent)

            if istag:
                out.write (tag_opening (node))
            if iscontent:
                out.write (node.content.encode ('utf-8'))

            if not isempty:
                if node.child and node.child.indent > -1:
                    out.write ('\n')
                    last_newline = True
                else:
                    last_newline = False

        else: # We're leaving the node ! -- its content already processed
            if istag:
                if node.child and node.child.indent > -1:
                    if not last_newline:
                        out.write ('\n')
                    out.write (' ' * node.indent)
                out.write (tag_closing (node))
            #if not iscmd and node.next and node.next.indent != -1:
            #    out.write ('\n')

    out.write ('\n')

def output_flat (root, out=sys.stdout):

    for status, node in gen_treewalk (root):
        istag = isinstance (node, TagNode)
        iscontent = isinstance (node, ContentNode)

        if status == ENTER:
            if istag:
                out.write (tag_opening (node))
            if iscontent:
                out.write (node.content.encode ('utf-8'))

        else: # We're leaving the node ! -- its content already processed
            if istag:
                out.write (tag_closing (node))
            if node.next and node.next.indent != -1:
                out.write (' ')


