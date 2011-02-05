import dm.times
import unittest
import os

def suite():
    suites = [
        unittest.makeSuite(TestTimeNow),
    ]
    return unittest.TestSuite(suites)


class TestTimeNow(unittest.TestCase):

    def testGetLocalNow(self):
        timeNow = dm.times.getLocalNow()
        self.failUnless(timeNow)
        self.failUnless(timeNow.ticks())
        self.failUnless(timeNow.year)
        
    def testGetLocalNowC(self):
        dm.times.getLocalNowC()
        
    def testGetLocalZoneName(self):
        refSeconds = dm.times.getLocalNow().ticks()
        dm.times.getLocalZoneName(refSeconds)
    
    def testGetLocalNowCWithZone(self):
        dm.times.getLocalNowCWithZone()
        
    def testResetTimezone(self):
        os.environ['TZ'] = 'Europe/Paris'
        dm.times.resetTimezone()
        dm.times.getLocalNowCWithZone()

