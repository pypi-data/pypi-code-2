# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: stefaan.himpe@gmail.com

from FileCollector import FileCollector
from IncludeFileFinder import IncludeFileFinder
from ProjectResolver import ProjectResolver
from Dependency import Dependency
from HierarchyParser import HierarchyParser
from PrologDumper import PrologDumper

class FactExtractor(object):
    """
    Class that walks over the files and extracts dependency information.
    This dependency information can then be dumped by using one of various
    backends.
    """
    def __init__(self, options):
        """
        Initialize the dependency analyzer with the command line options object.
        """
        self.options = options

    def run(self):
        """
        This implements the meat of the class:
            * first collect a set of files to examine
            * then, for each file, collect all the dependencies and projects

        """
        from path import path
        violations = []
        p = None
        if self.options.hierarchy:
            p = path(self.options.hierarchy)
            folder_specified = p.dirname() != path('')
            if not folder_specified:
                p = path(self.options.hierarchy)/p
            p = p.abspath()
        if p:
            h = HierarchyParser()
            filename = "%s" % p
            violations = h.parse(filename)

        file_nodes = FileCollector(self.options).nodes()
        project_resolver = ProjectResolver(self.options)
        dependencies = set([])
        cost_per_file = {}
        for p in file_nodes:
            with open(p.file_name(), "r") as f:
                contents = f.read()
                ifinder = IncludeFileFinder(contents)
                ifinder.parse()
                include_files = ifinder.get_raw_parse_result()
                for i in include_files:
                    full_incl_file = project_resolver.abs_node(p,i)
                    if full_incl_file:
                        if full_incl_file.is_header() or full_incl_file.is_code():
                            dependencies.add(Dependency(p, full_incl_file))
                        else:
                            import logging
                            logging.warning("File %s has an unknown file type. Please update your header/cpp file suffixes." % full_incl_file)
                    
                cost_per_file[p] = ifinder.get_no_of_statements()
                
        p = PrologDumper(self.options, dependencies, cost_per_file, violations)
        p.dump(self.options.prolog_name)

