import unittest

from pkg_resources import resource_listdir
from zope.testing import doctest
from zope.app.testing.functional import HTTPCaller
from five.grok.testing import GrokFunctionalLayer
from Testing.ZopeTestCase.zopedoctest.functional import getRootFolder, sync
from Testing.ZopeTestCase import FunctionalDocTestSuite

from Testing.ZopeTestCase import installProduct
installProduct('PageTemplates')

import Zope2 ; Zope2.startup()

def http_call(method, path, data=None, **kw):
    """Function to help make RESTful calls.

    method - HTTP method to use
    path - testbrowser style path
    data - (body) data to submit
    kw - any request parameters
    """

    if path.startswith('http://localhost'):
        path = path[len('http://localhost'):]
    request_string = '%s %s HTTP/1.1\n' % (method, path)
    for key, value in kw.items():
        request_string += '%s: %s\n' % (key, value)
    if data is not None:
        request_string += '\r\n'
        request_string += data
    return HTTPCaller()(request_string, handle_errors=False)


def suiteFromPackage(name):
    files = resource_listdir(__name__, name)
    suite = unittest.TestSuite()
    for filename in files:
        if not filename.endswith('.py'):
            continue
        if filename == '__init__.py':
            continue
        if filename[0] in ('.', '#'):
            # Some editor create temporary files which can be
            # annoying.
            continue

        dottedname = 'five.grok.ftests.%s.%s' % (name, filename[:-3])
        test = FunctionalDocTestSuite(
            dottedname,
            extraglobs=dict(http=HTTPCaller(),
                            http_call=http_call,
                            getRootFolder=getRootFolder,
                            sync=sync),
            optionflags=(doctest.ELLIPSIS+
                         doctest.NORMALIZE_WHITESPACE+
                         doctest.REPORT_NDIFF))
        test.layer = GrokFunctionalLayer

        suite.addTest(test)
    return suite


def test_suite():
    suite = unittest.TestSuite()
    for name in ['directoryresource', 'view', 'viewlet','form', 'site']:
        suite.addTest(suiteFromPackage(name))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
