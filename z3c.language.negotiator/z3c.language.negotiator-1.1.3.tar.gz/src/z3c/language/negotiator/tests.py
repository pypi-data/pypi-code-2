##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

"""
$Id: tests.py 117125 2010-10-01 15:29:15Z adamg $
"""
__docformat__ = 'restructuredtext'

import unittest

import zope.component
from zope.testing import doctest
from zope.testing.doctestunit import DocFileSuite

from z3c.language.negotiator import app
from z3c.language.negotiator import testing


class NegotiatorBaseTest(testing.BaseTestINegotiator):

    def getTestClass(self):
        return app.Negotiator


class NegotiatorTest(zope.component.testing.PlacelessSetup,
    unittest.TestCase):

    def setUp(self):
        super(NegotiatorTest, self).setUp()
        self.negotiator = app.Negotiator()
        zope.component.provideAdapter(testing.LanguageSessionStub)

    def test_policy(self):
        default = 'session --> browser --> server'
        self.assertEqual(self.negotiator.policy, default)
        self.negotiator.policy = 'server'
        self.assertEqual(self.negotiator.policy, 'server')

    def test_serverLanguage(self):
        self.assertEqual(self.negotiator.serverLanguage, u'en')
        self.negotiator.serverLanguage = u'de'
        self.assertEqual(self.negotiator.serverLanguage, u'de')

    def test_offeredLanguages(self):
        self.assertEqual(self.negotiator.offeredLanguages, [])
        self.negotiator.offeredLanguages = [u'de', u'en']
        self.assertEqual(self.negotiator.offeredLanguages, [u'de', u'en'])

    def test_getLanguagesBrowser(self):
        # first set the default policy to 'browser'
        self.negotiator.policy = 'browser'
        self.assertEqual(self.negotiator.policy, 'browser')

        _cases = (
            (('en','de'), ('en','de','fr'),  'en'),
            (('en'),      ('it','de','fr'),  None),
            (('pt-br','de'), ('pt_BR','de','fr'),  'pt_BR'),
            (('pt-br','en'), ('pt', 'en', 'fr'),  'pt'),
            (('pt-br','en-us', 'de'), ('de', 'en', 'fr'),  'en'),
            )

        for user_pref_langs, obj_langs, expected in _cases:
            env = testing.EnvStub(user_pref_langs)
            self.assertEqual(self.negotiator.getLanguage(obj_langs, env),
                             expected)

    def test_getLanguagesServer(self):
        self.negotiator.policy = 'server'
        self.assertEqual(self.negotiator.policy, 'server')

        self.negotiator.serverLanguage = u'de'
        self.assertEqual(self.negotiator.serverLanguage, u'de')

        _cases = (
            (('en','de'), ('en','de','fr'),  'de'),
            (('en'),      ('it','de','fr'),  'de'),
            (('pt-br','de'), ('pt_BR','de','fr'),  'de'),
            (('pt-br','en'), ('pt', 'en', 'fr'),  'de'),
            (('pt-br','en-us', 'de'), ('de', 'en', 'fr'),  'de'),
            )

        for user_pref_langs, obj_langs, expected in _cases:
            env = testing.EnvStub(user_pref_langs)
            self.assertEqual(self.negotiator.getLanguage(obj_langs, env),
                             expected)

    def test_getLanguagesSession(self):
        self.negotiator.policy = 'session'
        self.assertEqual(self.negotiator.policy, 'session')

        _cases = (
            (('en','de'), ('en','de','fr'),  'fr'),
            (('en'),      ('it','de','fr'),  'fr'),
            (('pt-br','de'), ('pt_BR','de','fr'),  'fr'),
            (('pt-br','en'), ('pt', 'en', 'fr'),  'fr'),
            (('pt-br','en-us', 'de'), ('de', 'en', 'fr'),  'fr'),
            )

        for user_pref_langs, obj_langs, expected in _cases:
            env = testing.EnvStub(user_pref_langs)
            self.assertEqual(self.negotiator.getLanguage(obj_langs, env),
                             expected)

    def test_getLanguagesCached(self):
        self.negotiator.cacheEnabled = True

        self.negotiator.policy = 'server'
        self.assertEqual(self.negotiator.policy, 'server')

        self.negotiator.serverLanguage = u'de'

        env = testing.EnvStub(('pt-br','en'))
        self.assertEqual(self.negotiator.getLanguage(('en', 'de'), env), 'de')

        self.negotiator.serverLanguage = u'en'

        self.assertEqual(self.negotiator.getLanguage(('en', 'de'), env), 'en')

        env = testing.EnvStub(('pt-br','en'))

        self.assertEqual(self.negotiator.getLanguage(('en', 'de'), env), 'en')

        self.negotiator.serverLanguage = u'de'

        self.assertEqual(self.negotiator.getLanguage(('en', 'de'), env), 'de')

        self.negotiator.clearCache(env)

        self.assertEqual(self.negotiator.getLanguage(('en', 'de'), env), 'de')

        self.negotiator.clearCache(env)
        self.negotiator.clearCache(env)

        #edge case, cache has a more specific language than available
        self.negotiator.policy = 'browser'
        env = testing.EnvStub(('de-de','de'))

        self.assertEqual(self.negotiator.getLanguage(('de-de', 'de'), env), 'de-de')

        self.assertEqual(self.negotiator.getLanguage(('de', 'en'), env), 'de')

        self.negotiator.clearCache(env)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(NegotiatorBaseTest),
        unittest.makeSuite(NegotiatorTest),
        DocFileSuite('README.txt',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
