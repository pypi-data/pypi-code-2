# Copyright (c) 2004-2005 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: test_widgets.py 236779 2011-04-01 05:51:02Z nilo $

# python imports
import unittest

# Zope imports
from AccessControl.SecurityManagement import newSecurityManager

# Plone imports
from Products.Archetypes.tests.ArchetypesTestCase import ArcheSiteTestCase

class WidgetTests(ArcheSiteTestCase):

    my_id = 'a_test_countrywidgetinstance'

    def afterSetUp(self):
        ArcheSiteTestCase.afterSetUp(self)
        user = self.getManagerUser()
        newSecurityManager(None, user)
 
    def addTestCountryWidget(self):
        my_id = self.my_id
        from TestWidget import TestCountryWidget
        site = self.getPortal()
        obj = TestCountryWidget(my_id)
        site._setObject(my_id, obj)
        obj = getattr(site, my_id)
        obj.initializeArchetype()
        res_obj = getattr(site, my_id)
        return res_obj
 
    def test_country_widget(self):
        site = self.getPortal()
        doc = self.addTestCountryWidget()
        field = doc.Schema()['country']
        widget = field.widget
        form = {'country':'DE'}
        expected = 'DE'
        result = widget.process_form(doc, field, form)
        self.assertEqual(expected, result[0])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(WidgetTests))
    return suite



# if __name__ == '__main__':
#     framework()
# else:
#     # While framework.py provides its own test_suite()
#     # method the testrunner utility does not.
#     import unittest
#     def test_suite():
#         suite = unittest.TestSuite()
#         suite.addTest(unittest.makeSuite(WidgetTests))
#         return suite
