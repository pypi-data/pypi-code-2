from quant.dom.testunit import TestCase
import unittest
import datetime

def suite():
    suites = [
        unittest.makeSuite(TestModel),
    ]
    return unittest.TestSuite(suites)

class TestModel(TestCase):

    observationTime = datetime.datetime(2010, 1, 1)

    def setUp(self):
        self.model = self.registry.models.read(title='WTI (Mock)')
        self.image = self.model.images.read(observationTime=self.observationTime)

    def test_model(self):
        self.assertTrue(self.model)
        self.assertTrue(self.image)


