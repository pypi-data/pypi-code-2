##
## config.py
## Login : <uli@pu.smp.net>
## Started on  Sat Jul 31 10:17:56 2010 Uli Fouquet
## $Id$
## 
## Copyright (C) 2010 Uli Fouquet
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
## 
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##
"""Configuration components.
"""
import os
from ConfigParser import SafeConfigParser

def get_config_paths(config_path=None):
    """Get a list of possible config file locations.

    Return a tuple of possible config file paths.
    
    The config parser can lookup all these locations and in the order
    returned. If `config_path` is not None, it will be appended to the
    list.

    As also config parser will not complain about not existing files,
    we won't do eigther.
    """
    system_path = os.path.abspath('/etc/indexer.conf')
    user_path = os.path.abspath(
        os.path.expanduser('~/indexer.conf'))
    if config_path is not None:
        return (system_path, user_path, config_path)
    return (system_path, user_path)

class PyNotifyConfigParser(SafeConfigParser):
    """A config parser that takes a configuration file as optional
       argument.
    """

    def __init__(self, config_path=None):
        self._config_paths = get_config_paths(config_path)
        return

    def read(self):
        """Read the config files.
        """
        SafeConfigParser.read(self, self._config_paths)
        #super(PyNotifyConfigParser, self).read(self._config_paths)
