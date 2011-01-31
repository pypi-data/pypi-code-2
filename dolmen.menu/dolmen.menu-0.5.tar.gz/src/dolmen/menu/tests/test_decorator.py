"""
  >>> grok(__name__)
  >>> root = getSite()

  >>> context = root['test'] = Location()
  >>> request = TestRequest()

  >>> someview = SomeView(context, request)
  >>> someview
  <dolmen.menu.tests.test_decorator.SomeView object at ...>

  >>> mymenu = MyMenu(context, request, someview)

  >>> from zope.security.testing import Principal, Participation
  >>> from zope.security.management import newInteraction, endInteraction

  >>> participation = Participation(Principal('zope.anybody'))
  >>> newInteraction(participation)

  >>> mymenu.update()
  >>> mymenu.viewlets
  [<MenuEntry `entrywithdetails` for menu `mymenu`>,
   <MenuEntry `testentry` for menu `mymenu`>,
   <FactoryGeneratedEntry `an_entry` for menu `mymenu`>]

  >>> print mymenu.render()
  <dl id="mymenu" class="menu">
    <dt>My nice menu</dt>
    <dd>
      <ul>
        <li class="entry">
          <a alt="This is a nice view."
             href="http://127.0.0.1/test/entrywithdetails"
             title="Nice view">Nice view</a>
        </li>
        <li class="entry">
    	  <a alt="" href="http://127.0.0.1/test/testentry"
    	     title="testentry">testentry</a>
    	</li>
        <li class="entry">
          <a href="http://dolmen-project.org"
             title="Dolmen link">Dolmen link</a>
        </li>
      </ul>
    </dd>
  </dl>

Using a user with the appropriate rights, we now have both the items::

  >>> endInteraction()
  >>> participation = Participation(Principal('zope.user'))
  >>> newInteraction(participation)

  >>> mymenu.update()
  >>> mymenu.viewlets
  [<MenuEntry `entrywithdetails` for menu `mymenu`>,
   <MenuEntry `protectedentry` for menu `mymenu`>,
   <MenuEntry `testentry` for menu `mymenu`>,
   <FactoryGeneratedEntry `an_entry` for menu `mymenu`>]

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
 

class SomeView(view.View):
    def render(self):
        return u"I'm a simple view"


class MyPerm(security.Permission):
    security.name('menu.Display')


@menuentry(MyMenu)
class TestEntry(view.View):
    def render(self):
        return u"A simple entry"


@menuentry(MyMenu)
class ProtectedEntry(view.View):
    view.require('zope.ManageContent')

    def render(self):
        return "I'm a restricted view"


@menuentry(MyMenu, title='Nice view', description='This is a nice view.')
class EntryWithDetails(view.View):
    def render(self):
        return u"A simple entry"


class MyEntry(object):
    """A very basic entry.
    """
    def __init__(self, menu, id, title, url, desc=u"", perm='zope.View'):
        self.__name__ = id
        self.permission = perm
        self.title = title
        self.description = desc
        self.url = url
        self.menu = menu

    def __repr__(self):
        return "<FactoryGeneratedEntry `%s` for menu `%s`>" % (
            self.__name__, self.menu.__name__)

    def render(self):
        return """<a href="%s" title="%s">%s</a>""" % (
            self.url, self.title, self.title)


@menuentry(MyMenu)
def manual_entry(context, request, view, menu):
   return MyEntry(menu, 'an_entry', 'Dolmen link',
                  url="http://dolmen-project.org")


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
