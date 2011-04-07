import unittest2 as unittest
import doctest
from plone.testing import layered

from collective.layout.authpersonalbar.tests._testing import (
    COLLECTIVELAYOUTAUTHPERSONALBAR_INTEGRATION_TESTING,
    COLLECTIVELAYOUTAUTHPERSONALBAR_FUNCTIONAL_TESTING,
    optionflags
)

integration_tests = [
    'installation.txt',
]

functional_tests = [
    '../README.txt',
]


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(doctest.DocFileSuite('tests/%s' % file,\
                                 package='collective.layout.authpersonalbar',\
                                 optionflags=optionflags),
                layer=COLLECTIVELAYOUTAUTHPERSONALBAR_INTEGRATION_TESTING)
        for file in integration_tests
        ])
    suite.addTests([
        layered(doctest.DocFileSuite('tests/%s' % file,\
                                 package='collective.layout.authpersonalbar',\
                                 optionflags=optionflags),
                layer=COLLECTIVELAYOUTAUTHPERSONALBAR_FUNCTIONAL_TESTING)
        for file in functional_tests
        ])
    return suite
