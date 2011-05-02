#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from BeautifulSoup import BeautifulSoup, NavigableString

import sys

INDENT = "    "

import re
import string
re_not_empty = re.compile ('[^\s]')
re_spaces = re.compile ('\s+', re.MULTILINE)

def print_string_at_indent (s, indent, origindent=""):
    s = s.replace ('[', '\[').replace ('@', '\@').replace (']', '\]')
    lines = s.rstrip (' \n\t').lstrip (' \n\t').split ('\n')
    lines = [lines[0]] + ['\n%s%s' %(indent, l) for l in lines[1:]] + ['\n']
    res = string.join (lines)
    sys.stdout.write (origindent + res)
    
def parse_attrs (node):
    if not node.attrs:
        return ""

    s = ['']
    for key, value in node.attrs:
        if key == "id":
            s.append ('#%s' % value)
        elif key == "class":
            for c in re_spaces.split (value):
                s.append ('.%s' % c)
        else:
            s.append ('%s="%s"' % (key, value))
    return string.join (s, ' ')

def treat_node (node, indent=""):
    # if node.string -- single content node.

    if not isinstance (node, NavigableString):
        sys.stdout.write ('%s@%s' % (indent, node.name))
        sys.stdout.write (parse_attrs (node))
        if node.string:
            sys.stdout.write (' ')
            print_string_at_indent (' %s' % (str (node.string)), indent + INDENT)
        else:
            sys.stdout.write ('\n')
            for n in node.contents:
                treat_node (n, indent + INDENT)
    else:
        if re_not_empty.search (str (node)):
            print_string_at_indent (str (node), indent, indent)

def treat_file (fname):
    f = open (fname, 'r')
    contents = f.read ()
    contents = contents.decode ('utf-8')
    f.close ()

    soup = BeautifulSoup (contents)
    for n in soup.contents:
        treat_node (n, "")

for fname in sys.argv[1:]:
    treat_file (fname)
