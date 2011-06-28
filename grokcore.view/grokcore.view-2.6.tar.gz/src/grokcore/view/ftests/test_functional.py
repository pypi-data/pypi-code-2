import re
import unittest
import os.path
import grokcore.view

from pkg_resources import resource_listdir

from zope.app.wsgi.testlayer import BrowserLayer, http
from zope.testing import doctest, renormalizing


FunctionalLayer = BrowserLayer(grokcore.view)

checker = renormalizing.RENormalizing([
    # Accommodate to exception wrapping in newer versions of mechanize
    (re.compile(r'httperror_seek_wrapper:', re.M), 'HTTPError:'),
    ])

def suiteFromPackage(name):
    files = resource_listdir(__name__, name)
    suite = unittest.TestSuite()
    getRootFolder = FunctionalLayer.getRootFolder
    for filename in files:
        if not filename.endswith('.py'):
            continue
        if filename == '__init__.py':
            continue

        dottedname = 'grokcore.view.ftests.%s.%s' % (name, filename[:-3])
        test = doctest.DocTestSuite(
            dottedname,
            checker=checker,
            extraglobs=dict(http=http,
                            getRootFolder=getRootFolder,
                            ),
            optionflags=(doctest.ELLIPSIS+
                         doctest.NORMALIZE_WHITESPACE+
                         doctest.REPORT_NDIFF),
            )
        test.layer = FunctionalLayer

        suite.addTest(test)
    return suite

def test_suite():
    suite = unittest.TestSuite()
    for name in [
        'contentprovider',
        'directoryresource',
        'staticdir',
        'url',
        'view',
        ]:
        suite.addTest(suiteFromPackage(name))
    return suite
