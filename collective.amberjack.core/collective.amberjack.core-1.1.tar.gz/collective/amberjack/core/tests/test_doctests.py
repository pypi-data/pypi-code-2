from collective.amberjack.core.tests import zcml_template
from zope.app.testing import placelesssetup
from zope.testing.doctest import ELLIPSIS, NORMALIZE_WHITESPACE, \
    REPORT_ONLY_FIRST_FAILURE
from zope.testing.doctestunit import DocFileSuite
import unittest
     
def test_suite():
    
    return unittest.TestSuite((
            DocFileSuite('README.txt',
                         package='collective.amberjack.core',
                         optionflags=ELLIPSIS|REPORT_ONLY_FIRST_FAILURE|NORMALIZE_WHITESPACE,
                         globs = {'template': zcml_template},
                         setUp=placelesssetup.setUp,                                                  
                         tearDown=placelesssetup.tearDown,                                             
                         ),          
            ))