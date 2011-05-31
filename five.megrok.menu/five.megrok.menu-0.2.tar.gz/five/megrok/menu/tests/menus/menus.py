"""
  >>> grok.testing.grok(__name__)

For menu configuration, we have to start a new interaction:

  >>> from Products.Five.security import newInteraction
  >>> newInteraction()

  >>> from zope.component import getUtility, getUtilitiesFor
  >>> from zope.app.publisher.interfaces.browser import IBrowserMenu
  >>> from zope.publisher.browser import TestRequest

A menu is available as a named utility providing ``IBrowserMenu``.

  >>> menu = getUtility(IBrowserMenu, u'tabs')
  >>> manfred = Mammoth()
  >>> request = TestRequest()

In order to retrieve the menu items, we need to pass in a context
object and a request.  The menu then determines which menu items are
available for this particular object and the principal that's attached
to the request:

  >>> from pprint import pprint
  >>> pprint(menu.getMenuItems(manfred, request))
  [{'action': '/path/customcontext',
    'description': u'',
    'extra': None,
    'icon': None,
    'selected': u'',
    'submenu': None,
    'title': 'CustomContext'},
   {'action': 'edit',
    'description': u'',
    'extra': None,
    'icon': None,
    'selected': u'',
    'submenu': None,
    'title': 'Edit'},
   {'action': 'index',
    'description': u'',
    'extra': None,
    'icon': None,
    'selected': u'',
    'submenu': None,
    'title': 'View'}]

"""

from grokcore.component import Context
from five import grok
from five.grok import testing
from five.megrok import menu
import grokcore.security


class Mammoth(Context):
    pass


class Smilodon(Context):
    pass


class Tabs(menu.Menu):
    grok.name('tabs')
    grok.title('Tabs')
    grok.context(Mammoth)
    grok.description('')

# You can either refer to the menu class itself:
# do not forget the security declaration

class Index(grok.View):
    grok.title('View')
    grok.context(Mammoth)
    menu.menuitem(Tabs)

    def render(self):
        return 'index'

# or you can refer to its identifier:

class Edit(grok.View):
    grok.title('Edit')
    grok.context(Mammoth)
    menu.menuitem('tabs')
    grokcore.security.require('zope2.Public')

    def render(self):
        return 'edit'

# You can define custom context and action for menuitem

class CustomContext(grok.View):
    grok.title('CustomContext')
    grok.context(Smilodon)
    grok.require('zope2.Public')
    menu.menuitem('tabs', context=Mammoth, action='/path/customcontext')

    def render(self):
        return 'custom-context'
