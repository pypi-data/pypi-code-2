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

##[ Name        ]## frontend.textfrontend
##[ Maintainer  ]## Niels Serup <ns@metanohi.org>
##[ Description ]## Contains the plain text frontend
##[ Start date  ]## 2010 August 25

import sys
import os.path
import random
import kvigall.various as various
import kvigall.frontend.commandsfrontend as commands
try:
    from termcolor import colored
except ImportError:
    from kvigall.external.termcolor import colored

try:
    import readline
    def _complete(text, state):
        for cmd in commands.complete_command(text):
            if not state:
                return cmd
            else:
                state -= 1

    readline.parse_and_bind("tab: complete")
    readline.set_completer(_complete)
except ImportError:
    pass

class Frontend(commands.Frontend):
    base_h1 = lambda self, message: message + '\n' + len(message) * '='
    base_h2 = lambda self, message: message + '\n' + len(message) * '-'

    def init(self, *settings):
        commands.Frontend.init(self)

        if self.system.use_styling:
            self.h1 = lambda message: \
                colored(self.base_h1(message), 'white', 'on_grey', attrs=['bold'])
            self.h2 = lambda message: \
                colored(self.base_h2(message), attrs=['bold'])
            self.style_time = lambda message: colored(message, 'white', 'on_yellow', attrs=['bold'])
            self.style_author = lambda message: colored(message, 'white', 'on_cyan', attrs=['bold'])
            self.style_info = lambda message: colored(message, 'white', 'on_green', attrs=['bold'])
            self.style_from = colored('from', attrs=['bold'])
        else:
            self.h1 = self.base_h1
            self.h2 = self.base_h2
            same = lambda message: message
            self.style_time = same
            self.style_author = same
            self.style_info = same
            self.style_from = 'from'

    def start(self):
        commands.Frontend.start(self)
        # Show events unless told not to
        if not self.system.start_empty:
            self.show_events()
        self.await_command()

    def read_commands_history(self):
        readline.read_history_file(self.commands_history_file)

    def write_commands_history(self):
        readline.write_history_file(self.commands_history_file)

    def show_events(self):
        # Format events nicely
        print
        print self.h1(self.system.get_current_date_string())
        print

        events = self.system.get_events()
        if events is None:
            msg = 'No events available.'
            if self.system.use_cache_only:
                msg += ' This is likely because you chose to only use the cache.'
            print msg
        elif not events:
            print 'No events on this day.'
        else:
            for event in events:
                if event.type:
                    if event.subject:
                        print self.h2('%s: %s' % (event.type,
                                                  event.subject))
                    else:
                        print self.h2('%s' % event.type)
                else:
                    print self.h2('%s' % event.subject)

                inr = event.interval
                if inr:
                    print self.style_time('Time:  ') + ' %02d:%02d--%02d:%02d' % (
                        inr[0][0], inr[0][1], inr[1][0], inr[1][1])
                if event.author or event.projects:
                    author_str = self.style_author('Author:') + ' %s' % event.author
                    if event.projects:
                        author_str += ' %s %s' % (self.style_from, ', '.join(event.projects))
                    print author_str
                print self.style_info('Info:  ') + self.system.fill_text(' ' + (event.text or 'None'))[7:]
                print
            print

    def await_command(self):
        # Wait for commands
        while True:
            text = raw_input('>> ')
            result = self.process_command(text)
            if result is False:
                break
            elif isinstance(result, basestring):
                print result
            else:
                try:
                    # Maybe it's an error
                    self.system.error(result[0])
                except Exception:
                    pass

    def end(self):
        commands.Frontend.end(self)
        print '* Exiting:', random.choice(various.exit_messages)
