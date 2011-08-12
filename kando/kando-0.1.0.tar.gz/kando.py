#!/usr/bin/env python3

# kando: a simple todo list manager
# Copyright 2011 Niels Serup

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
kando is a simple todo list manager. It can be used from the command-line, as a
Python 3 module, and with a text editor.

To use kando with Emacs, SAK Mode has been developed. SAK Mode can be
downloaded at <http://metanohi.name/projects/showandkill/>. A special mode is
not needed to edit a kando todo list in a text editor, but it makes it easier.
"""

__url__ = 'http://metanohi.name/projects/kando/'
__version__ = (0, 1, 0)
__author__ = 'Niels Serup <ns@metanohi.name>'

import sys
import pickle
import subprocess
import os
import shutil
import collections

class TodoManager:
    """
    A simple todo manager with support for command-line editing and editor
    editing.
    """
    def __init__(self, file):
        self.file = file
        try:
            with open(self.file, 'rb') as f:
                self.ilist = pickle.load(f)
        except IOError:
            self.ilist = []

    def list(self):
        """List items."""
        indent_len = len(str(len(self.ilist) + 1))
        fmt = '{{:{}d}}. {{}}'.format(indent_len)
        for i in range(len(self.ilist)):
            print(fmt.format(i, '\n'.join(' ' * (indent_len + 2) + x for x in
                                          self.ilist[i].split('\n'))[indent_len + 2:]))

    def add(self, text):
        """Add item."""
        self.ilist.append(text)
        
    def remove(self, *items):
        """
        Remove items. Formats: int, 'int-int' (range), iterable.
        """
        for x in items:
            if isinstance(x, str):
                if not '-' in x:
                    x = int(x)
                else:
                    # is range
                    a, b = map(int, x.split('-'))
                    x = list(range(a, b + 1))
            if isinstance(x, collections.Iterable):
                for i in x:
                    self.ilist[i] = None
            else:
                self.ilist[x] = None
        i = 0
        while True:
            try:
                x = self.ilist[i]
            except IndexError:
                break
            if x is None:
                del self.ilist[i]
            else:
                i += 1

    def edit_in_editor(self, editor=None):
        """
        Edit a simple representation of the list in external editor. If editor
        is None, it defaults to $EDITOR.
        """
        if not editor:
            editor = os.environ['EDITOR']
        nfile = self.file + '.temp.kando'
        with open(nfile, 'w') as f:
            f.write('\n\n'.join(self.ilist))
        mtime = os.stat(nfile).st_mtime
        if subprocess.call([editor, nfile]) != 0:
            sys.exit(1)
        if not os.stat(nfile).st_mtime > mtime:
            sys.exit()
        with open(nfile) as f:
            nlist = f.read().strip()
        if not nlist:
            self.ilist = []
            return
        nlist = nlist.split('\n\n')
        os.remove(nfile)
        i = 0
        while True:
            try:
                n = nlist[i]
            except IndexError:
                self.ilist = self.ilist[:i + 1]
            try:
                o = self.ilist[i]
            except IndexError:
                self.ilist.extend(nlist[i:])
                break
            try:
                while n != o:
                    del self.ilist[i]
                    o = self.ilist[i]
            except IndexError:
                self.ilist.extend(nlist[i:])
                break
            i += 1

    def save(self):
        """Save the list."""
        with open(self.file + '.bak', 'wb') as f:
            pickle.dump(self.ilist, f)
        shutil.copy2(self.file + '.bak', self.file)

def parse_args(args=None):
    """
    Parse command-line arguments and act upon them.
    """
    if args is None:
        args = sys.argv[1:]
    if not args or args[0] in ('h', '-h', '--help'):
        print('''\
Usage: kando FILE COMMAND ARGS...

A simple todo list manager

Special options:
  --version          show program's version info and exit
  -h, --help         show this help message and exit

Commands:
  l                  list all items in the list
  a TEXT...          add a point with TEXT to the todo list
  A [TEXT...]        If TEXT, do as `a', else do as `l'
  e [PROGRAM]        edit the todo list as a text file in PROGRAM or $EDITOR
  r NUMBER|RANGE...  remove items. RANGE = NUMBER-NUMBER

Examples:
  List all items in the .kando file:
    kando .kando l
    kando .kando A

  Add an item:
    kando .kando a Remember to buy one tomato
    kando .kando A Remember to buy one tomato

  Remove the second item (assuming the list has at least two items):
    kando r 1

  Remove items #1 through #4:
    kando r 1-4

  Remove items #2 through #5 (both included) and #7:
    kando r 2-5 7

  Edit in a text editor:
    kando e

  Edit in a specific text editor:
    kando e emacsclient

You can run `pydoc3 kando' to find out more about kando.''')
    elif args[0] in ('--version'):
        print('''
kando 0.1.0
Copyright (C) 2011  Niels Serup
License AGPLv3+: GNU AGPL version 3 or later <http://gnu.org/licenses/agpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.''')
    if len(args) < 2:
        return
    t = TodoManager(args[0])
    if args[1] == 'l' or (len(args) == 2 and args[1] == 'A'):
        t.list()
    elif args[1] == 'e':
        t.edit_in_editor()
        t.save()
        return
    if len(args) < 3:
        return
    if args[1] in ('a', 'A'):
        t.add(' '.join(args[2:]))
    elif args[1] == 'e':
        t.edit_in_editor(args[2])
    elif args[1] == 'r':
        t.remove(*args[2:])
    t.save()
    
if __name__ == '__main__':
    parse_args()
