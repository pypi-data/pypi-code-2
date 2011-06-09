# -*- coding: utf-8 -*-
#
# File: InscricaoCorporativa.py
#
# Copyright (c) 2011 by Associação Python Brasil
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

from Products.DataGridField import DataGridField, DataGridWidget
from Products.DataGridField.Column import Column
from Products.DataGridField.SelectColumn import SelectColumn
from Products.DataGridField.CheckboxColumn import CheckboxColumn

from zope.component import queryUtility
from zope.app.schema.vocabulary import IVocabularyFactory

import transaction
from Products.CMFCore.utils import getToolByName
from Products.PyConBrasil import MessageFactory as _


schema = Schema((

    StringField(
        name='razao_social',
        widget=StringWidget(
            description=_(u'Informa a razão social da empresa'),
            label=_(u'Razão Social'),
        ),
        schemata='Dados da Empresa / Organização',
        required=True
    ),

    StringField(
        name='email',
        widget=StringWidget(
            label=_(u'E-Mail'),
            description=_(u'Informe o seu endereço eletrônico para contato sobre as inscrições.'),
        ),
        schemata='Dados da Empresa / Organização',
        required=True,
        validators=('isEmail',)
    ),

    StringField(
        name='telefone',
        widget=StringWidget(
            description=_(u'Informe o seu telefone para contato em caso de necessidade. Incluindo o código DDD.'),
            size=14,
            maxlength=20,
            label=_(u'Telefone'),
        ),
        schemata='Dados da Empresa / Organização',
    ),
    
    StringField(
        name='endereco',
        widget=StringWidget(
            size=60,
            maxlength=180,
            description=_(u'Informe o endereço completo da empresa.'),
            condition="not:object/emPreInscricao",
            label=_(u'Endereço'),
        ),
        schemata='Endereço da Empresa',
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
        schemata='Endereço da Empresa',
    ),
    
    StringField(
        name='cidade',
        widget=StringWidget(
            description=_(u'Informe o nome da cidade da empresa.'),
            label=_(u'Cidade'),
        ),
        schemata='Endereço da Empresa',
        required=True,
    ),

    StringField(
        name='estado',
        widget=SelectionWidget(
            description=_(u'Selecione o Estado em que a empresa está localizada.'),
            label=_(u'Estado'),
        ),
        schemata='Endereço da Empresa',
        enforceVocabulary=True,
        vocabulary_factory='brasil.estados',
        required=True
    ),
    
    StringField(
        name='pais',
        widget=SelectionWidget(
            visible = False,
            description=_(u'Informe o pais de sua residência.'),
            label=_(u'País'),
        ),
        default='Brasil',
        enforceVocabulary=True,
        vocabulary_factory='brasil.paises',
        required=True,
        schemata='Endereço da Empresa',
    ),
    
    #Should be autocompute
    StringField(
        name='instituicao',
        widget=StringWidget(
            description=_(u'Informe o nome da instituição em que você estuda, trabalha ou representa.'),
            condition="not:object/emPreInscricao",
            label=_(u'Instituição'),
            visible=False,
        )
    ),

    StringField(
        name='tipo',
        widget=SelectionWidget(
            description=_(u'Tipo da inscrição que está sendo realizada. Órgãos públicos, escolham Empenho'),
            condition="not:object/emPreInscricao",
            label=_(u'Tipo de inscrição'),
        ),
        default="5",
        required=True,
        enforceVocabulary=True,
        vocabulary_factory='pythonbrasil.tipo_inscricao_corp',
        schemata='Dados da Inscrição',
    ),
    
    DataGridField('participantes',
        columns=('nome', 'email','sexo', 'camiseta'),
        required=True,
        allow_empty_rows = False,
        allow_delete = True,
        allow_insert = True,
        allow_reorder = False,
        allow_oddeven = True,
        widget = DataGridWidget(
            macro='participanteswidget',
            label=_(u'Lista de Participantes'),
            description=_(u'Informe quais serão os participantes enviados por sua empresa'),
            columns= {
                "nome" : Column(u"Nome do participante"),
                "email": Column(u"E-mail"),
                "sexo" : SelectColumn((u"Sexo"), vocabulary="getSexo"),
                "camiseta" : SelectColumn((u"Camiseta"), vocabulary="getCamiseta"),
            }
        ),
        schemata='Dados da Inscrição',
    ),
    
    StringField(
        name='code',
        widget=StringWidget(
            description=_(u'Caso você tenha recebido um código de desconto do evento, o informe aqui.'),
            condition="not:object/emPreInscricao",
            label=_(u'Código de desconto'),
        ),
        schemata='Dados da Inscrição',
    ),
    
    BooleanField(
        name='optin_evento',
        widget=BooleanWidget(
            label=_(u'Aceito receber informações relativas a PythonBrasil'),
            label_msgid='PyConBrasil_label_optin',
            i18n_domain='PyConBrasil',
        ),
        schemata='Dados da Inscrição',
        default=True,
    ),

    BooleanField(
        name='optin_parceiros',
        widget=BooleanWidget(
            label=_(u'Aceito receber informações dos patrocinadores do evento'),
        ),
        schemata='Dados da Inscrição',
        default=True,
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
            visible=0,
            condition="not:object/emPreInscricao",
            label=_(u'Treinamentos'),
        ),
        allowed_types=('Treinamento',),
        multiValued=1,
        relationship='Inscricao_Treinamento'
    ),

),
)

InscricaoCorporativa_schema = BaseSchema.copy() + \
    schema.copy()

InscricaoCorporativa_schema['title'].required = 0
InscricaoCorporativa_schema['title'].widget.visible = {'view':'invisible', 'edit':'invisible'}

##/code-section after-schema

class InscricaoCorporativa(UIDRenamer, BaseContent):
    """Inscricao efetivada por uma empresa em nome de seus funcionarios
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(UIDRenamer,'__implements__',()),) + (getattr(BaseContent,'__implements__',()),)
    
    archetype_name = 'Inscrição corporativa'
    
    meta_type = 'InscricaoCorporativa'
    portal_type = 'InscricaoCorporativa'
    allowed_content_types = []
    filter_content_types = 0
    global_allow = 0
    content_icon = 'inscricao_icon.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "Inscrição de participantes por uma empresa."
    typeDescMsgId = 'description_edit_inscricao_corp'
    
    _at_rename_after_creation = True
    
    schema = InscricaoCorporativa_schema
    for schemata in ['settings','default','categorization','metadata','dates','ownership']:
        for field in schema.getSchemataFields(schemata):
            field.widget.visible={'edit':'invisible','view':'invisible'}
    
    def Title(self):
        """Retorna o nome como título do objeto.
        """
        return self.getRazao_social()
    
    def validate_participantes(self,value):
        code = False
        for line in value:
            nome = line.get('nome','').strip()
            email = line.get('email','').strip()
            sexo = line.get('sexo','').strip()
            camiseta = line.get('camiseta','').strip()
            if not (nome and email and sexo and camiseta):
                continue
            if not (nome and email):
                code = False
            else:
                code = True
        if not code:
            return _(u"Por favor não deixe nenhum nome em branco.")
    
    def _convertVocab(self,name):
        util = queryUtility(IVocabularyFactory, name)
        vocab = util(self)
        vocab = [('','Escolha'),] +[((v.token, v.title or v.value,)) for v in vocab if v.value]
        return DisplayList(vocab)
    
    def getSexo(self):
        name = 'pythonbrasil.sexo'
        return self._convertVocab(name)
    
    def getCamiseta(self):
        name = 'pythonbrasil.camisetas'
        return self._convertVocab(name)
    
    def getCode(self):
        # Companies do not have a discount code
        return ''
    
    def quantity(self):
        ''' Return the number of inscritos
        '''
        participantes = self.getParticipantes()
        participantes = [p for p in participantes if p.get('nome').strip()]
        return len(participantes)
    
    def nomesParticipantes(self):
        participantes = self.getParticipantes()
        return [p.get('nome') for p in participantes if p.get('nome').strip()]

def modify_fti(fti):
    # Hide unnecessary tabs (usability enhancement)
    for a in fti['actions']:
        if a['id'] in ['metadata', 'sharing']:
            a['visible'] = 0
    return fti

registerType(InscricaoCorporativa, PROJECTNAME)
