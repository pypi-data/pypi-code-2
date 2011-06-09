# -*- coding: utf-8 -*-
#
# File: Treinamento.py
#
# Copyright (c) 2007 by Associação Python Brasil
# Generator: ArchGenXML 
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

__author__ = """Jean Rodrigo Ferri / Dorneles Treméa / Fabiano Weimar / Rodrigo Senra /
Érico Andrei <contato@pythobrasil.com.br>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.PyConBrasil.Trabalho import Trabalho
from Products.PyConBrasil.config import *

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Treinamento_schema = BaseSchema.copy() + \
    getattr(Trabalho, 'schema', Schema(())).copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here

Treinamento_schema['title'].required = 0
Treinamento_schema['title'].widget.visible = {'view':'invisible', 'edit':'invisible'}

##/code-section after-schema

class Treinamento(Trabalho, BaseContent):
    """Inscricaoo de um treinamento, curso, mini-curso, tutorial,
    etc... Este treinamento depende da aprovacao pela comissao do
    evento.
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(Trabalho,'__implements__',()),) + (getattr(BaseContent,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'Treinamento'

    meta_type = 'Treinamento'
    portal_type = 'Treinamento'
    allowed_content_types = [] + list(getattr(Trabalho, 'allowed_content_types', []))
    filter_content_types = 0
    global_allow = 0
    content_icon = 'treinamento_icon.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "Inscrição de um treimanento no evento."
    typeDescMsgId = 'description_edit_treinamento'

    _at_rename_after_creation = True

    schema = Treinamento_schema
    for schemata in ['settings','categorization','metadata','dates','ownership']:
        for field in schema.getSchemataFields(schemata):
            field.widget.visible={'edit':'invisible','view':'invisible'}
    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declarePrivate('getVocTempo')
    def getVocTempo(self):
        """
        """
        vocTempo = ['Indiferente',
                    '2 horas',
                    '4 horas',
                    '8 horas',
                    '16 horas',]
        return tuple(vocTempo)

def modify_fti(fti):
    # Hide unnecessary tabs (usability enhancement)
    for a in fti['actions']:
        if a['id'] in ['metadata', 'sharing']:
            a['visible'] = 0
    return fti

registerType(Treinamento, PROJECTNAME)
# end of class Treinamento

##code-section module-footer #fill in your manual code here
##/code-section module-footer



