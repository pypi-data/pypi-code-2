# -*- coding: utf-8 -*-
# feed2twitter
# Copyright (C) 2009 EBC - Empresa Brasil de Comunicação
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from ConfigParser import ConfigParser, NoOptionError
from parsetime import parsetime
import sys

class MicroblogConfig(ConfigParser):
    def __init__(self, filename):
        self._configs = []
        ConfigParser.__init__(self)
        x = self.read(filename)
        if len(x) == 0:
            raise Exception('erro')

    
    def configs(self):
        sections = self.sections()
        sections.remove('global')
        for section in sections:
            config = {}
            config['url'] = self.get(section, "url").strip()
            config['section'] = section
            config['service'] = self.get(section, "service").strip()
            config['oauth_token'] = self.get(section, "oauth_token").strip()
            config['oauth_secret'] = self.get(section, "oauth_secret").strip()
            if config['service'] != 'twitter':
                config['username'] = self.get(section, "username").strip()
                config['password'] = self.get(section, "password").strip()
            config['mode'] = self.get(section,"mode").strip()
            try:
                config['items'] = self.getint(section,"items")
            except NoOptionError:
                config['items'] = 5
	    try:
                config['pidfile'] = self.get("global","pidfile").strip()
            except NoOptionError:
		config['pidfile'] = None	
            try:
                config['interval'] = parsetime(self.get("global","interval").strip())
            except:
                print('Error in the interval setting')
                sys.exit(1)
            try:
                config['consumer_key'] = self.get("global","consumer_key").strip()
            except:
                print('Error in the consumer_key setting')
                sys.exit(1)
            try:
                config['consumer_secret'] = self.get("global","consumer_secret").strip()
            except:
                print('Error in the consumer_secret setting')
                sys.exit(1)
            try:
                config['shortener'] = self.get(section,'shortener').strip()
            except NoOptionError:
                config['shortener'] = 'tinyurl'

            if config['service'] == 'wordpress':
                config['xmlrpc_url'] = self.get(section, "xmlrpc_url").strip()
            self._configs.append(config)
        return self._configs
