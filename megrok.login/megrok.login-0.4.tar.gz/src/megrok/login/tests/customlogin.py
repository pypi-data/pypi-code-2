"""
How to setup a customized login page
************************************

:Test-Layer: functional

Using the `megrok.login.viewname` directive, you can specify your own
login page. If you do not use it, a default page is used.

If the `megrok.login.enable` directive is used, we get a login page
when trying to access a protected view.

If - additionally - a `megrok.login.viewname` directive is declared,
then this view will be used as the login page.

We create an instance of ``CustomLoginApp`` and store it in the ZODB::

  >>> from megrok.login.tests.customlogin import CustomLoginApp
  >>> root = getRootFolder()
  >>> root['app'] = CustomLoginApp()

Now, when we try to access the `index` view of the app, we'll get a
login page::
  
  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.open('http://localhost/app')
  >>> print browser.contents
  <html>...
  <h1>Custom Login Page</h1>...
  <input type="text" name="login" id="login" />
  ...

We enter the credentials::
  
  >>> browser.getControl(name='login').value = 'mgr'
  >>> browser.getControl(name='password').value = 'mgrpw'
  >>> browser.getControl('Log in').click()

We are redirected to the page we wanted to access in the beginning::

  >>> print browser.contents
  Hi after custom login!

  
Login view fields
-----------------
  
For the authentication it is essential, that your login form provides:

 * a field named `login` with the username (principal title)

 * a field named `password` with the password.

The pluggable authentication utility will lookup those fields.

If the password is wrong (or the username does not exist), we will again
be redirected to the login page.


Context of login views
----------------------

As with all views, also your login view is bound to the types of
objects declared with `grok.context`. You can setup different login
views for different types of objects, but if you want all kinds of
objects to be handled by your form, then you should bind to context
`Interface` as shown below.


"""
import grok
import megrok.login
from zope.interface import Interface

class ManageApp(grok.Permission):
    grok.name('app.ManageCustomLogin')

class CustomLoginApp(grok.Application, grok.Container):
    """An application that provides a custom login page.
    """
    megrok.login.enable()
    megrok.login.viewname('login') # Look for a view named 'login'
                                   # when we need authentication.

class Index(grok.View):
    grok.require('app.ManageCustomLogin')

    def render(self):
        return "Hi after custom login!"

class Login(grok.View):
    """A login view.

    See also `login.pt` in `customlogin_templates`
    """
    grok.context(Interface) # We bind to all possible contexts

    def update(self, camefrom=None, SUBMIT=None):
        self.camefrom=camefrom
        if SUBMIT is not None and camefrom is not None:
            # The credentials were entered. Go back. If the entered
            # credentials are not valid, another redirect will happen
            # to this view.
            self.redirect(camefrom)
        return
