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

import mako.template as t

class PrologDumper(object):
    """
    Class to convert the extracted facts to a prolog database
    """
    def __init__(self, options, dependencies, cost_per_file, violations):
        """
        initialize a PrologDumper with
        - options : command line options
        - dependencies: a set of Dependency
        - cost_per_file : a list of filenames and associated parsing cost (#statements)
        """
        self.options = options
        self.dependencies = dependencies
        self.cost_per_file = cost_per_file
        self.violations = violations

    def dump(self, filename):
        """
        dumps the data as a prolog database in the file "filename".
        If no explicit folder is specified, the prolog database ends up in the sandbox folder.
        """
        files = ""
        filebelongstoproject = ""
        fileincludesfile = ""
        hierarchydefinition = ""
        lines = ""
        projects = set([])
        from path import path
        path_specified = path(filename).dirname() != path('')
        if not path_specified:
            filename = "%s" % (path(self.options.sandbox)/path(filename))
        with open(filename, "w") as f:
            for fl in self.cost_per_file:
                if fl.is_code():
                    files += "cppfile '%s'.\n" % fl.analysis_name()
                else:
                    files += "headerfile '%s'.\n" % fl.analysis_name()
                filebelongstoproject += "'%s' belongs to project '%s'.\n" % (fl.analysis_name(), fl.project_name())
                projects.add(fl.project_name())
                lines += "'%s' costs %d.\n" % (fl.analysis_name(), self.cost_per_file[fl])
            for d in self.dependencies:
                fileincludesfile += "'%s' includes '%s'.\n" % (d.source_node.analysis_name(), d.include_node.analysis_name())

            for v in self.violations:
                if (self.options.case_insensitive):
                    hierarchydefinition += "'%s' cannot include from '%s'.\n" % (v.from_proj.lower(), v.to_proj.lower())
                    projects.add(v.from_proj.lower())
                    projects.add(v.to_proj.lower())
                else:
                    hierarchydefinition += "'%s' cannot include from '%s'.\n" % (v.from_proj, v.to_proj)
                    projects.add(v.from_proj)
                    projects.add(v.to_proj)

            projectsstring = ""
            for p in projects:
                projectsstring += "project '%s'.\n" % p
            mytemplate = t.Template(filename="template/PrologTemplate.pl")
            f.write(mytemplate.render(files=files, 
                projects=projectsstring,
                filebelongstoproject=filebelongstoproject, 
                fileincludesfile=fileincludesfile,
                hierarchydefinition=hierarchydefinition,
                lines=lines))
        destination = path(filename).abspath().dirname()
        templatedir = path("template").abspath()
        q = (templatedir / path("intuitivequery.pl"))
        q.copy(destination)
        import logging
        logging.info("Copy %s to %s" % (q, destination))
        c = (templatedir / path("categories.pl"))
        c.copy(destination)
        logging.info("Copy %s to %s" % (c, destination))

       
