"""
No factories
============

Sometimes, it makes no sense to have factories for objects, for they are not
destined to be used as a content type. In these case, having a factory is
useless and confusing. Therefore, a nofactory directive allows you to
explicitly mark your component as non-eligible for an auto factory grokking,
even if a factory directive is set on the class.

  >>> from zope.component import queryUtility
  >>> factory = queryUtility(dolmen.IFactory, 'horror')
  >>> factory is None
  True

"""

import dolmen.content as dolmen
from zope.schema import Bool


class ISomethingThatShouldntBe(dolmen.IBaseContent):
    """A cyclopean, undescriptable and non euclidean horror.
    """
    sanity_failure = Bool(
        title=u"Seeing this makes you unsane.",
        default=True)


class SunkenTemple(dolmen.Factory):
    dolmen.name('horror')


class Nyarlathotep(dolmen.Content):
    """A crawling chaos
    """
    dolmen.name(u'Impossible to name.')
    dolmen.schema(ISomethingThatShouldntBe)
    dolmen.nofactory()
    dolmen.factory(SunkenTemple)
