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
##[ Description ]## Settings parser

import os
try:
    from qvikconfig import parse as config_parse
except ImportError:
    from forbi.external.qvikconfig import parse as config_parse

basic_config_translations = {}

class SettingsParser(object):
    """
    A parser of options and settings with support for loading data
    from config files
    """
    def __init__(self, ok_config_translations={}, **etc):
        for key, val in basic_config_translations.iteritems():
            ok_config_translations[key] = val
        self.ok_config_translations = ok_config_translations
        self.ok_config_values = set(ok_config_translations.keys())

        for x in etc.items():
            self.__setattr__(*x)

    def is_nil(self, prop):
        return not prop in dir(self) or self.__dict__[prop] is None

    def set_if_nil(self, prop, val):
        if self.is_nil(prop):
            self.__dict__[prop] = val

    def load_from_file(self):
        if not self.is_nil('config_file_path'):
            # Attempt to parse a config file
            try:
                conf = config_parse(self.config_file_path)
                ok_keys = set(conf) & self.ok_config_values

                for key in ok_keys:
                    o_key = key
                    if key in self.ok_config_values:
                        n_key = self.ok_config_translations[key]
                        if n_key is not None:
                            key = n_key
                        self.set_if_nil(key, conf[o_key])
            except IOError:
                pass
