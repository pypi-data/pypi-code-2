import unittest
from quant.dom.testunit import TestCase
import datetime

def suite():
    suites = [
        unittest.makeSuite(BookTestCase)
    ]
    return unittest.TestSuite(suites)


class BookTestCase(TestCase):

    def setUp(self):
        self.book = self.registry.books.read(title="My Book")
        self.option1 = self.book.europeans.read(
            title="European call #1",
        )
        self.option2 = self.book.europeans.read(
            title="European put #2",
        )

    def test_book(self):
        self.assertTrue(self.book)
        self.assertTrue(self.option1)
        self.assertTrue(self.option2)
