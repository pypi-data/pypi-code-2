"""checkers for python source files

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
from __future__ import with_statement

__docformat__ = "restructuredtext en"

import sys
import os
import re
from commands import getoutput
from os.path import join, exists, abspath, dirname, split
from test import test_support
from warnings import warn

from logilab.common.testlib import find_tests
from logilab.common.modutils import get_module_files
from logilab.common.fileutils import norm_read
from logilab.common.shellutils import pushd
from logilab.common.decorators import cached
from logilab.common.compat import any
from logilab.common.proc import RESOURCE_LIMIT_EXCEPTION

try:
    from logilab.devtools.lib.pkginfo import PackageInfo
    from logilab.devtools.__pkginfo__ import version as devtools_version
except ImportError:
    devtools_version = 'nc'

try:
    # development version
    from logilab.devtools.lib import coverage
    COVFILE = coverage.__file__.replace('.pyc', '.py')
except ImportError:
    try:
        # debian installed version
        import coverage
        COVFILE = coverage.__file__.replace('.pyc', '.py')
    except ImportError:
        coverage = None

from apycotlib import register
from apycotlib import SUCCESS, FAILURE, PARTIAL, NODATA, ERROR
from apycotlib import SimpleOutputParser, ParsedCommand
from apycotlib.checkers import BaseChecker, AbstractFilteredFileChecker


def pyinstall_path(test):
    path = _pyinstall_path(test)
    if not exists(path):
        raise Exception('path %s doesn\'t exist' %  path)
    return path

@cached
def _pyinstall_path(test):
    """return the project's installation path"""
    config = test.apycot_config()
    if 'install_path' in config:
        return config['install_path']
    modname = config.get('python_modname')
    if modname:
        return join(test.tmpdir, 'local', 'lib', 'python', *modname.split('.'))
    elif exists(join(test.tmpdir, test.project_path(), '__pkginfo__.py')):
        pkginfo = PackageInfo(directory=join(test.tmpdir, test.project_path()))
        modname = getattr(pkginfo, 'modname', None)
        package = getattr(pkginfo, 'subpackage_of', None)
        if modname and package:
            modname = '%s.%s' % (package, modname)
        if modname:
            path = join(test.tmpdir, 'local', 'lib', 'python',
                        *modname.split('.'))
            cfg = test.apycot_config()
            if cfg.get('subpath'):
                path = join(path, cfg['subpath'])
        return path
    return join(test.tmpdir, test.project_path(subpath=True))

def pyversion_available(python):
    return not os.system('%s -V 2>/dev/null' % python)


class PythonSyntaxChecker(AbstractFilteredFileChecker):
    """check syntax of python file

       Use Pylint to check a score for python package. The check fails if the score is
       inferior to a given threshold.
    """

    id = 'python_syntax'
    checked_extensions = ('.py', )

    def check_file(self, filepath):
        """try to compile the given file to see if it's syntaxicaly correct"""
        # Try to compile it. If compilation fails, then there's a
        # SyntaxError
        try:
            compile(norm_read(filepath) + '\n', filepath, "exec")
            return SUCCESS
        except SyntaxError, error:
            self.writer.error(error.msg, path=filepath, line=error.lineno)
            return FAILURE

    def version_info(self):
        self.record_version_info('python', sys.version)

register('checker', PythonSyntaxChecker)


class PyTestParser(SimpleOutputParser):
    status = NODATA
    non_zero_status_code = FAILURE
    # search for following output:
    #
    # 'Ran 42 test cases in 0.07s (0.07s CPU), 3 errors, 31 failures, 3 skipped'
    regex = re.compile(
        r'Ran (?P<total>[0-9]+) test cases '
        'in (?P<time>[0-9]+(.[0-9]+)?)s \((?P<cputime>[0-9]+(.[0-9]+)?)s CPU\)'
        '(, )?'
        '((?P<errors>[0-9]+) errors)?'
        '(, )?'
        '((?P<failures>[0-9]+) failures)?'
        '(, )?'
        '((?P<skipped>[0-9]+) skipped)?'
        )

    total, failures, errors, skipped = 0, 0, 0, 0

    def __init__(self, writer, options=None):
        super(PyTestParser, self).__init__(writer, options)
        self.total    = 0
        self.failures = 0
        self.skipped  = 0
        self.errors   = 0

    def _parse(self, stream):
        self.status = None
        super(PyTestParser, self)._parse(stream)
        if self.errors or self.failures:
            self.set_status(FAILURE)
        elif self.skipped:
            self.set_status(PARTIAL)
        elif not self.total:
            self.set_status(NODATA)
        elif self.total >= 0:
            self.set_status(SUCCESS)

    @property
    def success(self):
        return max(0, self.total - sum(( self.failures, self.errors,
                                         self.skipped,)))
    def add_junk(self, line):
        if any(c for c in line if c not in 'EFS. \n\t\r-*'):
            self.unparsed.append(line)

    def extract_tests_status(self, values):
        for status in ('failures', 'errors', 'skipped'):
            try:
                setattr(self, status,
                        max(getattr(self, status), int(values[status])))
            except TypeError:
                pass

    def parse_line(self, line):
        match = self.regex.match(line)
        if match is not None:
            values = match.groupdict()
            total = int(values['total'])
            self.total += total
            self.extract_tests_status(values)
        else:
            self.add_junk(line)

PYVERSIONS_OPTIONS = {
    'tested_python_versions': {
        'type': 'csv',
        'help': ('comma separated list of python version (such as 2.5) that '
                 'should be considered for testing.'),
        },
    'ignored_python_versions': {
        'type': 'csv',
        'help': ('comma separated list of python version (such as 2.5) that '
                 'should be ignored for testing when '
                 'use_pkginfo_python_versions is set to 1.'),
        },
    'use_pkginfo_python_versions': {
        'type': 'int', 'default': True,
        'help': ('0/1 flag telling if tested python version should be '
                 'determinated according to __pkginfo__.pyversion of the '
                 'tested project. This option is ignored if tested_python_versions '
                 'is set.'),
        },
    'pycoverage': {
        'type': 'int', 'default': False,
        'help': ('Tell if test should be run with pycoverage  to gather '
                 'coverage data.'),
        },
    }

class PyTestChecker(BaseChecker):
    """check that unit tests of a python package succeed using the pytest command
    (from logilab.common)
    """

    id = 'pytest'
    need_preprocessor = 'install'
    parsercls = PyTestParser
    parsed_content = 'stdout'
    options_def = PYVERSIONS_OPTIONS.copy()
    options_def.update({
        'pytest.extra_argument': {
            'type': 'string',
            'help': ('extra argument to give to pytest. Add this option multiple '
                     'times in the correct order to give several arguments.'),
            },
        })

    def __init__(self, writer, options=None):
        BaseChecker.__init__(self, writer, options)
        self._path = None
        self.test = None

    @property
    @cached
    def pyversions(self):
        tested_pyversions = self.options.get("tested_python_versions")
        if tested_pyversions:
            pyversions = set(tested_pyversions)
        elif self.options.get("use_pkginfo_python_versions"):
            try:
                pkginfodir = dirname(self.test.environ['pkginfo'])
            except KeyError:
                pkginfodir = self.test.project_path()
            try:
                pkginfo = PackageInfo(directory=pkginfodir)
                pyversions = set(pkginfo.pyversions)
            except (NameError, ImportError):
                pyversions = set()
            ignored_pyversions = self.options.get("ignored_python_versions")
            if ignored_pyversions:
                ignored_pyversions = set(ignored_pyversions)
                ignored_pyversions = pyversions.intersection(
                    ignored_pyversions)
                if ignored_pyversions:
                    for py_ver in ignored_pyversions:
                        self.writer.debug("python version %s ignored", py_ver)
                    pyversions.difference_update(ignored_pyversions)
        else:
            pyversions = None
        if pyversions:
            pyversions_ = []
            for pyver in pyversions:
                python = 'python%s' % pyver
                if not pyversion_available(python):
                    self.writer.error('config asked for %s, but it\'s not available', pyver)
                else:
                    pyversions_.append(python)
            pyversions = pyversions_
        else:
            pyversions = [sys.executable]
        return pyversions

    def version_info(self):
        if self.pyversions:
            self.record_version_info('python', ', '.join(self.pyversions))

    def enable_coverage(self):
        if self.options.get('pycoverage') and coverage:
            # save back location of the coverage data file for usage in
            # narval action
            self.coverage_data = join(testdir, '.coverage')
            return True
        return False

    def setup_check(self, test):
        """run the checker against <path> (usually a directory)"""
        test_support.verbose = 0
        self.test = test
        if not self.pyversions:
            self.writer.error('no required python version available')
            return ERROR
        return SUCCESS

    def do_check(self, test):
        if self.enable_coverage():
            command = ['-c', 'from logilab.common.pytest import run; import sys; sys.argv=["pytest", "--coverage"]; run()']
        else:
            command = ['-c', 'from logilab.common.pytest import run; run()']
        extraargs = self.options.get("pytest.extra_argument", [])
        if not isinstance(extraargs, list):
            command.append(extraargs)
        else:
            command += extraargs
        cwd = os.getcwd()
        # XXX may cause unexpected bug in executed concurrently with another step
        os.chdir(pyinstall_path(test))
        try:
            status = SUCCESS
            testresults = {'success': 0, 'failures': 0,
                           'errors': 0, 'skipped': 0}
            total = 0
            for python in self.pyversions:
                cmd = self.run_test(command, python)
                for rtype in testresults:
                    total += getattr(cmd.parser, rtype)
                    testresults[rtype] += getattr(cmd.parser, rtype)
                status = self.merge_status(status, cmd.status)
            self.execution_info(total, testresults)
            return status
        finally:
            os.chdir(cwd)

    def execution_info(self, total, testresults):
        self.writer.raw('total_test_cases', total, 'result')
        self.writer.raw('succeeded_test_cases', testresults['success'], 'result')
        self.writer.raw('failed_test_cases', testresults['failures'], 'result')
        self.writer.raw('error_test_cases', testresults['errors'], 'result')
        self.writer.raw('skipped_test_cases', testresults['skipped'], 'result')

    def get_command(self, command, python):
        return [python, '-W', 'ignore'] + command

    def run_test(self, command, python='python'):
        """execute the given test file and parse output to detect failed /
        succeed test cases
        """
        if isinstance(command, basestring):
            command = [command]
        command = self.get_command(command, python)
        cmd = ParsedCommand(self.writer, command,
                            parsercls=self.parsercls,
                            parsed_content=self.parsed_content,
                            path=self._path)
        #cmd.parser.path = join(self._path, command[0]) # XXX
        cmd.run()
        cmd.set_status(cmd.parser.status)
        return cmd

register('checker', PyTestChecker)


class PyUnitTestParser(PyTestParser):
    result_regex = re.compile(
        r'(OK|FAILED)'
        '('
        ' \('
        '(failures=(?P<failures>[0-9]+))?'
        '(, )?'
        '(errors=(?P<errors>[0-9]+))?'
        '(, )?'
        '(skipped=(?P<skipped>[0-9]+))?'
        '\)'
        ')?')

    total_regex = re.compile(
        'Ran (?P<total>[0-9]+) tests?'
        ' in (?P<time>[0-9]+(.[0-9]+)?s)')

    def parse_line(self, line):
        match = self.total_regex.match(line)
        if match is not None:
            self.total = int(match.groupdict()['total'])
            return
        match = self.result_regex.match(line)
        if match is not None:
            self.extract_tests_status(match.groupdict())
            return
        self.add_junk(line)


class PyUnitTestChecker(PyTestChecker):
    """check that unit tests of a python package succeed

    Execute tests found in the "test" or "tests" directory of the package. The
    check succeed if no test cases failed. Note each test module is executed by
    a spawed python interpreter and the output is parsed, so tests should use
    the default text output of the unittest framework, and avoid messages on
    stderr.

    spawn unittest and parse output (expect a standard TextTestRunner)
    """

    id = 'pyunit'
    parsed_content = 'stderr'
    parsercls = PyUnitTestParser
    options_def = PYVERSIONS_OPTIONS.copy()
    options_def.update({
        'test_dirs': {
            'type': 'csv', 'default': ('test', 'tests'),
            'help': ('comma separated list of directories where tests could be '
                     'find. Search in "test" and "tests by default.'),
            },
        })

    def do_check(self, test):
        status = SUCCESS
        testdirs = self.options.get("test_dirs")
        basepath = test.project_path(subpath=True)
        for testdir in testdirs:
            testdir = join(basepath, testdir)
            if exists(testdir):
                self._path = testdir
                with pushd(testdir):
                    _status = self.run_tests()
                    status = self.merge_status(status, _status)
                break
        else:
            self.writer.error('no test directory', path=basepath)
            status = NODATA
        return status

    def run_tests(self):
        """run a package test suite
        expect to be in the test directory
        """
        tests = find_tests('.')
        if not tests:
            self.writer.error('no test found', path=self._path)
            return NODATA
        status = SUCCESS
        testresults = {'success': 0, 'failures': 0,
                       'errors': 0, 'skipped': 0}
        total = 0
        for python in self.pyversions:
            for test_file in tests:
                cmd = self.run_test(test_file + '.py', python)
                total += cmd.parser.total
                for rtype in testresults:
                    testresults[rtype] += getattr(cmd.parser, rtype)
                if cmd.status == NODATA:
                    self.writer.error('no test found', path=test_file)
                status = self.merge_status(status, cmd.status)
        self.execution_info(total, testresults)
        return status

    def get_command(self, command, python):
        if self.enable_coverage():
            return [python, '-W', 'ignore',  COVFILE, '-x',
                    '-p', pyinstall_path(self.test)] + command
        return [python, '-W', 'ignore'] + command


register('checker', PyUnitTestChecker)


class PyDotTestParser(PyUnitTestParser):
    line_regex = re.compile(
            r'(?P<filename>\w+\.py)(\[(?P<ntests>\d+)\] | - )(?P<results>.*)')

    # XXX overwrite property
    success = 0

    def _parse(self, stream):
        for _, _, _, results in self.line_regex.findall(stream.read()):
            if results == "FAILED TO LOAD MODULE":
                self.errors += 1
            else:
                self.success += results.count('.')
                self.total += results.count('.')
                self.failures += results.count('F')
                self.total += results.count('F')
                self.errors += results.count('E')
                self.total += results.count('E')
                self.skipped += results.count('s')
                self.total += results.count('s')
        if self.failures or self.errors:
            self.set_status(FAILURE)
        elif self.skipped:
            self.set_status(PARTIAL)
        elif not self.success:
            self.set_status(NODATA)


class PyDotTestChecker(PyUnitTestChecker):
    """check that py.test based unit tests of a python package succeed

    spawn py.test and parse output (expect a standard TextTestRunner)
    """
    need_preprocessor = 'install'
    id = 'py.test'
    parsercls = PyDotTestParser
    parsed_content = 'stdout'
    options_def = PYVERSIONS_OPTIONS.copy()

    def get_command(self, command, python):
        # XXX coverage
        return ['py.test', '--exec=%s' % python, '--nomagic', '--tb=no'] + command

register('checker', PyDotTestChecker)


class PyLintChecker(BaseChecker):
    """check that the python package as a decent pylint evaluation
    """
    need_preprocessor = 'install'
    id = 'pylint'
    options_def = {
        'pylintrc': {
            'help': ('path to a pylint configuration file.'),
            },
        'pylint.threshold': {
            'type': 'int', 'default': 7,
            'help': ('integer between 1 and 10 telling expected pylint note to '
                     'pass this check. Default to 7.'),
         },
        'pylint.show_categories': {
            'type': 'csv', 'default': ['E', 'F'],
            'help': ('comma separated list of pylint message categories to add to '
                     'reports. Default to error (E) and failure (F).'),
         },
        'pylint.additional_builtins': {
            'type': 'csv',
            'help': ('comma separated list of additional builtins to give to '
                     'pylint.'),
            },
        'pylint.disable': {
            'type': 'csv',
            'help': ('comma separated list of pylint message id that should be '
                     'ignored.'),
            },
        'pylint.ignore': {
            'type': 'csv',
            'help': 'comma separated list of files or directories to ignore',
            },
        }

    def version_info(self):
        self.record_version_info('pylint', pylint_version)

    def do_check(self, test):
        """run the checker against <path> (usually a directory)"""
        threshold = self.options.get('pylint.threshold')
        pylintrc_path = self.options.get('pylintrc')
        linter = PyLinter(pylintrc=pylintrc_path)
        # register checkers
        checkers.initialize(linter)
        # load configuration
        package_wd_path = test.project_path()
        if exists(join(package_wd_path, 'pylintrc')):
            linter.load_file_configuration(join(package_wd_path, 'pylintrc'))
        else:
            linter.load_file_configuration()
        linter.set_option('persistent', False)
        linter.set_option('reports', 0, action='store')
        linter.quiet = 1
        # set file or dir to ignore
        for option in ('ignore', 'additional_builtins', 'disable'):
            value = self.options.get('pylint.' + option)
            if value is not None:
                linter.global_set_option(option.replace('_', '-'), ','.join(value))
        # message categories to record
        categories = self.options.get('pylint.show_categories')
        linter.set_reporter(MyLintReporter(self.writer, test.tmpdir, categories))
        # run pylint
        linter.check(pyinstall_path(test))
        try:
            note = eval(linter.config.evaluation, {}, linter.stats)
            self.writer.raw('pylint.evaluation', '%.2f' % note, 'result')
        except ZeroDivisionError:
            self.writer.raw('pylint.evaluation', '0', 'result')
            note = 0
        except RESOURCE_LIMIT_EXCEPTION:
            raise
        except Exception:
            self.writer.error('Error while processing pylint evaluation',
                              path=test.project_path(subpath=True), tb=True)
            note = 0
        self.writer.raw('statements', '%i' % linter.stats['statement'], 'result')
        if note < threshold:
            return FAILURE
        return SUCCESS

try:
    from pylint import checkers
    from pylint.lint import PyLinter
    from pylint.__pkginfo__ import version as pylint_version
    from pylint.interfaces import IReporter
    register('checker', PyLintChecker)

    class MyLintReporter(object):
        """a partial pylint writer (implements only the message method, not
        methods necessary to display layouts
        """
        __implements__ = IReporter

        def __init__(self, writer, basepath, categories):
            self.writer = writer
            self.categories = set(categories)
            self._to_remove = len(basepath) + 1 # +1 for the leading "/"

        def add_message(self, msg_id, location, msg):
            """ manage message of different type and in the context of path """
            if not msg_id[0] in self.categories:
                return
            path, line = location[0], location[-1]
            path = path[self._to_remove:]
            if msg_id[0] == 'I':
                self.writer.info(msg, path=path, line=line)
            elif msg_id[0]  == 'E':
                self.writer.error(msg, path=path, line=line)
            elif msg_id[0] == 'F':
                self.writer.fatal(msg, path=path, line=line)
            else: # msg_id[0] in ('R', 'C', 'W')
                self.writer.warning(msg, path=path, line=line)

        def display_results(self, layout):
            pass
except ImportError, e:
    warn("unable to import pylint. Pylint checker disabled : %s" % e)


class PyCoverageChecker(BaseChecker):
    """check the tests coverage of a python package

    if used, it must be after the pyunit checker

    When devtools is available, test will be launched in a coverage mode. This
    test will gather coverage information, and will succeed if the test coverage
    is superior to a given threshold. *This checker must be executed after the
    python_unittest checker.
    """

    id = 'pycoverage'
    options_def = {
        'coverage.threshold': {
            'type': 'int', 'default': 80,
            'help': ('integer between 1 and 100 telling expected percent coverage '
                     'to pass this check. Default to 80.'),
            },
        'coverage_data': {
            'required': True,
            'help': ('integer between 1 and 100 telling expected percent coverage '
                     'to pass this check. Default to 80.'),
            },
        }

    def version_info(self):
        self.record_version_info('devtools', devtools_version)

    def do_check(self, test):
        """run the checker against <path> (usually a directory)"""
        self.threshold = self.options.get('coverage.threshold')
        assert self.threshold, 'no threshold defined'
        # XXX check the pyunit check is executed before (with coverage
        # activated) ?
        coverage_file = self.options.get('coverage_data')
        if not exists(coverage_file):
            self.writer.fatal('no coverage information', path=coverage_file)
            return NODATA
        directory, fname = split(coverage_file)
        with pushd(directory):
            percent = self._get_cover_info(fname, pyinstall_path(test))
        if percent < self.threshold:
            return FAILURE
        return SUCCESS

    def _get_cover_info(self, fname, inst_path):
        covertool = coverage.Coverage()
        covertool.cache_default = fname
        covertool.restore()
        stats = covertool.report_stat(inst_path, ignore_errors=1)
        percent = stats[coverage.TOTAL_ENTRY][2]
        self.writer.raw('coverage', '%.3f' % (percent, ), 'result')
        result = []
        for name in stats.keys():
            if name == coverage.TOTAL_ENTRY:
                continue
            nb_stmts, nb_exec_stmts, pc, pc_missing, readable = stats[name]
            if pc == 100:
                continue
            result.append( (pc_missing, name, pc, readable) )
        result.sort()
        for _, name, pc_cover, readable in result:
            msg = '%d %% covered, missing %s' % (pc_cover, readable)
            if pc_cover < ( self.threshold / 2):
                self.writer.error(msg, path=name)
            elif pc_cover < self.threshold:
                self.writer.warning(msg, path=name)
            else:
                self.writer.info(msg, path=name)
        return percent

if coverage is not None:
    register('checker', PyCoverageChecker)


class PyCheckerOutputParser(SimpleOutputParser):
    non_zero_status_code = FAILURE
    def parse_line(self, line):
        try:
            path, line, msg = line.split(':')
            self.writer.error(msg, path=path, line=line)
            self.status = FAILURE
        except ValueError:
            self.unparsed.append(line)

class PyCheckerChecker(BaseChecker):
    """check that unit tests of a python package succeed

    spawn unittest and parse output (expect a standard TextTestRunner)
    """

    id = 'pychecker'
    need_preprocessor = 'install'

    def do_check(self, test):
        """run the checker against <path> (usually a directory)"""
        command = ['pychecker', '-Qqe', 'Style']
        command += get_module_files(pyinstall_path(test))
        return ParsedCommand(self.writer, command, parsercls=PyCheckerOutputParser).run()

    def version_info(self):
        self.record_version_info('pychecker', getoutput("pychecker --version").strip())

register('checker', PyCheckerChecker)
