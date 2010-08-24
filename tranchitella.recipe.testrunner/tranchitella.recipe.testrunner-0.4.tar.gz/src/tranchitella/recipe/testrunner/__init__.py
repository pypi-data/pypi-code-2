# tranchitella.recipe.testrunner
# Copyright (C) 2008-2010 Tranchitella Kft. <http://tranchtella.eu>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import os
import os.path
import pkg_resources
import sys
import zc.buildout.easy_install
import zc.recipe.egg

class Recipe:

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        options['script-name'] = os.path.join(
            buildout['buildout']['bin-directory'],
            options.get('script-name', self.name))
        if not options.get('working-directory', ''):
            options['location'] = os.path.join(
                buildout['buildout']['parts-directory'], name)
        self.egg = zc.recipe.egg.Egg(buildout, name, options)

    def relativize(self, base, path):
        base += os.path.sep
        if path.startswith(base):
            path = 'join(base, %r)' % path[len(base):]
        else:
            path = repr(path)
        return path

    def install(self):
        options = self.options
        dest = []
        eggs, ws = self.egg.working_set(('coverage', 'tranchitella.recipe.testrunner'))
        test_paths = [ws.find(pkg_resources.Requirement.parse(spec)).location
            for spec in eggs]
        defaults = options.get('defaults', '').strip()
        if defaults:
            defaults = '(%s) + ' % defaults
        wd = options.get('working-directory', '')
        if not wd:
            wd = options['location']
            if os.path.exists(wd):
                assert os.path.isdir(wd)
            else:
                os.mkdir(wd)
            dest.append(wd)
        wd = os.path.abspath(wd)
        if self.egg._relative_paths:
            wd = self.relativize(self.egg._relative_paths, wd)
            test_paths = [self.relativize(self.egg._relative_paths, p)
                for p in test_paths]
        else:
            wd = repr(wd)
            test_paths = map(repr, test_paths)
        initialization = initialization_template % wd
        env_section = options.get('environment', '').strip()
        if env_section:
            env = self.buildout[env_section]
            for key, value in env.items():
                initialization += env_template % (key, value)
        initialization_section = options.get('initialization', '').strip()
        if initialization_section:
            initialization += initialization_section
        dest.extend(zc.buildout.easy_install.scripts(
            [(options['script-name'], 'tranchitella.recipe.testrunner', 'run')],
            ws, options['executable'],
            self.buildout['buildout']['bin-directory'],
            extra_paths=self.egg.extra_paths,
            arguments=defaults + (
                '[\n'+
                ''.join(("        '--test-path', %s,\n" % p)
                    for p in test_paths)
                +'        ]'),
            initialization=initialization,
            relative_paths=self.egg._relative_paths,
        ))
        return dest

    update = install


arg_template = """[
  '--test-path', %(TESTPATH)s,
  ]"""

initialization_template = """import os
sys.argv[0] = os.path.abspath(sys.argv[0])
os.chdir(%s)
"""

env_template = """os.environ['%s'] = %r
"""

def run(defaults=None, args=None, script_parts=None):
    import zope.testrunner
    import zope.testrunner.options
    from coverage import coverage
    # add the --coverage-annotate option
    zope.testrunner.options.analysis.add_option(
         '--coverage-annotate', action="store", metavar='PATH',
        dest='coverage_annotate',
        help="""Store coverage annotation in the specified directorz.""")
    # add the --coverage-branch option
    zope.testrunner.options.analysis.add_option(
         '--coverage-branch', action="store_true",
        dest='coverage_branch', help="""Enable branch coverage.""")
    # add the --coverage-module option
    zope.testrunner.options.analysis.add_option(
         '--coverage-module', action="append", type='string',
        dest='coverage_modules', metavar="MODULE",
        help="Perform code-coverage analysis for the given module using "
            "the coverage library.")
    # add the --coverage-xml option
    zope.testrunner.options.analysis.add_option(
         '--coverage-xml', action="store_true",
        dest='coverage_xml', help="""Enable XML coverage report.""")
    # add the --coverage-html option
    zope.testrunner.options.analysis.add_option(
         '--coverage-html', action="store_true",
        dest='coverage_html', help="""Enable HTML coverage report.""")
    options = zope.testrunner.options.get_options(args, defaults)
    # coverage support
    if options.coverage_modules:
        coverage = coverage(branch=options.coverage_branch)
        coverage.exclude('#pragma[: ]+[nN][oO] [cC][oO][vV][eE][rR]')
        coverage.start()
    # test runner
    failed = zope.testrunner.run_internal(defaults, args, script_parts)
    # coverage report
    if options.coverage_modules:
        coverage.stop()
        coverage.save()
        modules = [module for name, module in sys.modules.items()
            if with_coverage(name, module, options.coverage_modules)]
        print "\nCoverage report\n===============\n"
        coverage.report(modules)
        if options.coverage_xml:
            coverage.xml_report(modules)
        if options.coverage_html:
            coverage.html_report(modules)
        if options.coverage_annotate:
            coverage.annotate(morfs=modules,
                directory=options.coverage_annotate)
    # return code
    sys.exit(int(failed))


def with_coverage(name, module, modules):
    if hasattr(module, '__file__'):
        for m in modules:
            if name.startswith(m):
                return True
    return False
