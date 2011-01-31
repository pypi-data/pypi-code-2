"""
  >>> grok(__name__)
  >>> root = getSite()

  >>> context = root['test'] = Location()
  >>> request = TestRequest()

  >>> current_view = GlobalView(context, request)
  >>> current_view
  <dolmen.menu.tests.test_directives.GlobalView object at ...>

  >>> navigation = NavigationMenu(context, request, current_view)

  >>> from zope.security.testing import Principal, Participation
  >>> from zope.security.management import newInteraction, endInteraction

  >>> participation = Participation(Principal('zope.anybody'))
  >>> newInteraction(participation)

  >>> navigation.update()
  >>> navigation.viewlets
  [<MenuEntry `a_direct_entry` for menu `navigationmenu`>,
   <MenuEntry `anotherview` for menu `navigationmenu`>]

  >>> print navigation.render()
  <dl id="navigationmenu" class="menu">
    <dt>My nice menu</dt>
      <dd>
        <ul>
          <li class="entry">
    	    <a href="http://127.0.0.1/test/a_direct_entry"
               title="My Entry">My Entry</a>
          </li>
          <li class="entry">
            <a alt="" href="http://127.0.0.1/test/anotherview"
               title="anotherview">anotherview</a>
         </li>
      </ul>
    </dd>
  </dl>

  >>> endInteraction()
"""
from grokcore.component.testing import grok
from zope.location.location import Location
from grokcore import view, security, viewlet
from dolmen.menu import global_menuentry, menu, Menu, Entry
from zope.interface import Interface
from zope.site.hooks import getSite
from zope.publisher.browser import TestRequest 

view.context(Interface)

class NavigationMenu(Menu):
    view.title('My nice menu')


class GlobalView(view.View):
    def render(self):
        return u"I'm a view"


class AnotherView(view.View):
    def render(self):
        return u"I'm a view and I want to be a menu entry"


class MyMenuEntry(Entry):
    viewlet.order(1)
    viewlet.name('a_direct_entry')
    viewlet.title('My Entry')
    menu(NavigationMenu)


global_menuentry(AnotherView, NavigationMenu, order=2)


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
