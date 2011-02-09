import martian
import grok
import megrok.login
from zope import component
from zope.pluggableauth import PluggableAuthentication
from zope.pluggableauth.plugins.principalfolder import PrincipalFolder
from zope.pluggableauth.plugins.session import SessionCredentialsPlugin
from zope.authentication.interfaces import IAuthentication
from megrok.login.authplugins import (PrincipalRegistryAuthenticator,
                                      AutoRegisteringPrincipalFolder)

class ApplicationGrokker(martian.ClassGrokker):
    martian.component(grok.Site)
    martian.priority(100)
    martian.directive(megrok.login.enable, default=False)
    martian.directive(megrok.login.viewname, default=u'loginForm.html')
    martian.directive(megrok.login.strict, default=False)
    martian.directive(megrok.login.autoregister, default=u'')
    martian.directive(megrok.login.setup, default=None)
    
    def execute(self, factory, config, enable, viewname, strict,
                autoregister, setup, **kw):
        if enable is False:
            return False
        # XXX: check autoregister values
        adapts = (factory, grok.IObjectAddedEvent)
        config.action(
            discriminator=None,
            callable=component.provideHandler,
            args=(authenticationSubscriber, adapts)
            )
        return True

def authenticationSubscriber(site, event):
    try:
        # Conditional import. Newer versions of grok do not provide
        # `setupUtility` any more...
        from grok.meta import setupUtility
    except ImportError:
        from grokcore.site.interfaces import IUtilityInstaller
        setupUtility = component.getUtility(IUtilityInstaller)
    setupUtility(site, PluggableAuthentication(), IAuthentication,
                 setup=setupPAU,
                 name_in_container='megrok_login_pau')

def setupPAU(pau):
    """Callback to setup the Pluggable Authentication Utility """
    site = pau.__parent__.__parent__
    setup = megrok.login.component.setup.bind().get(site)
    viewname = megrok.login.component.viewname.bind().get(site)
    strict = megrok.login.component.strict.bind().get(site)
    autoregister = megrok.login.component.autoregister.bind().get(site)

    if setup is not None:
        # Call a customer defined callable.
        result = setup(pau, viewname=viewname, strict=strict,
                       autoregister=autoregister)
        return result
    
    if len(autoregister) > 0 :
        pau['principals'] = AutoRegisteringPrincipalFolder(
            autopermissions = autoregister)
    else:
        pau['principals'] = PrincipalFolder()
    pau.authenticatorPlugins = ('principals', )
    if strict is False:
        pau['readonly_principals'] = PrincipalRegistryAuthenticator()
        pau.authenticatorPlugins = ('principals', 'readonly_principals')

    pau['session'] = session = SessionCredentialsPlugin()
    # If we use this, already authenticated users will get no login
    # screen when they enter a forbidden page.
    #pau.credentialsPlugins = ('No Challenge if Authenticated', 'session',)
    pau.credentialsPlugins = ('session',)
    session.loginpagename = viewname
    return None
