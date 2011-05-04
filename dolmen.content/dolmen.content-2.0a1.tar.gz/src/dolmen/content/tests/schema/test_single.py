# -*- coding: utf-8 -*-
"""Test single schema declaration.
"""

import dolmen.content as dolmen
from dolmen.content import testing
from zope.interface import Interface
from zope.schema import TextLine, Int
from zope.testing.cleanup import cleanUp


def setup_module(module):
    testing.grok(
        "dolmen.content.meta",
        "dolmen.content.tests.schema.test_single")


def teardown_module(module):
    cleanUp()


class IBarbarian(Interface):
    """A barbarian. Usually only wearing a leather underpants.
    """
    kills = Int(
        title=u"Kills !",
        default=100)

    nickname = TextLine(
        title=u"Nickname",
        default=u"The Barbarian")


class Barbarian(dolmen.Content):
    """A barbaric content.
    """
    dolmen.name('male')
    dolmen.schema(IBarbarian)


def test_unique_schema():
    conan = Barbarian()
    assert IBarbarian.providedBy(conan)
    assert dolmen.IContent.providedBy(conan)
    assert conan.nickname == u'The Barbarian'
    assert conan.kills == 100
