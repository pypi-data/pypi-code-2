from quant.dom.testunit import TestCase
import unittest
import datetime

def suite():
    suites = [
        unittest.makeSuite(TestResult),
    ]
    return unittest.TestSuite(suites)

class TestResult(TestCase):

    observationTime = datetime.datetime(2010, 1, 1)

    def setUp(self):
        self.model = self.registry.models.read(title='WTI (Mock)')
        self.image = self.model.images.read(observationTime=self.observationTime)
        self.book = self.registry.books.read(title='My Book')
        self.result = self.registry.results.create(book=self.book, image=self.image)

    def tearDown(self):
        self.result.delete()

    def test_result(self):
        self.assertTrue(self.result)
        self.assertTrue(len(self.result.lines))

