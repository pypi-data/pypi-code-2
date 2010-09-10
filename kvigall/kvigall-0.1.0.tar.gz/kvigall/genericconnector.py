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

##[ Name        ]## genericconnector
##[ Maintainer  ]## Niels Serup <ns@metanohi.org>
##[ Description ]## Contains the kvigall Connector base class
##[ Start date  ]## 2010 August 26

import os.path
from datetime import datetime
try:
    import cPickle as pickle
except ImportError:
    import pickle

# The following class is supposed to be used as a base module for
# creating kvigall modules.

class Connector(object):
    name=None
    title=None

    def __init__(self, system, script_name, *args, **kwargs):
        self.system = system
        self.script_name = script_name
        if self.name is None:
            self.name = self.script_name
        if self.title is None:
            self.title = self.name

        if not self.system.use_cache_only:
            try:
                self.init(*args, **kwargs)
            except Exception, e:
                self.system.error(e)
                pass

    def init(self, *args, **kwargs):
        pass

    def start(self):
        pass

    def end(self):
        pass

    def safe_start(self):
        if not self.system.use_cache_only:
            self.start()

    def safe_end(self):
        if not self.system.use_cache_only:
            self.end()

    def get_save_file(self, date):
        return os.path.join(self.system.saves_path, '%s-%04d%02d%02d' %
                            (self.name, date.year, date.month, date.day))

    def get_cached_data(self, date):
        fpath = self.get_save_file(date)
        if not os.path.exists(fpath):
            return False, None

        try:
            cached = pickle.load(open(fpath))
        except Exception:
            os.remove(fpath)
            return False, None

        if datetime.now() - cached[0] < self.system.update_after:
            return True, cached[1]
        else:
            return False, cached[1]

    def cache_data(self, date, events):
        fpath = self.get_save_file(date)
        pickle.dump((datetime.now(), events), open(fpath, 'wb'))

    def get_kvigall_data(self, date, force=False):
        if self.system.use_cache_only:
            return self.get_cached_data(date)[1]
        if force:
            cached_events = False, None
        else:
            cached_events = self.get_cached_data(date)
        if cached_events[0]:
            return cached_events[1]
        else:
            try:
                events = self.get_kvigall_events(date)
                if not cached_events[0]:
                    self.cache_data(date, events)
                return events
            except Exception, e:
                if force:
                    self.system.error(e)
                return cached_events[1]

    def get_kvigall_events(self, date):
        pass
