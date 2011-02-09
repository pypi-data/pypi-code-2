import re
from zope.testing import module, renormalizing
from zope.app.testing.functional import FunctionalTestSetup
from z3c.testsetup import register_all_tests
from megrok.login.tests import FunctionalLayer

checker = renormalizing.RENormalizing([
    # Relevant normalizers from zope.testing.testrunner.tests:
    (re.compile(r'\d+[.]\d\d\d seconds'), 'N.NNN seconds'),
    # Our own one to work around
    # http://reinout.vanrees.org/weblog/2009/07/16/invisible-test-diff.html:
    (re.compile(r'.*1034h'), ''),
    (re.compile(r'httperror_seek_wrapper:'), 'HTTPError:' )
    ])

def setUp(test):
    if test.filename.endswith('.txt'):
        module.setUp(test, '__main__')
    FunctionalTestSetup().setUp()
    
def tearDown(test):
    FunctionalTestSetup().tearDown()
    if test.filename.endswith('.txt'):
        module.tearDown(test)

test_suite = register_all_tests('megrok.login', layer=FunctionalLayer,
                                fextensions=['.txt', '.py'],
                                fsetup=setUp,
                                fteardown=tearDown,
                                checker=checker,
                                )
