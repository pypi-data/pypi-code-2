"""

How to disable authentication of internal principals
****************************************************

:Test-Layer: functional

If we want to disable 'default' principals (users) defined in
``site.zcml`` or similar from logging in, we can use
``megrok.login.strict()``. This marker directive takes care, so that
only explicitly added users are allowed to log in.

The background: ``megrok.login`` by default installs *two* authenticator
plugins for your site:

 1) a usual ``PrincipalFolder`` instance which is empty in the
    beginning.

 2) a fallback folder that authenticates against principals held in
    the central principal registry.

The latter allows login of all principals defined in your site.zcml or
other ZCML configurations read on startup. The fallback-folder is
read-only. The common manager login for the whole instance is an
example for such an 'internal' principal.

When using ``megrok.login.strict()``, the second folder is not created
and the normally working accounts from the global principal registry
will not work.

We create an instance of App and store it in the ZODB::

  >>> from megrok.login.tests.strict import StrictApp
  >>> root = getRootFolder()
  >>> root['app'] = StrictApp()

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

When we enter the normal manager credentials, this will not let us
in. Instead we will again see the login page::
  
  >>> browser.getControl('User Name').value = 'mgr'
  >>> browser.getControl('Password').value = 'mgrpw'
  >>> browser.getControl('Log in').click()

  >>> print browser.contents
  <!DOCTYPE html ...
  Please provide Login Information...
  <input type="text" name="login" id="login" />
  ...

Before we can login, we have to add a user to the one and only
principal folder of our app.

First we create a new principal (user)::

  >>> from zope.pluggableauth.plugins.principalfolder import InternalPrincipal
  >>> bob = InternalPrincipal('bob', 'bobpw', 'bob')

We add bob to our principal folder::

  >>> app = root['app']
  >>> sm = app.getSiteManager()
  >>> pau = sm['megrok_login_pau']
  >>> principal_folder = pau['principals']
  >>> principal_folder['bob'] = bob

We grant `bob` the permission to view our app::

  >>> from zope.securitypolicy.interfaces import IPrincipalPermissionManager
  >>> perm_mgr = IPrincipalPermissionManager(app)
  >>> perm_mgr.grantPermissionToPrincipal(
  ...   'app.ManageStrict', principal_folder.prefix + 'bob')

Now we authenticate as Bob::

  >>> browser.getControl('User Name').value = 'bob'
  >>> browser.getControl('Password').value = 'bobpw'
  >>> browser.getControl('Log in').click()

We are redirected to the page we wanted to access in the beginning::

  >>> print browser.contents
  Hi from strict app!

"""
import grok
import megrok.login

class ManageApp(grok.Permission):
    grok.name('app.ManageStrict')

class StrictApp(grok.Application, grok.Container):
    megrok.login.enable()
    megrok.login.strict()

class Index(grok.View):
    grok.require('app.ManageStrict')

    def render(self):
        return "Hi from strict app!"
