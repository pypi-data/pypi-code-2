# DjangoDE, an integrated development environment for Django
# Copyright (C) 2010-2011 Andrew Wilkinson
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import os
import glob

from autocompleter import process_text
from djangode.data.autocomplete.namespace import Namespace
from djangode.data.autocomplete.builtins import builtins

class Module(Namespace):
    def __init__(self):
        Namespace.__init__(self, builtins)

        self.filename = None
        self.docstring = None
        self.variables = {}
        self.text_finder = None

    def get_at_text_pos(self, lineno, charno):
        return self.text_finder.get_at_text_pos(lineno, charno)

    def get_submodule(self, module_name):
        assert self.filename is not None

        for filename in glob.glob(os.path.dirname(self.filename) + os.sep + "*"):
            if filename.endswith(".py"):
                if filename.split(os.sep)[-1][:-3] == module_name:
                    return Module.load_from_file(filename)
            elif os.path.isdir(filename) and os.path.exists(filename + os.sep + "__init__.py"):
                if filename.split(os.sep)[-1] == module_name:
                    return Module.load_from_file(filename + os.sep + "__init__.py")

    def get_submodules(self, prefix):
        assert self.filename is not None

        modules = []
        for filename in glob.glob(os.path.dirname(self.filename) + os.sep + "*"):
            if filename.endswith(".py"):
                if filename.split(os.sep)[-1][:-3].startswith(prefix):
                    modules.append(filename.split(os.sep)[-1][:-3])
            elif os.path.isdir(filename) and os.path.exists(filename + os.sep + "__init__.py"):
                if filename.split(os.sep)[-1].startswith(prefix):
                    modules.append(filename.split(os.sep)[-1])
        return modules

    @staticmethod
    def load_from_file(filename):
        module = process_text(open(filename).read())
        module.filename = filename
        return module

    def __unicode__(self):
        return "<Module %s>" % (self.filename, )

    def __repr__(self):
        return "<Module %s>" % (self.filename, )
