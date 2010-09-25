import datetime
from unittest import TestCase

from ccy import period, date2juldate, juldate2date
from ccy import date2yyyymmdd, yyyymmdd2date
from ccy import date2timestamp, timestamp2date


class PeriodTests(TestCase):
    
    def testPeriod(self):
        a = period('5Y')
        self.assertEqual(a.years,5)
        b = period('1y3m')
        self.assertEqual(b.years,1)
        self.assertEqual(b.months,3)
        c = period('-3m')
        self.assertEqual(c.years,0)
        self.assertEqual(c.months,-3)
        
    def testAdd(self):
        a = period('4Y')
        b = period('1Y3M')
        c = a + b
        self.assertEqual(c.years,5)
        self.assertEqual(c.months,3)
        
    def testSubtract(self):
        a = period('4Y')
        b = period('1Y')
        c = a - b
        self.assertEqual(c.years,3)
        self.assertEqual(c.months,0)
        c = period('3Y') - period('1Y3M')
        self.assertEqual(c.years,1)
        self.assertEqual(c.months,9)
        self.assertEqual(str(c),'1Y9M')
        
    def testCompare(self):
        a = period('4Y')
        b = period('4Y')
        c = period('1Y2M')
        self.assertTrue(a==b)
        self.assertTrue(a>=b)
        self.assertTrue(a<=b)
        self.assertTrue(c<=a)
        self.assertTrue(c<a)
        self.assertFalse(c==a)
        self.assertFalse(c>=b)
        self.assertTrue(c>a-b)
    
    
class DateConverterTest(TestCase):
    
    def setUp(self):
        self.dates = [
                      (datetime.date(2010,6,11),40340,20100611,1276210800),
                      (datetime.date(2009,4,2), 39905,20090402,1238626800),
                      (datetime.date(1996,2,29),35124,19960229, 825552000),
                      (datetime.date(1970,1,1), 25569,19700101,         0),
                      (datetime.date(1900,1,1),1,19000101,           None)]
        
    def testdate2JulDate(self):
        for d,jd,y,ts in self.dates:
            self.assertEqual(jd,date2juldate(d))
    
    def testJulDate2Date(self):
        for d,jd,y,ts in self.dates:
            self.assertEqual(d,juldate2date(jd))
            
    def testDate2YyyyMmDd(self):
        for d,jd,y,ts in self.dates:
            self.assertEqual(y,date2yyyymmdd(d))
            
    def testYyyyMmDd2Date(self):
        for d,jd,y,ts in self.dates:
            self.assertEqual(d,yyyymmdd2date(y))
        
    #def testDate2Timestamp(self):
    #    for d,jd,y,ts in self.dates:
    #        if ts is not None:
    #            self.assertEqual(ts,date2timestamp(d))
            
    #def testTimestamp2Date(self):
    #    for d,jd,y,ts in self.dates:
    #        if ts is not None:
    #            self.assertEqual(d,timestamp2date(ts))
        