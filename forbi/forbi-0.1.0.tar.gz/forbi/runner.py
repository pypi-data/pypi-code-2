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
##[ Description ]## Runner of client or server

import sys
import os
import cStringIO as StringIO
import getpass
from forbi.settingsparser import SettingsParser
import forbi.misc as misc
from forbi.client import ForbiClient
from forbi.server import ForbiServer

_config_file_translations = {
    'save file': 'save_file',
    'execute on new message': 'execute_on_new_message',
    'verbose': 'term_verbose',
    'colored text': 'term_colored_text',
    'server': 'is_server',
    'host': 'server_host',
    'port': 'server_port',
    'user': 'server_user',
    'password': 'server_password',
    'client port': 'client_port'
}

class ForbiRunner(SettingsParser):
    """
    A root class containing base functions meant for use by class
    objects
    """
    def __init__(self, **options):
        SettingsParser.__init__(self, _config_file_translations,
                                **options)
        # Get values, or set them to default ones
        self.set_if_nil('use_config_file', True)
        if self.use_config_file:
            self.set_if_nil('config_file_path',
                            os.path.expanduser('~/.forbi.conf'))
            self.load_from_file()
        self.set_if_nil('save_file', '~/.forbi.db')
        self.save_file = os.path.expanduser(self.save_file)
        self.set_if_nil('execute_on_new_message', None)

        self.set_if_nil('term_verbose', True)
        self.set_if_nil('term_colored_text', True)
        self.set_if_nil('is_server', False)
        self.set_if_nil('server_host', None)
        self.set_if_nil('server_port', 54547)
        self.set_if_nil('server_user', None)
        self.set_if_nil('server_password', None)
        self.set_if_nil('client_port', -1) # -1 = pick a random port

        self.communicator = None
        self.text_output_paused = False
        self.prev_error = None
        self.prev_state = None

    def state(self, msg, prefix=''):
        """State something"""
        if self.term_verbose:
            if self.text_output_paused:
                out = self.state_text_cache
            else:
                out = sys.stdout
            misc.state(msg, self.term_colored_text, prefix, out)
        self.prev_state = msg

    def error(self, msg, prefix=''):
        """Output an error message"""
        if self.term_verbose:
            if self.text_output_paused:
                out = self.error_text_cache
            else:
                out = sys.stderr
            misc.error(msg, self.term_colored_text, prefix)
        self.prev_error = msg

    def pause_text_output(self, pause=True):
        """Pause text output"""
        self.text_output_paused = pause
        self.state_text_cache = StringIO.StringIO()
        self.error_text_cache = StringIO.StringIO()

    def unpause_text_output(self, unpause=True):
        """Unpause text output"""
        self.flush_caches()
        self.pause_text_output(not unpause)

    def flush_caches(self):
        """Output all cached text"""
        sys.stdout.write(self.state_text_cache.getvalue())
        sys.stderr.write(self.error_text_cache.getvalue())

    def get_input(self, prompt, echo=True):
        """Get text input from the terminal"""
        self.pause_text_output()
        if echo:
            inp = raw_input(prompt)
        else:
            inp = getpass.getpass(prompt)
        self.unpause_text_output()
        return inp.decode(misc.encoding)

    def start(self):
        """
        Continue running either as server or client, depending on
        the options sent to the runner object
        """
        if not self.is_server:
            self.communicator = ForbiClient(
                self.server_host, self.server_port,
                self.server_user, self.server_password,
                runner=self, client_port=self.client_port,
                program=self.execute_on_new_message)
        else:
            self.communicator = ForbiServer(
                self.server_port, runner=self,
                save_file=self.save_file,
                default_client_port=self.client_port)

        self.communicator.start()

    def end(self):
        """End everything"""
        if self.communicator is not None:
            self.communicator.end()
