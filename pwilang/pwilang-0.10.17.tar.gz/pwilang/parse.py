#!/usr/bin/env python

from lineparser import parser, set_current_pwiline
from node import *

def parselines (lines):
    '''
        Parse a whole line set (eg. a file)
        On each line, invoke the line parser to get the resulting tree.
        All these trees are then assembled to make the tree of the whole file.

        @param lines : An array of PwiLine
        @return      : The root node of the resulting tree.
    '''
    root = EmptyNode () # This node is meant to be discarded.
    stack = [root]

    # This is to avoid nasty errors when somebody deems intelligent
    # to add spaces on the first element.
    if lines and lines[0].indent != 0:
        lines[0].indent = 0

    for line in lines:
        # We first get the root node of the current line.
        set_current_pwiline (line)
        if line.content:
            node = parser.parse (line.content)
        else:
            node = ContentNode (" " * line.indent)
        if not node:
            node = EmptyNode ()
        node.indent = line.indent

        # We unstack our tree since the indentation decreased.
        while line.indent < stack[0].indent:
            stack.pop (0)

        if line.indent > stack[0].indent: # We are increasing the level.
            if stack[0].last.child:
                stack[0].last.child.last.next = node
            else:
                stack[0].last.child = node
            stack.insert (0, node)
        elif line.indent == stack[0].indent:
            stack[0].last.next = node

    res = root.child
    if res: # Resulting tree might be None
        res.parent = None
    return res

def parsestr (line):
    '''
        Parse a line or an array of lines
        @param line : A string or an array of string.
             if line if a string, it will be split by \n.
        @return     : The root node of the resulting tree
    '''
    rawlines = line
    if isinstance (line, str) or isinstance (line, unicode):
        rawlines = line.split ('\n')
    lines = []
    for l in rawlines:
        if l.strip () != "":
            lines.append (PwiLine (l, -1, "<str>"))
    return parselines (lines)

