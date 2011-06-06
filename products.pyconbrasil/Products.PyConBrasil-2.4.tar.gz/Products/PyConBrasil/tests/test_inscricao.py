# -*- coding: utf-8 -*-
import unittest
import doctest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from Products.PloneTestCase.layer import onsetup

from Products.PyConBrasil.tests.base import TestCase, FunctionalTestCase
from Products.PyConBrasil.Inscricao import Inscricao
from AccessControl import Unauthorized

class InscricaoTest(TestCase):
    def test_inscricoes_nao_abertas(self):
        # Como anonimo vamos criar uma inscricao
        # com o objeto Inscricoes ainda nao liberado
        self.logout()
        inscricoes = self.inscricoes
        dictParam = {'type_name':'Inscricao','id':'FooBar','title':'FooBar'}
        self.assertRaises(Unauthorized, inscricoes.invokeFactory, **dictParam)

    def test_abrir_inscricoes(self):
        # Como manager vamos abrir as inscricoes
        self.loginAsPortalOwner()
        wt = self.wt
        inscricoes = self.inscricoes
        # Abre todas as inscricoes
        wt.doActionFor(inscricoes,'abrir_inscricoes')
        # Como anonimo vamos criar uma inscricao
        self.logout()
        dictParam = {'type_name':'Inscricao','id':'FooBar','title':'FooBar'}
        inscricao =inscricoes.invokeFactory(**dictParam)
        oInscricao = inscricoes[inscricao]
        self.failUnless(isinstance(oInscricao,Inscricao))
        

def test_suite():
    return unittest.TestSuite([

        ztc.FunctionalDocFileSuite(
            'inscricao.txt', 
            package='Products.PyConBrasil.docs',
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | 
                        doctest.NORMALIZE_WHITESPACE | 
                        doctest.ELLIPSIS,
            test_class=FunctionalTestCase),
        
        unittest.makeSuite(InscricaoTest)
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
