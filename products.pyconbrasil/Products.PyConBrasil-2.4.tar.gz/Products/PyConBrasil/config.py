# -*- coding: utf-8 -*-

__author__ = """Jean Rodrigo Ferri / Dorneles Treméa / Fabiano Weimar / Rodrigo Senra /
Érico Andrei <contato@pythobrasil.com.br>"""
__docformat__ = 'plaintext'

from Products.CMFCore.permissions import setDefaultRoles

PROJECTNAME = "Products.PyConBrasil"

DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"
setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner'))
ADD_CONTENT_PERMISSIONS = {
    'Inscricoes': 'PyConBrasil: Add Inscricoes',
    'InscricaoCorporativa': 'PyConBrasil: Add Inscricao',
    'Inscricao': 'PyConBrasil: Add Inscricao',
    'Treinamento': 'PyConBrasil: Add Treinamento',
    'Palestra': 'PyConBrasil: Add Palestra',
    'PalestraRelampago': 'PyConBrasil: Add PalestraRelampago',
    'Imprensa': 'PyConBrasil: Add Imprensa',
}
setDefaultRoles('PyConBrasil: Add Inscricoes', ('Manager',))
setDefaultRoles('PyConBrasil: Add Inscricao', ('Manager', 'Member', 'Anonymous'))
setDefaultRoles('PyConBrasil: Add Treinamento', ('Manager',))
setDefaultRoles('PyConBrasil: Add Palestra', ('Manager', 'Member', 'Anonymous'))
setDefaultRoles('PyConBrasil: Add PalestraRelampago', ('Manager',))
setDefaultRoles('PyConBrasil: Add Imprensa', ('Manager', 'Member', 'Anonymous'))

product_globals = globals()