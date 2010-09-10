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

##[ Name        ]## frontend.genericfrontend
##[ Maintainer  ]## Niels Serup <ns@metanohi.org>
##[ Description ]## Contains a generic base frontend
##[ Start date  ]## 2010 August 25

class Frontend(object):
    def __init__(self, system, *args, **kwargs):
        self.system = system
        self.init(*args, **kwargs)

    def init(self, *args, **kwargs):
        pass

    def start(self):
        pass

    def end(self):
        pass
