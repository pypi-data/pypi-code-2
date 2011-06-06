# -*- coding: utf-8 -*-
#
# File: Inscricoes.py
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

from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.PyConBrasil.config import *

from urllib import quote
from Products.CMFCore.utils import getToolByName
from Products.PyConBrasil.interfaces import IInscricoes


schema = Schema((

    IntegerField(
        name='ano',
        widget=IntegerWidget(
            description="Informe a qual ano nos referimos nesta pasta.",
            label='Ano',
            label_msgid='PyConBrasil_label_ano',
            description_msgid='PyConBrasil_help_ano',
            i18n_domain='PyConBrasil',
        ),
        default=2010,
        required=True,
    ),

    TextField(
        name='texto',
        allowable_content_types=('text/plain', 'text/structured', 'text/html', 'application/msword',),
        widget=RichWidget(
            description="Informe o texto promocional que você deseja usar para esta pasta de inscrições.",
            label='Texto',
            label_msgid='PyConBrasil_label_texto',
            description_msgid='PyConBrasil_help_texto',
            i18n_domain='PyConBrasil',
        ),
        default_output_type='text/html'
    ),

    LinesField(
        name='trilhas',
        widget=LinesField._properties['widget'](
            rows="20",
            visible={'view':'invisible','edit':'visible'},
            label="Trilhas do evento",
            description="Informe, uma por linha, as trilhas disponíveis no evento.",
            label_msgid='PyConBrasil_label_trilhas',
            description_msgid='PyConBrasil_help_trilhas',
            i18n_domain='PyConBrasil',
        )
    ),

),
)

Inscricoes_schema = BaseBTreeFolderSchema.copy() + \
    schema.copy()

class Inscricoes(BaseBTreeFolder):
    """Pasta que contem todas as inscricoes de participantes,
    palestras, treinamentos, etc...
    """
    security = ClassSecurityInfo()
    implements(IInscricoes)

    # This name appears in the 'add' box
    archetype_name = 'Inscrições'

    meta_type = 'Inscricoes'
    portal_type = 'Inscricoes'
    allowed_content_types = ['Inscricao', 'Treinamento', 'Palestra', 'PalestraRelampago', 'Imprensa']
    filter_content_types = 1
    global_allow = 1
    content_icon = 'inscricoes_icon.gif'
    immediate_view = 'base_view'
    default_view = 'inscricoes_view'
    suppl_views = ()
    typeDescription = "Controle de Inscrições."
    typeDescMsgId = 'description_edit_inscricoes'
    allow_discussion = 1


    actions =  (

       {'action': "string:${object_url}/inscricoes_view",
        'category': "object",
        'id': 'view',
        'name': 'View',
        'permissions': ("View",),
        'condition': 'python:1'
       },


       {'action': "string:${object_url}/pre_inscricao_list",
        'category': "object",
        'id': 'pre_inscricao_list',
        'name': 'Pré-Inscrições',
        'permissions': ("Review portal content",),
        'condition': 'python:1'
       },


       {'action': "string:${object_url}/inscricao_list",
        'category': "object",
        'id': 'inscricao_list',
        'name': 'Inscrições',
        'permissions': ("Review portal content",),
        'condition': 'python:1'
       },


       {'action': "string:${object_url}/palestra_list",
        'category': "object",
        'id': 'palestra_list',
        'name': 'Palestras',
        'permissions': ("Review portal content",),
        'condition': 'python:1'
       },

       {'action': "string:${object_url}/imprensa_list",
        'category': "object",
        'id': 'imprensa_list',
        'name': 'Imprensa',
        'permissions': ("Review portal content",),
        'condition': 'python:1'
       },


    )

    _at_rename_after_creation = True

    schema = Inscricoes_schema

    security.declarePrivate('emEstado')
    def emEstado(self, estado):
        """Testa se o objeto está em um determinado estado.
        """
        portal_workflow = getToolByName(self, 'portal_workflow')
        review_state = portal_workflow.getInfoFor(self, 'review_state', None)
        return review_state == estado

    security.declarePublic('emInscricao')
    def emInscricao(self):
        """Testa se o objeto está aberto para inscrições, o que
        corresponde ao estado inscricoes do workflow.
        """
        return self.emEstado('inscricoes')

    security.declarePublic('emPreInscricao')
    def emPreInscricao(self):
        """Testa se o objeto está aberto para pré-inscrições, o que
        corresponde ao estado pre-inscricoes do workflow.
        """
        return self.emEstado('pre-inscricoes')
        
    security.declarePublic('confirmaInscricao')
    def confirmaInscricao(self, key):
        """Inicia o processo de confirmação de uma inscrição.
        """
        redirect = self.REQUEST.RESPONSE.redirect
        reference_catalog = getToolByName(self, 'reference_catalog')
        inscricao = reference_catalog.lookupObject(key)

        if inscricao is None or inscricao.portal_type != 'Inscricao':
            url = self.absolute_url()
            msg = 'Inscrição Inválida.'
            redirect = self.REQUEST.RESPONSE.redirect
            return redirect("%s?portal_status_message=%s" % (url, quote(msg)))

        portal_workflow = getToolByName(self, 'portal_workflow')
        review_state = portal_workflow.getInfoFor(inscricao, 'review_state')

        if review_state == 'pre-inscrito':
            portal_workflow.doActionFor(inscricao, 'iniciar_confirmacao')

        url = inscricao.absolute_url()
        msg = 'Preencha os campos restantes para confirmar sua inscrição.'
        return redirect('%s/edit?portal_status_message=%s' % (url, quote(msg)))


registerType(Inscricoes, PROJECTNAME)



