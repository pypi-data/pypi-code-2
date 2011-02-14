#!/usr/bin/env python

import re
import sys

from os import path

default_dirs = [path.expanduser("~/.pwilang/templates")]

from common import error, warning, deps_add

re_comment = re.compile ("^\s*#.*$")

############### PwiLines #########

re_indent = re.compile (r'(\s*)(.*)', re.DOTALL)
prev_indent = 0

class PwiLine (object):
    '''
        This class represents a single line in the pwilang world.
        It possesses the following information :
        The line number in the original file, the original file, the indentation of the line, and of course its contents.
    '''

    def __init__ (self, content, linenb, fname):
        global prev_indent

        self.linenb = linenb
        self.fname = fname

        if not content: # empty line
            self.indent = prev_indent
            self.content = ""
        else:
            m = re_indent.match (content)
            self.indent = len (m.group(1))
            self.content = m.group(2)
            prev_indent = self.indent

    def __repr__ (self):
        return '%d:%s' % (self.linenb, self.content)

############# MACROS ####################

def warning (text):
    sys.stderr.write ("%s\n" % text)

def real_lines (lines_arr):
    '''
        Sorts out comments, empty lines and multi lines. 
        Acts as a generator.
    '''
    raw_block = False
    nb = 0

    in_multiline = False
    acc = ""

    for line in lines_arr:
        nb += 1
        line = line.rstrip ()

        if line.endswith ('\\'):
            acc += '%s\n' % (line[:-1]) # Removing the \
            continue
        #if line == '': # discarding empty lines
        #    continue
        if line.startswith ('#'): # comment
            continue
        if acc:
            acc += line
            yield acc, nb
            acc = ""
            continue
        yield line, nb
    if acc:
        yield acc, nb

def real_lines_getter (iterative, fname="<str>"):
    lines = []
    for l, nb in real_lines (iterative):
        lines.append (PwiLine (l, nb, fname))
    return lines

def get_lines_from_iterable (iterable, file_like=True):
    return real_lines_getter (iterable)

def get_lines_from_file (fname):
    ''' Get the complete lines from a file (with blocks resolved and includes executed) '''
    f = open (fname, 'r')
    lines = get_lines_from_iterable (f, fname)
    f.close ()
    return lines

def get_lines_from_string (str):
    lines = real_lines_getter (str.split ('\n'))
    return lines

