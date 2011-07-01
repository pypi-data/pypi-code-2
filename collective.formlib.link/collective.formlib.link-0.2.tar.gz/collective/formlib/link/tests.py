import zope.testing
import unittest

OPTIONFLAGS = (zope.testing.doctest.ELLIPSIS |
               zope.testing.doctest.NORMALIZE_WHITESPACE)

import zope.component.testing

def test_suite():
    modules = (
        'collective.formlib.link.field',
        'collective.formlib.link.utils')
    
    return unittest.TestSuite(
        [zope.testing.doctest.DocTestSuite(
                module,
                setUp=zope.component.testing.setUp,
                tearDown=zope.component.testing.tearDown,
                optionflags=OPTIONFLAGS) for module in modules]
         )

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
