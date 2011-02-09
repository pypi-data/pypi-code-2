"""
How to setup auto registering authentication
********************************************

:Test-Layer: functional

When (beside `megrok.login.enable()`, which is always necessary), the
`megrok.login.autoregister()` directive is used, then all credentials
that contain a new username are automatically registered and accepted
when logging in.

The `autoregister` directive expects a permission name as
argument. This permission is granted to each auto-registered user. You
can also use this directive multiple times to grant more than one
permission.

We create an instance of ``AutoRegisterApp`` and store it in the ZODB::

  >>> from megrok.login.tests.autoregister import AutoRegisterApp
  >>> root = getRootFolder()
  >>> root['app'] = AutoRegisterApp()

Now, when we try to access the `index` view of the app, we'll get a
login page::
  
  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.open('http://localhost/app')
  >>> print browser.contents
  <!DOCTYPE html ...
  Please provide Login Information...
  <input type="text" name="login" id="login" />
  ...

We enter the credentials::
  
  >>> browser.getControl('User Name').value = 'bob'
  >>> browser.getControl('Password').value = 'bobspw'
  >>> browser.getControl('Log in').click()

We are redirected to the page we wanted to access in the beginning::

  >>> print browser.contents
  Hi autoregistered user!

We can also logout. This is managed by a specialized view (see
below)::

  >>> browser.open('http://localhost/app/@@logout')
  >>> print browser.contents
  You are logged out.

This is not a lie. When we try to watch our app, we will be asked for
a password again::

  >>> browser.open('http://localhost/app')
  >>> print browser.contents
  <!DOCTYPE html ...
  Please provide Login Information...
  <input type="text" name="login" id="login" />
  ...

If we try to login now with the wrong credentials, we will not get
through::

  >>> browser.getControl('User Name').value = 'bob'
  >>> browser.getControl('Password').value = 'notbobspw'
  >>> browser.getControl('Log in').click()
  >>> print browser.contents
  <!DOCTYPE html ...
  Please provide Login Information...
  <input type="text" name="login" id="login" />
  ...

The correct credentials, of course, will work::

  >>> browser.getControl('User Name').value = 'bob'
  >>> browser.getControl('Password').value = 'bobspw'
  >>> browser.getControl('Log in').click()
  >>> print browser.contents
  Hi autoregistered user!

  
"""
import grok
import megrok.login
from zope.authentication.interfaces import IAuthentication
from zope.component import getUtility

class ManageApp(grok.Permission):
    grok.name('app.ManageAutoRegister')

class AutoRegisterApp(grok.Application, grok.Container):
    megrok.login.enable()
    # We grant this permission to autoregistered users.
    megrok.login.autoregister('app.ManageAutoRegister')

class Index(grok.View):
    grok.require('app.ManageAutoRegister')

    def render(self):
        return "Hi autoregistered user!"

class Logout(grok.View):
    """A logout screen.
    """
    
    def render(self):
        # The session plugin which is automatically created, is always
        # called 'session'
        session = getUtility(IAuthentication)['session']
        session.logout(self.request)
        return "You are logged out."
