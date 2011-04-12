# Copyright (c) 2004-2005 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: test_validator.py 236779 2011-04-01 05:51:02Z nilo $

from Products.ATCountryWidget.validators import CountryValidator
from Products.validation.interfaces import ivalidator
import unittest

class ValidatorTests(unittest.TestCase):

    def test_interface(self):
        self.failUnless(ivalidator.isImplementedByInstancesOf(CountryValidator))
    
    def test_validation(self):
        good1 = 'DE'
        good2 = 'US'
        good3 = ''
        bad1 = 'ZZ'
        bad2 = 'XJ'
        bad3 = 'De'
        bad4 = 'uS'
        
        good = [good1, good2, good3]
        bad = [bad1, bad2, bad3, bad4]
        
        validator = CountryValidator('isValidISOCountry')

        for goodval in good:
            self.assertEqual(validator(goodval), 1)
            
        for badval in bad:
            self.assertNotEqual(validator(badval), 1)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ValidatorTests))
    return suite
