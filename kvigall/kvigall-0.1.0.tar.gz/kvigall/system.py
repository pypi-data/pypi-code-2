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

##[ Name        ]## system
##[ Maintainer  ]## Niels Serup <ns@metanohi.org>
##[ Description ]## Contains the kvigall system
##[ Start date  ]## 2010 August 18

import sys
import os
import math
import textwrap
from datetime import datetime, timedelta
try:
    from qvikconfig import parse as config_parse
except ImportError:
    from kvigall.external.qvikconfig import parse as config_parse
try:
    from termcolor import colored
except ImportError:
    from kvigall.external.termcolor import colored
import kvigall.various as various
import locale
locale.setlocale(locale.LC_ALL, '')

class System(object):
    def __init__(self, **etc):
        for x in etc.items():
            self.__setattr__(*x)

        attrs = dir(self)
        if not 'error_function' in attrs:
            self.error_function = various.usable_error

        # Get paths
        default_scripts_path = os.path.join(os.path.expanduser('~'), '.kvigall')
        if not self.scripts_path:
            self.scripts_path = default_scripts_path
        self.saves_path = os.path.join(self.scripts_path,
                                       'kvigall-saves')
        if not os.path.exists(self.scripts_path):
            os.mkdir(self.scripts_path)
        initfile = os.path.join(self.scripts_path, '__init__.py')
        if not os.path.exists(initfile):
            open(initfile, 'w').close()
        if not os.path.exists(self.saves_path):
            os.mkdir(self.saves_path)

        self.current_date = self.get_today() # Might change in start()
        self.current_events = None

        self.front = None

        # Wrap long lines
        self.info_wrapper = textwrap.TextWrapper(
            initial_indent=' ' * 7, subsequent_indent=' ' * 8, break_long_words=False)

        # Get config file
        try:
            # We believe in what we've been told
            conf = config_parse(os.path.join(self.scripts_path, self.config_file_path))
        except IOError:
            try:
                # We'll try the default setting instead
                conf = config_parse(os.path.join(default_scripts_path, self.config_file_path))
            except IOError:
                try:
                    # Maybe the name of the default path is actually
                    # a file
                    conf = config_parse(default_scripts_path)
                except IOError:
                    conf = {}
        self.config = conf

        # term_verbose
        if self.term_verbose is None:
            tmp = conf.get('verbose')
            if tmp is None:
                self.term_verbose = True
            else:
                self.term_verbose = tmp

        # term_color_errors
        if self.term_color_errors is None:
            tmp = conf.get('color errors')
            if tmp is None:
                self.term_color_errors = True
            else:
                self.term_color_errors = tmp
        if self.term_color_errors:
            class ColoredErrors:
                def write(self, msg):
                    sys.__stderr__.write(colored(msg, 'red'))
            sys.stderr = ColoredErrors()

        # scripts
        if not self.scripts_names:
            try:
                defsc = conf['default scripts']
                if isinstance(defsc, basestring):
                    defsc = (defsc,)
                self.scripts_names = defsc
            except KeyError:
                self.error('no script name(s) specified, quitting', False)

        # update_after
        if not self.update_after:
            tmp = conf.get('update after')
            if tmp is None:
                tmp = '1h'
            else:
                tmp = str(tmp)
        else:
            tmp = self.update_after
        try:
            upd_end = tmp[-1]
            if upd_end in ('m', 'h', 'd', 'w'):
                sec = int(tmp[:-1])
                if upd_end == 'm':
                    sec *= 60
                elif upd_end == 'h':
                    sec *= 60 * 60
                elif upd_end == 'd':
                    sec *= 60 * 60 * 24
                elif upd_end == 'w':
                    sec *= 60 * 60 * 24 * 7
                self.update_after = sec
            else:
                self.update_after = int(self.update_after)
        except Exception:
            parser.error('wrong time syntax', False)
        self.update_after = timedelta(0, self.update_after)

        # frontend
        if not self.frontend_name:
            self.frontend_name = conf.get('frontend') or 'curses'

        spl = self.frontend_name.split(':')
        self.frontend_name = spl[0]
        self.frontend_args = spl[1:]

        # start_empty
        if self.start_empty is None:
            self.start_empty = conf.get('start empty') or False

        # date_format
        if not self.date_format:
            self.date_format = conf.get('date format') or '%A, %x'

        # use_styling
        if self.use_styling is None:
            tmp = conf.get('styling')
            if tmp is None:
                self.use_styling = True
            else:
                self.use_styling = tmp

    def error(self, *args):
        if self.term_verbose:
            self.error_function(*args)

    def start(self):
        # Start everything
        sys.path.append(self.scripts_path)
        self.mods = []
        for x in self.scripts_names:
            spl = x.split(':')
            name = spl[0]
            args = spl[1:]
            mod = __import__(name, globals(), locals(), ['Connector'], -1)
            self.mods.append(mod.Connector(self, name, *args))

        # Start frontend
        frontend = None
        if self.frontend_name == 'curses':
            import kvigall.frontend.cursesfrontend as frontend
        elif self.frontend_name == 'text':
            import kvigall.frontend.textfrontend as frontend
        else:
            self.error('frontend "%s" is not supported' %
                       self.frontend_name, False)

        self.front = frontend.Frontend(self, *self.frontend_args)
        for x in self.mods:
            try:
                x.safe_start()
            except Exception, e:
                self.error(e)
                pass

        # start_date
        conf = self.config
        start_date_err = lambda: self.error(
            'given start date is not understandable', False)
        if not self.start_date:
            self.start_date = str(conf.get('start date'))
        if self.start_date:
            if self.start_date == 'today':
                self.start_date = self.get_today()
            elif self.start_date == 'tomorrow':
                self.start_date = self.get_today() + timedelta(1)
            elif self.start_date == 'yesterday':
                self.start_date = self.get_today() - timedelta(1)
            else:
                inverse = self.start_date.startswith('*')
                if inverse:
                    self.start_date = self.start_date[1:]
                func = 0
                if self.start_date.startswith('++'):
                    func = 1
                    self.start_date = self.start_date[2:]
                elif self.start_date.startswith('--'):
                    func = 2
                    self.start_date = self.start_date[2:]
                elif self.start_date.startswith('+'):
                    if inverse: start_date_err()
                    func = 3
                    self.start_date = self.start_date[1:]
                elif self.start_date.startswith('-'):
                    if inverse: start_date_err()
                    func = 4
                    self.start_date = self.start_date[1:]
                if func != 0:
                    self.current_date = self.get_today()
                    try:
                        n = int(self.start_date)
                    except Exception:
                        n = 1
                    if func == 1:
                        if inverse: self.goto_next_nothing(n)
                        else: self.goto_next(n)
                        self.start_date = self.current_date.replace() # Copy
                    elif func == 2:
                        if inverse: self.goto_previous_nothing(n)
                        else: self.goto_previous(n)
                        self.start_date = self.current_date.replace() # Copy
                    elif func == 3:
                        self.start_date = self.get_today() + timedelta(n)
                    elif func == 4:
                        self.start_date = self.get_today() - timedelta(n)
                else:
                    # [[YYYY]MM]DD
                    year, month, day = \
                        self.split_date_string(self.start_date)
                    if day == 0:
                        start_date_err()
                    else:
                        self.start_date = self.get_date(year, month, day)
        else:
            self.start_date = self.get_today()

        self.current_date = self.start_date.replace() # Copy

        # Start the frontend
        self.front.start()

    def get_events(self, force=False):
        events = []
        err = False
        for x in self.mods:
            evs = x.get_kvigall_data(self.current_date, force)
            if evs is None:
                err = True
            else:
                events.extend(evs)
        if not events and err:
            self.current_events = None
            return None
        else:
            self.current_events = events
            return events

    def get_current_date_string(self):
        return self.current_date.strftime(self.date_format)

    def split_date_string(self, string):
        try:
            day = int(string[-2:])
        except Exception:
            day = 0
        try:
            month = int(string[-5:-2])
        except Exception:
            month = 0
        try:
            year = int(string[:-4])
        except Exception:
            year = 0
        return year, month, day

    def go_forward(self, n=1):
        try:
            self.current_date += timedelta(n)
        except Exception:
            pass

    def go_backward(self, n=1):
        self.go_forward(-n)

    def goto_next(self, n=1, inverse=False):
        # Goto next day with events
        if n < 0:
            n *= -1
            op = -1
        else:
            op = 1
        if n == 0 and bool(self.get_events()) is inverse:
            while n == 0:
                try:
                    self.current_date += op * timedelta(1)
                except Exception:
                    return False
                evs = self.get_events()
                if evs is None:
                    return False
                elif inverse ^ bool(evs): # XOR, same as (not inverse and evs) or (inverse and not evs):
                    n += 1
            return

        while n > 0:
            try:
                self.current_date += op * timedelta(1)
            except Exception:
                return False
            evs = self.get_events()
            if evs is None:
                return False
            elif inverse ^ bool(evs):
                n -= 1

    def goto_previous(self, n=1, inverse=False):
        self.goto_next(-n, inverse)

    def goto_next_nothing(self, n=1):
        self.goto_next(n, True)

    def goto_previous_nothing(self, n=1):
        self.goto_previous(n, True)

    def get_date(self, year, month, day):
        # Return datetime of date
        if year == 0:
            year = self.current_date.year
        if month == 0:
            month = self.current_date.month
        try:
            return datetime(year, month, day)
        except ValueError, e:
            self.error(e)

    def goto_date(self, year, month, day):
        date = self.get_date(year, month, day)
        return date is not None

    def get_today(self):
        now = datetime.now()
        return datetime(now.year, now.month, now.day)

    def goto_today(self):
        self.current_date = self.get_today()

    def goto_start(self):
        self.current_date = self.start_date.replace() # Copy

    def fill_text(self, text):
        spl = text.split('\n')
        for i in range(1, len(spl)):
            spl[i] = ' ' + spl[i]
        return '\n'.join([self.info_wrapper.fill(y) for y in spl])

    def exit(self, c=1):
        sys.exit(c)

    def end(self):
        # End frontend and mods
        if self.front is not None:
            self.front.end()
            for x in self.mods:
                x.safe_end()

