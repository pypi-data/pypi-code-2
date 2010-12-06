import pep8
import py, pytest

__version__ = '0.6'

def pytest_addoption(parser):
    group = parser.getgroup("general")
    group.addoption('--pep8', action='store_true',
        help="perform some pep8 sanity checks on .py files")
    parser.addini("pep8options", type="args",
        help="enable/disable warnings/errors: e.g. +W293 and -W293")

def pytest_collect_file(path, parent):
    if parent.config.option.pep8 and path.ext == '.py':
        return Pep8Item(path, parent)

def pytest_configure(config):
    if config.option.pep8:
        # defaults taken from MoinMoin + own
        pep8ignores = set("E202,E221,E222,E241,E301,E302,E401,E501,"
            "E701,W391,W601,W602,W293".split(","))
        for opt in config.getini("pep8options"):
            if opt[0] == "-":
                pep8ignores.add(opt[1:])
            else:
                if opt[0] == "+":
                    opt = opt[1:]
                try:
                    pep8ignores.remove(opt)
                except KeyError:
                    pass
        config._pep8ignores = pep8ignores

def pytest_report_header(config):
    pep8ignores = getattr(config, '_pep8ignores', None)
    if pep8ignores:
        return "pep8 ignore opts: %s" %(" ".join(sorted(pep8ignores)))

class Pep8Error(Exception):
    """ indicates an error during pep8 checks. """

class Pep8Item(pytest.Item, pytest.File):
    def __init__(self, path, parent):
        super(Pep8Item, self).__init__(path, parent)
        self.keywords['pep8'] = True

    def runtest(self):
        call = py.io.StdCapture.call
        pep8ignores = self.config._pep8ignores
        found_errors, out, err = call(check_file, self.fspath, pep8ignores)
        if found_errors:
            raise Pep8Error(out, err)

    def repr_failure(self, excinfo):
        if excinfo.errisinstance(Pep8Error):
            return excinfo.value.args[0]
        return super(Pep8Item, self).repr_failure(excinfo)

    def reportinfo(self):
        return (self.fspath, -1, "PEP8-check")

def check_file(path, pep8ignores):
    pep8.process_options(['pep8',
        # ignore list taken from moin
        '--ignore=%s' % (",".join(pep8ignores)),
        '--show-source',
        '--repeat',
        'dummy file',
        ])
    checker = PyTestChecker(str(path))
    #XXX: bails out on death
    error_count = checker.check_all()
    ignored = checker.ignored_errors
    return max(error_count - ignored, 0)

class PyTestChecker(pep8.Checker):
    ignored_errors = 0
    def report_error(self, line_number, offset, text, check):
        # XXX hack
        if pep8.ignore_code(text[:4]):
            self.ignored_errors += 1
        pep8.Checker.report_error(self, line_number, offset, text, check)
