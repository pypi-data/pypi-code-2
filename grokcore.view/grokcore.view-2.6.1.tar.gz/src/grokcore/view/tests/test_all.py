import re
import unittest
from pkg_resources import resource_listdir
from zope.testing import doctest, cleanup, renormalizing
import zope.component.eventtesting
from grokcore.view.templatereg import file_template_registry

optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS

def setUp(test):
    zope.component.eventtesting.setUp(test)
    file_template_registry.ignore_templates('.svn')

def cleanUp(test):
    cleanup.cleanUp()

checker = renormalizing.RENormalizing([
    # str(Exception) has changed from Python 2.4 to 2.5 (due to
    # Exception now being a new-style class).  This changes the way
    # exceptions appear in traceback printouts.
    (re.compile(r"ConfigurationExecutionError: <class '([\w.]+)'>:"),
                r'ConfigurationExecutionError: \1:'),
    ])

def suiteFromPackage(name):
    files = resource_listdir(__name__, name)
    suite = unittest.TestSuite()
    for filename in files:
        if not filename.endswith('.py'):
            continue
        if filename.endswith('_fixture.py'):
            continue
        if filename == '__init__.py':
            continue
        dottedname = 'grokcore.view.tests.%s.%s' % (name, filename[:-3])
        test = doctest.DocTestSuite(
            dottedname,
            setUp=setUp,
            tearDown=cleanUp,
            checker=checker,
            optionflags=optionflags)
        suite.addTest(test)
    return suite

def test_suite():
    suite = unittest.TestSuite()
    for name in [
        'contentprovider',
        'directoryresource',
        'skin',
        'template',
        'view',
        ]:
        suite.addTest(suiteFromPackage(name))
    suite.addTest(doctest.DocFileSuite(
        '../templatereg.txt',
        optionflags=optionflags,
        setUp=setUp,
        tearDown=cleanUp,
        ))
    return suite
