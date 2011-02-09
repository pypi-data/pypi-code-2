"""
How to enable session based authentication
******************************************

:Test-Layer: functional

If the `megrok.login.enable` directive is used, we get a login page
when trying to access a protected view.

We create an instance of App and store it in the ZODB::

  >>> from megrok.login.tests.simple import SimpleApp
  >>> root = getRootFolder()
  >>> root['simpleapp'] = SimpleApp()

Now, when we try to access the `index` view of the app, we'll get a
login page::
  
  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.open('http://localhost/simpleapp')
  >>> print browser.contents
  <!DOCTYPE html ...
  Please provide Login Information...
  <input type="text" name="login" id="login" />
  ...

We enter the credentials::
  
  >>> browser.getControl('User Name').value = 'mgr'
  >>> browser.getControl('Password').value = 'mgrpw'
  >>> browser.getControl('Log in').click()

We are redirected to the page we wanted to access in the beginning::

  >>> print browser.contents
  Hi!

"""
import grok
import megrok.login

class ManageApp(grok.Permission):
    grok.name('app.ManageSimple')

class SimpleApp(grok.Application, grok.Container):
    megrok.login.enable()

class Index(grok.View):
    grok.require('app.ManageSimple')

    def render(self):
        return "Hi!"
