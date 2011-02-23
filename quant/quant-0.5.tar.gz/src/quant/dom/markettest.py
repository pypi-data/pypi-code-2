from quant.dom.testunit import TestCase
import unittest
import datetime

def suite():
    suites = [
        unittest.makeSuite(TestModel),
    ]
    return unittest.TestSuite(suites)

class TestModel(TestCase):

    now = datetime.datetime.now()
    thisYear = now.year
    thisMonth = now.month
    thisDay = now.day
    observationTime = datetime.datetime(thisYear, thisMonth, thisDay)

    def setUp(self):
        self.image = self.registry.images.read(observationTime=self.observationTime)

    def test_model(self):
        self.assertTrue(self.image)


