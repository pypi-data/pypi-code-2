"""
  >>> grok(__name__)
  >>> root = getSite()

  >>> context = root['test'] = Location()
  >>> request = TestRequest()

  >>> someview = GenericView(context, request)
  >>> rootmenu = RootMenu(context, request, someview)

  >>> from zope.security.testing import Principal, Participation
  >>> from zope.security.management import newInteraction, endInteraction

  >>> participation = Participation(Principal('zope.anybody'))
  >>> newInteraction(participation)

  >>> rootmenu.update()
  >>> rootmenu.viewlets
  [<MenuEntry `somerootentry` for menu `rootmenu`>]

  >>> print rootmenu.render()
  <dl id="rootmenu" class="menu">
    <dt>My Root Menu</dt>
    <dd>
      <ul>
        <li class="entry">
          <a alt="" href="http://127.0.0.1/somerootentry"
                    title="somerootentry">somerootentry</a>
        </li>
      </ul>
    </dd>
  </dl>

  >>> endInteraction()

"""

from grokcore.component.testing import grok
from zope.location.location import Location
from grokcore import view
from dolmen.menu import menuentry, Menu
from zope.interface import Interface
from zope.site.hooks import getSite
from zope.publisher.browser import TestRequest
from zope.site.interfaces import IRootFolder

view.context(Interface)


class GenericView(view.View):
    view.context(Interface)

    def render(self):
        return u"Nothing to see here"


class RootMenu(Menu):
    view.title('My Root Menu')
    view.context(Interface)

    def update(self):
        self.setMenuContext(getSite())
        Menu.update(self)


@menuentry(RootMenu)
class SomeRootEntry(view.View):
    view.context(IRootFolder)
    
    def render(self):
        return u"A Root entry"


def test_suite():
    import unittest, doctest
    from dolmen.menu import tests

    suite = unittest.TestSuite()
    mytest = doctest.DocTestSuite(
        setUp=tests.siteSetUp, tearDown=tests.siteTearDown,
        optionflags=(doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS))
    mytest.layer = tests.DolmenMenuLayer(tests)
    suite.addTest(mytest)
    return suite
