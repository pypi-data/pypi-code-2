# -*- coding: utf-8 -*-
from datetime import datetime
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from Products.CMFCore.utils import getToolByName
from Products.PyConBrasil import utils

class BaseVocabulary(object):
    """ Base vocabulary for all PythonBrasil info
    """
    def __call__(self, context):
        self.context = getattr(context, 'context', context)
        self.ptool = getToolByName(context, 'portal_properties', None)
        self.sheet = getattr(self.ptool,'pythonbrasil_%s' % self.edicao_atual)
    
    @property
    def edicao_atual(self):
        ptool = self.ptool
        site_properties = getattr(ptool,'site_properties')
        return site_properties.getProperty('edicao_atual', '2011')
        


class Camisetas(BaseVocabulary):
    """ Tamanhos de camisetas
    """
    implements(IVocabularyFactory)
    
    def __call__(self, context):
        super(Camisetas,self).__call__(context)
        context = self.context
        ptool = self.ptool
        if ptool is None:
            return None
        sheet = self.sheet
        items = utils.splitLines(sheet.getProperty('tamanho_camiseta', []))
        items = [SimpleTerm('', '', 'Escolha uma camiseta')] + [SimpleTerm(k, k, v) for k,v in items]
        return SimpleVocabulary(items)
        
    


CamisetasVocabularyFactory = Camisetas()

class TipoInscricao(BaseVocabulary):
    """ Tipos de inscricao
    """
    implements(IVocabularyFactory)
    
    def __call__(self, context):
        super(TipoInscricao,self).__call__(context)
        context = self.context
        ptool = self.ptool
        if ptool is None:
            return None
        sheet = self.sheet
        items = utils.fmtVocabInscr(sheet)
        items = [SimpleTerm(k, k, v) for k,v,corp in items if corp !='1']
        return SimpleVocabulary(items)

TipoInscricaoVocabularyFactory = TipoInscricao()

class TipoInscricaoCorp(BaseVocabulary):
    """ Tipos de inscricao corporativa
    """
    implements(IVocabularyFactory)
    
    def __call__(self, context):
        super(TipoInscricaoCorp,self).__call__(context)
        context = self.context
        ptool = self.ptool
        if ptool is None:
            return None
        sheet = self.sheet
        items = utils.splitLines(sheet.getProperty('tipo_inscricao', []))
        items = [SimpleTerm(k, k, v) for k,v,corp in items if corp == '1']
        return SimpleVocabulary(items)

TipoInscricaoCorpVocabularyFactory = TipoInscricaoCorp()

class Sexo(object):
    """ Tipos de inscricao
    """
    implements(IVocabularyFactory)
    
    def __call__(self, context):
        items = ['Masculino','Feminino',]
        return SimpleVocabulary.fromValues(items)
        
    

SexoVocabularyFactory = Sexo()