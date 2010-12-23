#!/usr/bin/env python
# -*- coding: utf-8 -*-

# forbi: a TCP-based communication tool
# Copyright (C) 2010  Niels Serup

# This file is part of forbi.
#
# forbi is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# forbi is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General
# Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with forbi. If not, see
# <http://www.gnu.org/licenses/>.

##[ Maintainer  ]## Niels Serup <ns@metanohi.org>
##[ Description ]## What to do when a message is received

import Tkinter as tk
import tkFont
import forbi.misc as misc

# Global variables
program = None
windows = None
new_message = None


# Internal way of showing new messages
class MessageWindows(object):
    """A hidden root window with dynamically addable visible subwindows"""
    def __init__(self):
        self.queue = []
        self.created = False

    def start(self):
        """In a new thread, create the root window and run the event loop"""
        misc.QuickThread(self.create)
        while not self.created:
            pass

    def create(self):
        """Create an empty root window"""
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.bind('<<show_message>>', self.show_message)
        self.created = True
        tk.mainloop()

    def new_message(self, username, msg):
        """Add a new window"""
        self.queue.append((username, msg))
        self.root.event_generate('<<show_message>>', when='tail')

    def show_message(self, *args):
        """Format and show the new message"""
        username, msg = self.queue.pop(0)

        top = tk.Toplevel()
        top.geometry('320x240')
        top.maxsize(320, 240)
        top.title('Message received')

        top.bind(sequence='<Control-q>', func=lambda *args: top.destroy())

        scrollbar = tk.Scrollbar(top)
        text = tk.Text(top)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(side=tk.LEFT, fill=tk.Y)
        scrollbar.config(command=text.yview)
        text.config(yscrollcommand=scrollbar.set)

        user_font = tkFont.Font(size=14, weight='bold')
        text.tag_config('u', background='black', foreground='white', font=user_font)

        text.insert(tk.END, username + '\n', ('u',))
        text.insert(tk.END, msg)

def _new_msg_gui(user_from, user_to, msg):
    global windows
    windows.new_message(user_from, msg)


# External way of showing new messages
def _new_msg_program(user_from, user_to, msg):
    global program
    misc.exec_program(program, user_from, user_to, msg)

def init(prog=None):
    """Prepare this module for new messages"""
    global new_message
    if prog is None:
        # Prepare the GUI
        global windows, _new_msg_gui
        windows = MessageWindows()
        windows.start()
        new_message = _new_msg_gui
    else:
        # Prepare to call an external program
        global program, _new_msg_program
        program = prog
        new_message = _new_msg_program

if __name__ == '__main__':
    # For testing it
    win = MessageWindows()
    win.start()
    win.new_message(u'Test user', u'\n'.join((u'Hello!' for i in xrange(25))))
    win.new_message(u'Test user2', u'\n'.join((u'!olleH' for i in xrange(52))))
    while True: pass
