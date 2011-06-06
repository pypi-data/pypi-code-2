# -*- coding: utf-8 -*-
import unittest
import doctest

try:
    from zope.site.hooks import setSite
    from zope.site.hooks import setHooks
except ImportError:
    from zope.app.component.hooks import setSite
    from zope.app.component.hooks import setHooks

from zope.testing import doctestunit
from zope.component import testing
from zope.component import getSiteManager
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from Products.PloneTestCase.layer import onsetup

from Products.SecureMailHost.SecureMailHost import SecureMailHost

import Products.PyConBrasil
import collective.brasil.vocab
import Products.DataGridField

PRODUCTS =  [('collective.brasil.vocab','Products.DataGridField',),]

def hacked_import(name):
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

@onsetup
def setup_product():
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml',
                     Products.PyConBrasil)
    fiveconfigure.debug_mode = False
    # Carrega profile de testes
    fiveconfigure.debug_mode = True
    zcml.load_config('testing.zcml',
                     Products.PyConBrasil.tests)
    fiveconfigure.debug_mode = False
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml',
                     Products.DataGridField)
    fiveconfigure.debug_mode = False
    ztc.installProduct('PyConBrasil')
    ztc.installProduct('DataGridField')

setup_product()

ptc.setupPloneSite(products=['Products.PyConBrasil','Products.DataGridField','PyConBrasil','DataGridField',],
                   extension_profiles=['Products.PyConBrasil.tests:testing',])

class DummySecureMailHost(SecureMailHost):
    meta_type = 'Dummy secure Mail Host'

    def __init__(self, id):
        self.id = id
        self.sent = []

    def _send(self, mfrom, mto, messageText, debug=False):
        self.sent.append(messageText)

class BaseSetUp(object):
    def afterSetUp(self):
        setHooks()
        setSite(self.portal)
        
        # Mock do MailHost
        sm = getSiteManager(self.portal)
        from Products.MailHost.interfaces import IMailHost
        sm.unregisterUtility(provided=IMailHost)
        dummyMailHost = DummySecureMailHost('dMailhost')
        sm.registerUtility(dummyMailHost, IMailHost)
        self.portal.MailHost = DummySecureMailHost('Mailhost')
        # Business as usual
        self.portal_path = '/'.join(self.portal.getPhysicalPath())
        self.loginAsPortalOwner()
        portal = self.portal
        portal.error_log._ignored_exceptions = ()
        self.wt = portal.portal_workflow
        portal.invokeFactory(type_name="Folder",id="2042",title="2042")
        evento = portal['2042']
        self.evento = evento
        evento.invokeFactory(type_name='Inscricoes',id='inscricoes',title='Inscricoes')
        self.inscricoes = evento['inscricoes']
        self.logout()
        

class TestCase(BaseSetUp,ptc.PloneTestCase):
    class layer(PloneSite):

        @classmethod
        def tearDown(cls):
            pass
    

class FunctionalTestCase(BaseSetUp,ptc.FunctionalTestCase):
    class layer(PloneSite):

        @classmethod
        def tearDown(cls):
            pass
    
    def abreInscricoes(self):
        self.loginAsPortalOwner()
        wt = self.wt
        evento = self.evento
        # Publica evento
        wt.doActionFor(evento,'publish')
        # Abre todas as inscricoes
        inscricoes = self.inscricoes
        wt.doActionFor(inscricoes,'abrir_todos')
        
