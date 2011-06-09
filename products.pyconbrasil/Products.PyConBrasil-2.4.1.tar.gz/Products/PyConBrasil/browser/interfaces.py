# -*- coding: utf-8 -*-
from zope.interface import Interface

class IHelperView(Interface):
    """ Helper View
    """
    
    def ano():
        """ Em que ano estamos ancorados?
        """
        
    def price(inscricao):
        """ Preco a ser cobrado por todas as incricoes
        """
    
    def unit_price(inscricao):
        """ Preco a ser cobrado por uma inscricao
        """
    
    def formataValor(valor):
        """ Formata valor recebido em centavos
        """
    
    def patrocinadores():
        """ Retorna dados do pagseguro
        """
    
    def dadosPagSeguro():
        """ Retorna dados do pagseguro
        """