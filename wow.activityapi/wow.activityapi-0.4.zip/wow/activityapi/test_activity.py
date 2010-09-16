# -*- coding: utf-8 -*-
"""
Doctest runner for 'activity_api'
"""
__docformat__ = 'restructuredtext'

import unittest
import doctest

optionflags =  (doctest.ELLIPSIS |
                doctest.NORMALIZE_WHITESPACE |
                doctest.REPORT_ONLY_FIRST_FAILURE)

def setUp(test):
    pass

def test_suite():
    suite = unittest.TestSuite((
            doctest.DocFileSuite(
                'README.txt',
                setUp=setUp,
                optionflags=optionflags,
                ),
            ))
    return suite

def mocked_get_activity(self, name, realm, zone, count):

    activity = [u'Earned the achievement [Neck-Deep in Vile (10 player)].',
                u'Has now completed [Victories over the Lich King (Icecrown 10 player)] 4 times.',
                u'Has now completed [Sindragosa kills (Heroic Icecrown 10 player)] 2 times.',
                u'Has now completed [Valithria Dreamwalker rescues (Heroic Icecrown 10 player)] 4 times.',
                u'Has now completed [Blood Queen Lanathel kills (Heroic Icecrown 10 player)] 6 times.']

    return activity

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
