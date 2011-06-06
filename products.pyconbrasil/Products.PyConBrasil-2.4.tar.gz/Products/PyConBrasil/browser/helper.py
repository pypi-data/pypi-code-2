# -*- coding: utf-8 -*-

from Acquisition import aq_inner
from datetime import datetime
from zope.component import getMultiAdapter
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from plone.memoize.view import memoize
from string import Template
from Products.PyConBrasil import utils
import re


class HelperView(BrowserView):
    """ Helper view para a pasta de inscricoes
    """
    
    def _sheet(self):
        context = aq_inner(self.context)
        ptool = getToolByName(context,'portal_properties')
        ano = self.ano()
        sheet = getattr(ptool,'pythonbrasil_%d' % ano)
        return sheet
        
    
    def ano(self):
        ''' Em que ano estamos ancorados
        '''
        ano = 2011
        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        base_path = '/'.join(portal_state.portal().getPhysicalPath())
        path = '/'.join(context.getPhysicalPath())
        if not path == base_path:
            base_folder = path[len(base_path)+1:].split('/')[0]
            if base_folder.isdigit():
                ano = int(base_folder)
        return ano
    
    def prices(self,inscricao):
        ''' Retorna a lista de preços
        '''
        sheet = self._sheet()
        if not sheet:
            return []
        precos = sheet.getProperty('valor_inscricao',[])
        tipos = sheet.getProperty('tipo_inscricao',[])
        return utils.dictPrecos(precos,tipos)
        
    def price(self,inscricao):
        ''' Dado uma inscricao, retornamos o seu 
            preco
        '''
        price = int(self.unit_price(inscricao))
        # Participantes
        participantes = inscricao.quantity()
        price = price * participantes    
        return '%d' % price
    
    def unit_price(self,inscricao):
        ''' Dado uma inscricao, retornamos o seu 
            preco unitario
        '''
        price = 0
        context = aq_inner(self.context)
        validDiscounts = self.discountCodes()
        wt = getToolByName(context,'portal_workflow')
        # Tipo da inscricao
        tipo = inscricao.getTipo()
        # Participantes
        participantes = inscricao.quantity()
        # Desconto
        discount_code = inscricao.getCode().upper()
        # Estado
        review_state = wt.getInfoFor(inscricao,'review_state')
        # Se estiver paga, retornamos o preco pago
        if inscricao.getPaga():
            return inscricao.getValor_pago()
        # Caso contrario, o preco atual
        prices = self.prices(context)
        if tipo in prices:
            price = int(prices[tipo])
        if discount_code in validDiscounts:
            price = price * (1-validDiscounts[discount_code])
        if inscricao.portal_type == 'InscricaoCorporativa':
            # Calculamos o desconto de grupo e depois calculamos o total
            price = (price * (1-self.groupDiscounts(tipo,participantes)))
        return '%d' % price
    
    def formataValor(self,valor):
        ''' Formata valor passado em centavos
        '''
        return utils.formataValor(valor)
    
    def patrocinadores(self):
        ''' Retorna uma lista de dicionarios com os patrocinadores
        '''
        sheet = self._sheet()
        groups = sheet.getProperty('grupos_cotas',[])
        cotas = sheet.getProperty('cotas',[])
        patrocinadores = sheet.getProperty('patrocinadores',[])
        return utils.listaPatrocinadores(groups,cotas,patrocinadores)
        
    def dadosPagSeguro(self):
        sheet = self._sheet()
        pagseguro = {}
        pagseguro['email'] = sheet.getProperty('pagseguro_email','')
        pagseguro['url'] = sheet.getProperty('pagseguro_url','')
        pagseguro['description'] = sheet.getProperty('pagseguro_description','')
        return pagseguro
    
    def discountCodes(self):
        ''' Retorna a lista de codigos ainda disponiveis
        '''
        sheet = self._sheet()
        codes = sheet.getProperty('discount_codes',[])
        codes = utils.splitLines(sheet.getProperty('discount_codes', []))
        # Ex: 42W23|0.2
        return dict([(k.upper(),v) for k,v in codes])
        
    def groupDiscounts(self,tipo,participantes):
        ''' Retorna valor base para 
        '''
        sheet = self._sheet()
        codes = sheet.getProperty('group_discount',[])
        return utils.getGroupDiscount(codes,tipo,participantes)
    
