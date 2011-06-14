# -*- coding: utf-8 -*-

import dolmen.content
from dolmen.content import testing
from zope.interface import Interface
from zope.schema import Choice
from zope.testing.cleanup import cleanUp


class IViking(Interface):
    """Defines a Norseman
    """
    rank = Choice(
        title=u"Rank of the viking warrior",
        default=u"Jarl",
        values=[u"Bondi", u"Hersir", u"Jarl", u"Einherjar"])


class Ynglingar(dolmen.content.Content):
    dolmen.content.schema(IViking)


class JomsWarrior(dolmen.content.Content):
    dolmen.content.schema(IViking)
    rank = u"Bondi"


def setup_module(module):
    """ grok the publish module
    """
    testing.grok(
        "dolmen.content.meta",
        "dolmen.content.tests.schema.test_preserve")


def teardown_module(module):
    """ undo groking
    """
    cleanUp()


def test_preserve():
    """
    A `dolmen.content` content type can provide values described in the
    schema at the class level. These values are thus preserved::
    """
    harfagri = Ynglingar()
    assert harfagri.rank == u'Jarl'

    gormsson = JomsWarrior()
    assert gormsson.rank == u'Bondi'
