# -*- coding: utf-8 -*-

from django.utils import unittest

from issues import models


class TestIssue(unittest.TestCase):

    def test_get_title(self):
        issue = models.Issue()
        master = models.Issue()
        master.no = 2
        self.assertEqual(issue.get_title(), None)
        issue.title = u'foo'
        self.assertEqual(issue.get_title(), u'foo')
        issue.no = 1
        self.assertEqual(issue.get_title(), u'#1: foo')
        issue.master = master
        self.assertEqual(issue.get_title(), u'#1 (#2): foo')

    def test_set_title(self):
        i = models.Issue()
        self.assertRaises(AssertionError, i.set_title, 123)
        i.set_title('x' * 256)
        self.assertEqual(len(i.title), 255)

    def test_set_description(self):
        i = models.Issue()
        self.assertRaises(AssertionError, i.set_description, 123)
        i.set_description('x' * 5001)
        self.assertEqual(len(i.description), 5000)


if __name__ == '__main__':
    unittest.main()
