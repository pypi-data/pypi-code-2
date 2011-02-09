"""

:Test-Layer: functional

If the `megrok.login.enable` directive is not used, we get the
standard behaviour, a HTTP error: 401 Unauthorized when trying to
access a protected view.

We create an instance of App and store it in the ZODB::

  >>> from megrok.login.tests.unset import App
  >>> root = getRootFolder()
  >>> root['app'] = App()

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.open('http://localhost/app')
  Traceback (most recent call last):
  ...
  httperror_seek_wrapper: HTTP Error 401: Unauthorized

We can, however, use basic-auth::

  >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')
  >>> browser.open('http://localhost/app')
  >>> browser.headers['status']
  '200 Ok'
  

"""
import grok

class ManageApp(grok.Permission):
    grok.name('app.ManageRaw')

class App(grok.Application, grok.Container):
    pass

class Index(grok.View):
    grok.require('app.ManageRaw')

    def render(self):
        return "Hi!"
