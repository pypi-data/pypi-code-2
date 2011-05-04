# -*- coding: utf-8 -*-
"""
"""

import dolmen.content as dolmen
from dolmen.content import testing
from dolmen.content.interfaces import IFactory
from zope.interface import Interface, implements
from zope.component import getUtility, queryUtility
from zope.testing.cleanup import cleanUp


def setup_module(module):
    testing.grok(
        "dolmen.content.meta",
        "dolmen.content.tests.factory.test_custom_factory")


def teardown_module(module):
    cleanUp()


class IBread(Interface):
    pass


class BakerJoe(dolmen.Factory):
    dolmen.name('baker_joe')
    title = u"Joe's bakery"
    description = u"I am a totally custom factory."


class BakerSteve(dolmen.Factory):
    dolmen.name('baker_steve')
    title = u"Steve and Sons."


class Baguette(dolmen.Content):
    """A crusty bread.
    """
    dolmen.name(u'White fresh bread')
    dolmen.factory(BakerJoe)
    implements(IBread)


def test_custom_factory():
    joe = getUtility(IFactory, 'baker_joe')
    assert isinstance(joe, BakerJoe)

    assert joe.title == u"Joe's bakery"
    assert joe.description == u'I am a totally custom factory.'

    steve = queryUtility(IFactory, 'baker_steve')
    assert steve is None
