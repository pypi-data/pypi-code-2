# Copyright (c) 2004-2005 gocept. All rights reserved.
# See also LICENSE.txt
# $Id: test_util.py 236779 2011-04-01 05:51:02Z nilo $

import unittest

from Products.ATCountryWidget import config
from Products.ATCountryWidget.CountryTool import CountryUtils, Country, Area
from Products.ATCountryWidget.Interfaces import ICountry, IArea, ICountryUtils

class CountryClassTest(unittest.TestCase):

    interfaces_to_test = [(ICountry, Country),
                          (IArea, Area),
                          (ICountryUtils, CountryUtils),
                          ]

    def test_interface(self):
        failed = []
        for i, c in self.interfaces_to_test:
            self.failUnless(i.isImplementedByInstancesOf(c),
                            "%r is not implemented by %r" % (i,c))
            methlist = i.namesAndDescriptions(all=True)
            for meth in methlist:
                if not hasattr(c, meth[0]):
                    failed.append('Method %r not implemented by %s' % (
                        meth[0], c))
        self.assertEquals(failed, [], 'Interface tests failed:\n%s' % (
            '\n'.join(failed), ))
       
    def test_methods(self):
        country1 = Country('DE')
        country2 = Country('DE', 'Germany')
        country3 = Country('US')
        # test __eq__
        self.assertEqual(country1, country2)
        self.assertNotEqual(country1, country3)
        self.assertNotEqual(country3, 'bla')
        self.assertNotEqual(country3, None)
        # test __str__
        self.assertEqual(str(country1), '')
        self.assertEqual(str(country2), 'Germany')

class AreaClassTest(unittest.TestCase):

    def test_methods(self):
        area1 = Area('aEine Area')
        area2 = Area('bEine andere Area')
        area3 = Area('bEine andere Area')
        country = Country('DE','Germany')
        country2 = Country('AT','Austria')
        # test __cmp__
        arealist = [area2, 'string', area1]
        arealist.sort()
        self.assertEqual(arealist, [area1, area2, 'string'])
        # test __str__
        self.assertEqual(str(area1), 'aEine Area')
        # test add & del country        
        self.assertRaises(TypeError, area1.addCountry, None)
        self.assertRaises(TypeError, area1.addCountry, 'fakecountry')
        self.assertEqual(len(area1.countries), 0)
        self.failIf(area1.addCountry(country))
        self.assertEqual(len(area1.countries), 1)
        self.failIf(area1.delCountry(country))
        self.assertEqual(len(area1.countries), 0)
        self.assertRaises(ValueError, area1.delCountry, country2)
        self.assertRaises(ValueError, area1.delCountry, 'nix')
                
class CountryUtilTest(unittest.TestCase):

    def test_byiso(self):
        util = CountryUtils()
        self.assertEquals(util.getCountryByIsoCode('asdf').name, 'asdf')
        self.assertEquals(util.getCountryByIsoCode('DE').name,
            config.COUNTRIES['DE'])

    def test_getdict(self):
        util = CountryUtils()
        isodict = util.getCountryIsoDict()
        self.assert_(isodict is not config.COUNTRIES)
        self.assertEquals(len(isodict.keys()),
            len(config.COUNTRIES.keys()))
        
    def test_getlist(self):
        util = CountryUtils()
        cclist_keys = util.getCountryIsoDict().keys()
        cclist_values = util.getCountryIsoDict().values()
        cclist = zip(cclist_values, cclist_keys)
        cclist2 = list(util.getCountryIsoList())
        cclist.sort()
        cclist = [(x[1], x[0]) for x in cclist]
        # cclist2 must be sorted by value not by key
        self.assertEquals(cclist, cclist2)
        self.failUnless(isinstance(cclist[0], tuple))
        self.assertEqual(2, len(cclist[0]))
        self.assertEquals(len(cclist), len(config.COUNTRIES.keys()))
 
    def test_addCountry(self):
        # add custom country
        util = CountryUtils()
        a1 = ('A1', 'Custom Country 1')
        a2 = ('A2', 'Custom Country 2')
        cclist = util.getCountryIsoList()
        self.assert_(a1 not in cclist)
        self.assert_(a2 not in cclist)
        util.manage_countries_addCountry(*a1)
        util.manage_countries_addCountry(*a2)
        cclist = util.getCountryIsoList()
        self.assert_(a1 in cclist)
        self.assert_(a2 in cclist)
        self.assertEquals(a1[1], util.getCountryByIsoCode(a1[0]).name)
        self.assertEquals(a2[1], util.getCountryByIsoCode(a2[0]).name)
 
    def test_arealist(self):
        util = CountryUtils()
        util.manage_countries_addArea('Germauch')
        util.manage_countries_addArea('America')
        util.manage_countries_addCountryToArea('Germauch', ['DE', 'AT', 'CH'])
        util.manage_countries_addCountryToArea('America', ['US', 'CA'])
        area_list = util.listAreas()
        self.assertEquals(len(area_list), 2)
        self.assertEquals(area_list[0].name, 'Germauch')
        self.assertEquals(len(area_list[0].countries), 3)

        # test filter
        area_list = util.listAreas(['DE', 'AT'])
        self.assertEquals(len(area_list), 1)
        self.assertEquals(area_list[0].name, 'Germauch')
        self.assertEquals(len(area_list[0].countries), 2)

        # test omit
        area_list = util.listAreas(omit=['AT', 'US', 'CA'])
        self.assertEquals(len(area_list), 1)
        self.assertEquals(area_list[0].name, 'Germauch')
        self.assertEquals(len(area_list[0].countries), 2)


    def test_removearea(self):
        util = CountryUtils()
        self.assertEquals(len(util.listAreas()), 0)
        util.manage_countries_addArea('Ger & Au')
        self.assertEquals(len(util.listAreas()), 1)
        util.manage_countries_deleteArea('Ger & Au')
        self.assertEquals(len(util.listAreas()), 0)

    def test_sortarea(self):
        util = CountryUtils()
        util.manage_countries_addArea('Germauch')
        util.manage_countries_addCountryToArea('Germauch', ['DE', 'AT', 'CH'])
        util.manage_countries_sortArea('Germauch')
        a = util.listAreas()[0]
        self.assertEquals(a.name, 'Germauch')
        self.assertEquals(len(a.countries), 3)
        self.assertEquals(a.countries[0].isocc, 'AT')
        self.assertEquals(a.countries[1].isocc, 'DE')
        self.assertEquals(a.countries[2].isocc, 'CH')


    
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CountryUtilTest))
    suite.addTest(unittest.makeSuite(CountryClassTest))
    suite.addTest(unittest.makeSuite(AreaClassTest))
    return suite
