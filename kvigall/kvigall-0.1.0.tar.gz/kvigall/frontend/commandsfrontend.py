#!/usr/bin/env python
# -*- coding: utf-8 -*-

# kvigall: A customizable calender program meant for use in terminals
# Copyright (C) 2010  Niels Serup

# This file is part of kvigall.
#
# kvigall is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# kvigall is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with kvigall.  If not, see <http://www.gnu.org/licenses/>.

##[ Name        ]## frontend.commandsfrontend
##[ Maintainer  ]## Niels Serup <ns@metanohi.org>
##[ Description ]## Contains the abstract commands frontend
##[ Start date  ]## 2010 August 29

import os.path
import kvigall.frontend.genericfrontend as generic

# Commands recognizable by this frontend
_commands = ('help', 'forward', 'backward', 'next', 'previous',
             'inverse-next', 'inverse-previous', 'update',
             'reshow', 'date', 'today', 'over', 'exit')

def complete_command(text):
    for cmd in _commands:
        if cmd.startswith(text):
            yield cmd

class Frontend(generic.Frontend):
    def init(self):
        self.commands_history_file = os.path.join(self.system.saves_path, 'frontend-commands-history')
        self.help_string = '''\
The following commands can be used:
    help: show this help
    forward [n=1]: show events for n days away of your current date
    backward [n=1]: show events for n days before your current date
    next [n=1]: like forward, but don't count days without events. If
        n is 0, only search for new dates if the current date has no
        events
    previous [n=1]: like next, but backwards
    inverse-next [n=1]: like next, but look for the next date without
        any events
    inverse-previous [n=1]: like inverse-next, but backwards
    date [[YYYY]MM]DD: show events for the given date (YYYY defaults
        to current year, MM defaults to current month)
    today: show events for today
    update: regenerate the cache from source
    reshow: show the events for the current date
    over: start over from the start date
    exit: exit the program\
'''

    def start(self):
        try:
            self.read_commands_history()
        except Exception:
            pass

    def end(self):
        try:
            self.write_commands_history()
        except Exception:
            pass

    def read_commands_history(self):
        pass

    def write_commands_history(self):
        pass

    def show_events(self):
        pass

    def process_command(self, text):
        args = text.split(' ')
        args_len = len(args)
        cmd = args[0]

        def get_num(args, i):
            try:
                return int(args[i])
            except Exception:
                return 1

        if cmd == 'help':
            return self.help_string
        elif cmd == 'forward':
            self.system.go_forward(get_num(args, 1))
            self.show_events()
        elif cmd == 'backward':
            self.system.go_backward(get_num(args, 1))
            self.show_events()
        elif cmd == 'next':
            self.system.goto_next(get_num(args, 1))
            self.show_events()
        elif cmd == 'previous':
            self.system.goto_previous(get_num(args, 1))
            self.show_events()
        elif cmd == 'inverse-next':
            self.system.goto_next_nothing(get_num(args, 1))
            self.show_events()
        elif cmd == 'inverse-previous':
            self.system.goto_previous_nothing(get_num(args, 1))
            self.show_events()
        elif cmd == 'date':
            if args_len < 2:
                return 'missing argument', False
            year, month, day = self.system.split_date_string(args[1])
            try:
                if self.system.goto_date(year, month, day):
                    self.show_events()
            except Exception:
                return 'date syntax is wrong', False
        elif cmd == 'today':
            self.system.goto_today()
            self.show_events()
        elif cmd == 'update':
            self.system.get_events(True)
        elif cmd == 'reshow':
            self.show_events()
        elif cmd == 'over':
            self.system.goto_start()
            self.show_events()
        elif cmd == 'exit':
            return False
        else:
            return 'command not recognized; try "help"', False
