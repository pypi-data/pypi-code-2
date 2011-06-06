# -*- coding: utf-8 -*-
#
# File: Inscricao.py
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
from Products.PyConBrasil.UIDRenamer import UIDRenamer
from Products.PyConBrasil.config import *

import transaction
from Products.CMFCore.utils import getToolByName
from Products.PyConBrasil import MessageFactory as _


schema = Schema((

    StringField(
        name='nome',
        widget=StringWidget(
            description=_(u'Informe o seu nome completo.'),
            label=_(u'Nome'),
        ),
        required=True,
        schemata='Seus dados',
    ),
    
    StringField(
        name='instituicao',
        widget=StringWidget(
            description=_(u'Informe o nome da instituição em que você estuda, trabalha ou representa.'),
            condition="not:object/emPreInscricao",
            label=_(u'Instituição'),
        ),
        schemata='Seus dados',
    ),
    
    StringField(
        name='sexo',
        widget=SelectionWidget(
            description=_(u'Informe o seu sexo.'),
            label=_(u'Sexo'),
        ),
        enforceVocabulary=True,
        vocabulary_factory='pythonbrasil.sexo',
        required=True,
        schemata='Seus dados',
    ),

    StringField(
        name='email',
        widget=StringWidget(
            label=_(u'E-Mail'),
            description=_(u'Informe o seu endereço eletrônico.'),
        ),
        required=True,
        validators=('isEmail',),
        schemata='Informações de contato',
    ),
    
    StringField(
        name='twitter',
        widget=StringWidget(
            label=_(u'Twitter'),
            description=_(u'Possui uma conta no Twitter, nos diga qual o seu usuário.'),
        ),
        required=False,
        schemata='Informações de contato',
    ),
        
    StringField(
        name='site',
        widget=StringWidget(
            label=_(u'Site  pessoal / Blog'),
            description=_(u'Caso tenha um site ou blog, por favor informe aqui o endereço, com o http://.'),
        ),
        required=False,
        validators=('isURL',),
        schemata='Informações de contato',
    ),
    
    StringField(
        name='telefone',
        widget=StringWidget(
            description=_(u'Informe o seu telefone para contato em caso de necessidade. Incluindo o código DDD.'),
            size=14,
            maxlength=20,
            label=_(u'Telefone'),
        ),
        schemata='Informações de contato',
    ),
    
    StringField(
        name='endereco',
        widget=StringWidget(
            size=40,
            maxlength=180,
            description=_(u'Informe o endereço completo em que você reside. Será utilizado caso seja necessário enviar algo para você como por exemplo um brinde, ou o certificado de participação.'),
            condition="not:object/emPreInscricao",
            label=_(u'Endereço'),
        ),
        schemata='Seu endereço',
    ),
    
    StringField(
        name='cep',
        widget=StringWidget(
            size=10,
            maxlength=9,
            description=_(u'Por favor informe o cep do endereço da empresa'),
            condition="not:object/emPreInscricao",
            label=_(u'CEP'),
        ),
        schemata='Seu endereço',
    ),
    
    StringField(
        name='cidade',
        widget=StringWidget(
            description=_(u'Informe o nome da cidade em que você reside.'),
            label=_(u'Cidade'),
        ),
        required=True,
        schemata='Seu endereço',
    ),

    StringField(
        name='estado',
        widget=SelectionWidget(
            description=_(u'Selecione o Estado em que você reside.'),
            label=_(u'Estado'),
        ),
        enforceVocabulary=True,
        vocabulary_factory='brasil.estados',
        required=True,
        schemata='Seu endereço',
    ),
    
    StringField(
        name='pais',
        widget=SelectionWidget(
            description=_(u'Informe o pais de sua residência.'),
            label=_(u'País'),
        ),
        default='Brasil',
        enforceVocabulary=True,
        vocabulary_factory='brasil.paises',
        required=True,
        schemata='Seu endereço',
    ),


    StringField(
        name='tipo',
        widget=SelectionWidget(
            description=_(u'Tipo da inscrição que está sendo realizada.'),
            condition="not:object/emPreInscricao",
            label=_(u'Tipo'),
        ),
        required=True,
        enforceVocabulary=True,
        default=3,
        vocabulary_factory='pythonbrasil.tipo_inscricao',
        schemata='Sua inscrição',
    ),

    StringField(
        name='camiseta',
        widget=SelectionWidget(
            description=_(u'Por favor nos informe qual o tamanho da camiseta que você pretende receber'),
            condition="not:object/emPreInscricao",
            label=_(u'Tamanho da camiseta'),
        ),
        required=True,
        enforceVocabulary=True,
        vocabulary_factory='pythonbrasil.camisetas',
        schemata='Sua inscrição',
    ),

    StringField(
        name='code',
        widget=StringWidget(
            description=_(u'Caso você tenha recebido um código de desconto do evento, o informe aqui.'),
            condition="not:object/emPreInscricao",
            label=_(u'Código de desconto'),
        ),
        schemata='Sua inscrição',
    ),

    BooleanField(
        name='optin_evento',
        widget=BooleanWidget(
            label=_(u'Aceito receber informações relativas a PythonBrasil'),
        ),
        default=True,
        schemata='Sua inscrição',
    ),

    BooleanField(
        name='optin_parceiros',
        widget=BooleanWidget(
            label=_(u'Aceito receber informações dos patrocinadores do evento'),
        ),
        default=True,
        schemata='Sua inscrição',
    ),

    BooleanField(
        name='paga',
        widget=BooleanWidget(
            visible=0,
            label=_(u'Paga'),
        )
    ),
    
    IntegerField(
        name='valor_pago',
        widget=IntegerWidget(
            condition="object/getPaga",
            label=_(u'Valor pago'),
        )
    ),
    
    ReferenceField(
        name='treinamentos',
        widget=ReferenceWidget(
            description=_(u'Selecione os treinamentos que você deseja participar.'),
            format="select",
            visible=True,
            condition="not:object/emPreInscricao",
            label=_(u'Treinamentos'),
        ),
        allowed_types=('Treinamento',),
        multiValued=True,
        relationship='Inscricao_Treinamento'
    ),

),
)

Inscricao_schema = BaseSchema.copy() + \
    schema.copy()

Inscricao_schema['title'].required = False
Inscricao_schema['title'].widget.visible = {'view':'invisible', 'edit':'invisible'}

##/code-section after-schema

class Inscricao(UIDRenamer, BaseContent):
    """Inscricao efetiva do participante do evento.
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(UIDRenamer,'__implements__',()),) + (getattr(BaseContent,'__implements__',()),)
    
    archetype_name = 'Inscrição'
    
    meta_type = 'Inscricao'
    portal_type = 'Inscricao'
    allowed_content_types = []
    filter_content_types = 0
    global_allow = 0
    content_icon = 'inscricao_icon.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "Inscrição de um participante no evento."
    typeDescMsgId = 'description_edit_inscricao'
    
    _at_rename_after_creation = True
    
    schema = Inscricao_schema
    for schemata in ['default','settings','categorization','metadata','dates','ownership']:
        for field in schema.getSchemataFields(schemata):
            field.widget.visible={'edit':'invisible','view':'invisible'}
    
    def Title(self):
        """Retorna o nome como título do objeto.
        """
        return self.getNome()
    
    def quantity(self):
        ''' Return the number of inscritos
        '''
        return 1
    
    def nomesParticipantes(self):
        return self.getTitle()



def modify_fti(fti):
    # Hide unnecessary tabs (usability enhancement)
    for a in fti['actions']:
        if a['id'] in ['metadata', 'sharing']:
            a['visible'] = 0
    return fti

registerType(Inscricao, PROJECTNAME)
