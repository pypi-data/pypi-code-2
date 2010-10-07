import doctest
import re
import zc.buildout.testing
from zope.testing import renormalizing


normalize_script = (
    re.compile('(\n?)-  ([a-zA-Z0-9_.-]+)-script.py\n-  \\2.exe\n'),
    '\\1-  \\2\n')

# Distribute does not result in a setuptools compattest binary, so filter that
# out.
normalize_setuptools = (
    re.compile('-  compattest-setuptools'),
    '')


def DocFileSuite(*args, **kw):
    def setUp(test):
        zc.buildout.testing.buildoutSetUp(test)
        zc.buildout.testing.install_develop('z3c.recipe.compattest', test)

        # need to explicitly name our dependencies for the buildout test
        # environment
        zc.buildout.testing.install('zc.recipe.testrunner', test)
        zc.buildout.testing.install('zc.recipe.egg', test)
        zc.buildout.testing.install('z3c.recipe.scripts', test)
        zc.buildout.testing.install('zope.testing', test)
        zc.buildout.testing.install('zope.testrunner', test)
        zc.buildout.testing.install('zope.interface', test)
        zc.buildout.testing.install('zope.exceptions', test)
        zc.buildout.testing.install('zope.dottedname', test)

    def tearDown(test):
        zc.buildout.testing.buildoutTearDown(test)

    kw['setUp'] = setUp
    kw['tearDown'] = tearDown
    kw['optionflags'] = (doctest.ELLIPSIS
                         | doctest.NORMALIZE_WHITESPACE)
    kw['checker'] = renormalizing.RENormalizing([
        zc.buildout.testing.normalize_path,
        normalize_script,
        normalize_setuptools,
        ])

    return doctest.DocFileSuite(*args, **kw)
