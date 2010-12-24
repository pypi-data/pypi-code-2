"""
  >>> grok(__name__)
  >>> root = getSite()

  >>> context = root['test'] = Location()
  >>> request = TestRequest()

  >>> someview = SomeView(context, request)
  >>> someview
  <dolmen.menu.tests.test_multidecorators.SomeView object at ...>

  >>> mymenu = MyMenu(context, request, someview)
  >>> anothermenu = AnotherMenu(context, request, someview)

  >>> from zope.security.testing import Principal, Participation
  >>> from zope.security.management import newInteraction, endInteraction

  >>> participation = Participation(Principal('zope.anybody'))
  >>> newInteraction(participation)

  >>> mymenu.update()
  >>> mymenu.viewlets
  [<MenuEntry `entrywithdetails` for menu `mymenu`>]
  
  >>> anothermenu.update()
  >>> anothermenu.viewlets
  [<MenuEntry `entrywithdetails` for menu `anothermenu`>]

  >>> print mymenu.render()
  <dl id="mymenu" class="menu">
    <dt>My nice menu</dt>
    <dd>
      <ul>
        <li class="entry">
          <a alt="" href="http://127.0.0.1/test/entrywithdetails"
             title="An entry with some details">An entry with some details</a>
        </li>
      </ul>
    </dd>
  </dl>

  >>> print anothermenu.render()
  <dl id="anothermenu" class="menu">
    <dt>My other menu</dt>
    <dd>
      <ul>
        <li class="entry">
          <a alt="" href="http://127.0.0.1/test/entrywithdetails"
             title="Alternate title">Alternate title</a>
        </li>
      </ul>
    </dd>
  </dl>

  >>> endInteraction()
"""
from grokcore.component.testing import grok
from zope.location.location import Location
from grokcore import view, security
from dolmen.menu import menuentry, Menu, Entry, IMenuEntry, IMenu
from zope.interface import Interface
from zope.site.hooks import getSite
from zope.publisher.browser import TestRequest 

view.context(Interface)


class MyMenu(Menu):
    view.title('My nice menu')

 
class AnotherMenu(Menu):
    view.title('My other menu')


class SomeView(view.View):
    def render(self):
        return u"I'm a simple view"


@menuentry(MyMenu)
@menuentry(AnotherMenu, title="Alternate title")
class EntryWithDetails(view.View):
    view.title("An entry with some details")
    def render(self):
        return u"A simple entry"


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
