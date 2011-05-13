from ccy import currencydb, countryccy, set_new_country, CountryError, country_map
from ccy.basket.models import BasketGroup 

from django.test import TestCase


class CcyTest(TestCase):
        
    def testdefaultcountry(self):
        ccys = currencydb()
        for ccy in ccys.values():
            co = ccy.code[:2]
            cto = country_map(co)
            self.assertEqual(cto,ccy.default_country)
            
    def testiso(self):
        ccys = currencydb()
        iso = {}
        for ccy in ccys.values():
            self.assertFalse(ccy.isonumber in iso)
            iso[ccy.isonumber] = ccy
            
    def test2letters(self):
        ccys = currencydb()
        twol = {}
        for ccy in ccys.values():
            self.assertFalse(ccy.twolettercode in twol)
            twol[ccy.twolettercode] = ccy
            
    def testNewCountry(self):
        try:
            set_new_country('EU','EUR','Eurozone')
        except CountryError:
            return
        self.assertTrue(False)
        
    def testCountryCcy(self):
        self.assertEqual('AUD',countryccy('au'))
        self.assertEqual('EUR',countryccy('eu'))
        
    def testBasketLengthOthers(self):
        ccys = currencydb()
        b = BasketGroup(code = 'test')
        b.save()
        others = b.others()
        self.assertEqual(len(others),len(ccys))
        
    def testBasket1(self):
        ccys = currencydb()
        b = BasketGroup(code = 'test')
        b.save()
        b1 = b.add('europe','eur,chf,gbp')
        self.assertEqual(len(b1.ccys()),3)
        b2 = b.add('america','usd,cad')
        self.assertEqual(len(b2.ccys()),2)
        others = b.others()
        self.assertEqual(len(others),len(ccys)-5)
    
    def testBasket2(self):
        ccys = currencydb()
        b = BasketGroup(code = 'test')
        b.save()
        b1 = b.add('europe','eur,chf,gbp,sek,nok,eur,gbp')
        self.assertEqual(len(b1.ccys()),5)
        others = b.others()
        self.assertEqual(len(others),len(ccys)-5)