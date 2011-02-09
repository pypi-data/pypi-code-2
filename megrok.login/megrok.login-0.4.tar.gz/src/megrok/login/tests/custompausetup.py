"""
How to setup a cutomized PAU with ``megrok.login``
**************************************************

:Test-Layer: functional

You can setup the Pluggable Authentication Utility (PAU) completely
yourself. We defined a function `customPAUSetup` below, which performs
exactly that task.

We use::

  megrok.login.setup(<callable>)

to setup the PAU using this function.

As with all other directives of ``megrok.login``, we also have to set::

  megrok.login.enable()

to generally enable the ``megrok.login`` machinery explicitly.

We will see how this works in action and start by creating an
application instance::

  >>> from megrok.login.tests.custompausetup import CustomSetupApp
  >>> app = CustomSetupApp()

To setup the PAU, the app must become a site (it reacts on
IObjectAdded events). This is performed for instance by adding it to
the ZODB root folder::

  >>> root = getRootFolder()
  >>> root['app'] = app
  Custom PAU setup performed for <...CustomSetupApp object at 0x...>

The installed PAU is indeed the one, we configured below::

  >>> sm = app.getSiteManager()
  >>> sorted(list(sm['megrok_login_pau']))
  [u'custom_session', u'customprincipals', u'my_readonly_principals']

The installed setup is active. We can login via a login screen::

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.open('http://localhost/app')
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
  Hi from custom setup app!

Note, that the installed PAU (as any other PAU installed by
``megrok.login``) does only handle access to `app` or objects 'below'
`app`. It is a *local* utility. We are not authenticated for the root
folder, for example, which is handled by a different PAU::

  >>> browser.open('http://localhost')
  Traceback (most recent call last):
  ...
  HTTPError: HTTP Error 500: Internal Server Error

  >>> print browser.contents
  A system error occurred.

"""
import grok
import megrok.login

from zope.pluggableauth import PluggableAuthentication
from zope.pluggableauth.plugins.principalfolder import PrincipalFolder
from zope.pluggableauth.plugins.session import SessionCredentialsPlugin
from zope.authentication.interfaces import IAuthentication
from megrok.login.authplugins import (PrincipalRegistryAuthenticator,
                                      AutoRegisteringPrincipalFolder)

def customPAUSetup(site, pau, viewname=None, strict=None, autoregister=None):
    """Setup our own PAU.

    This setup performs more or less the same steps as a default
    setup. You are free to change it as you like and build completely
    different setups.
    """
    print "Custom PAU setup performed for %s" % site
    if len(autoregister) > 0 :
        pau['customprincipals'] = AutoRegisteringPrincipalFolder(
            autopermissions = autoregister)
    else:
        pau['customprincipals'] = PrincipalFolder()
    pau.authenticatorPlugins = ('customprincipals', )
    if strict is False:
        pau['my_readonly_principals'] = PrincipalRegistryAuthenticator()
        pau.authenticatorPlugins = ('cutomprincipals', 'my_readonly_principals')

    pau['custom_session'] = session = SessionCredentialsPlugin()
    pau.credentialsPlugins = ('No Challenge if Authenticated',
                              'custom_session',)
    session.loginpagename = viewname
    return

    
class ManageCustomSetupApp(grok.Permission):
    grok.name('app.manageCustomSetupApp')

class CustomSetupApp(grok.Application, grok.Container):
    megrok.login.enable()
    megrok.login.setup(customPAUSetup)

class Index(grok.View):
    grok.require('app.manageCustomSetupApp')

    def render(self):
        return "Hi from custom setup app!"
