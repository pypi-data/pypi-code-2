"""
yamlconfig.py
A config file reader that support yaml based config files.

Copyright 2010, Kelsey Hightower
Kelsey Hightower <kelsey.hightower@gmail.com>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
02110-1301  USA
"""
import string
import yaml

class YamlConfig(dict):
    """
    YAML configuration file reader with basic variable interpolation.
    """

    def __init__(self, infile, defaults=None):
        """
        Initialization method.
        """
        dict.__init__(self)
        self.infile = infile

        if defaults is None:
            self.defaults = {}
        else:
            self.defaults = defaults

        indict = self.get_config()

        for entry in indict:
            self[entry] = indict[entry]

    def _interpolate(self, infile, defaults):
        """
        Interpolate variables.
        """
        with open(infile, 'r') as config:
            template = string.Template(config.read())
            interpolated_config = template.safe_substitute(defaults)
        return interpolated_config

    def _deserialize(self, infile):
        """
        Deserialize YAML string.
        """
        config = yaml.load(infile)
        return config

    def get_config(self):
        self.infile = self._interpolate(self.infile, self.defaults)
        config = self._deserialize(self.infile)
        return config
