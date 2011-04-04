import unittest
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite

from collective.types.externalsearch.tests.base import TypesFunctionalTestCase

#Doctests relative to the main project directory
#(must contain file extension)
list_doctests = ['content/externalsearch.py',
                 'tests/external_search.txt',
                 ]
OPTIONFLAGS = []

def test_suite():
    return unittest.TestSuite(
        [Suite(filename,
               #optionflags=OPTIONFLAGS,
               package='collective.types.externalsearch',
               test_class=TypesFunctionalTestCase)
         for filename in list_doctests]
        )
