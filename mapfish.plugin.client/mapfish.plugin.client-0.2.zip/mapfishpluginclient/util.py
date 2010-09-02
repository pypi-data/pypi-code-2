# 
# Copyright (C) 2009  Camptocamp
#  
# This file is part of mapfish.plugin.client
#  
# mapfish.plugin.client is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#  
# mapfish.plugin.client is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#  
# You should have received a copy of the GNU General Public License
# along with mapfish.plugin.client.  If not, see <http://www.gnu.org/licenses/>.
#

import sys
import os
import shutil
import subprocess

from paste.script.templates import Template, var
from paste.script.command import BadCommand
from paste.util.template import paste_script_template_renderer

# redefine paste_script_template_renderer method because the one provided
# by paste fails to import python module
# (issue related to filename parameter which should not contains spaces)
def template_renderer(content, vars, filename=None): 
    return paste_script_template_renderer(content, vars, filename=None)

class MapFishClientTemplate(Template):
    egg_plugins = ['mapfish.plugin.client']
    summary = 'MapFish client plugin template'
    template_renderer=staticmethod(template_renderer)
    _template_dir_list = ['template']
    overwrite = True

    def run(self, command, output_dir, vars):
        self.pre(command, output_dir, vars)
        for dir in self._template_dir_list:
            self._template_dir = dir
            self.write_files(command, output_dir, vars)
        self.post(command, output_dir, vars)

    def pre(self, command, output_dir, vars):
        """
        Called before template is applied.
        """
        template_dir = 'default_app_template'
        if vars.has_key('template_dir'):
            template_dir = vars['template_dir']
        self._template_dir_list.append(template_dir)
