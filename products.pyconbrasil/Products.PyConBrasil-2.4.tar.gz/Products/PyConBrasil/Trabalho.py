# -*- coding: utf-8 -*-
#
# File: Trabalho.py
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

##code-section module-header #fill in your manual code here
import transaction
##/code-section module-header

schema = Schema((

    StringField(
        name='trilha',
        index="FieldIndex:brains",
        widget=SelectionWidget
        (
            description="Selecione a trilha a qual seu trabalho melhor se destina",
            label="Trilha",
            label_msgid='PyConBrasil_label_trilha',
            description_msgid='PyConBrasil_help_trilha',
            i18n_domain='PyConBrasil',
            visible=0,
        ),
        vocabulary='getTrilhas',
        required=False
    ),

    StringField(
        name='titulo',
        index="FieldIndex:brains",
        widget=StringWidget(
            description="Informe o título do trabalho que você está submetendo.",
            label="Título",
            label_msgid='PyConBrasil_label_titulo',
            description_msgid='PyConBrasil_help_titulo',
            i18n_domain='PyConBrasil',
        ),
        required=True,
        searchable=True
    ),

    StringField(
        name='assunto',
        index=":schema",
        widget=StringWidget(
            description="Informe o assunto que trata o trabalho que você está submetendo.",
            label='Assunto',
            label_msgid='PyConBrasil_label_assunto',
            description_msgid='PyConBrasil_help_assunto',
            i18n_domain='PyConBrasil',
        ),
        required=True,
        searchable=True
    ),

    StringField(
        name='nivel',
        index="FieldIndex",
        widget=SelectionWidget
        (
            label="Nível da apresentação",
            description="Informe qual o nível de conhecimento para melhor acompanhamento desta apresentação / treinamento.",
            format="select",
            label_msgid='PyConBrasil_label_nivel',
            description_msgid='PyConBrasil_help_nivel',
            i18n_domain='PyConBrasil',
        ),
        enforceVocabulary=True,
        vocabulary=['Iniciante/Básico', 'Intermediário', 'Avançado'],
        required=True
    ),

    TextField(
        name='resumo',
        widget=TextAreaWidget(
            description="Faça um resumo do seu trabalho.",
            row="10",
            label='Resumo',
            label_msgid='PyConBrasil_label_resumo',
            description_msgid='PyConBrasil_help_resumo',
            i18n_domain='PyConBrasil',
        ),
        required=True,
        searchable=True
    ),

    StringField(
        name='tempo',
        widget=SelectionWidget
        (
            description="Duração estimada da apresentação de seu trabalho.",
            label="Tempo estimado",
            label_msgid='PyConBrasil_label_tempo',
            description_msgid='PyConBrasil_help_tempo',
            i18n_domain='PyConBrasil',
        ),
        required=True,
        read_permission="Review portal content",
        vocabulary='getVocTempo',
        enforceVocabulary=True
    ),

    StringField(
        name='nome',
        index="FieldIndex:brains",
        widget=StringWidget(
            description="Informe o seu nome completo.",
            label='Nome',
            label_msgid='PyConBrasil_label_nome',
            description_msgid='PyConBrasil_help_nome',
            i18n_domain='PyConBrasil',
        ),
        required=True,
        read_permission="View"
    ),

    TextField(
        name='curriculum',
        widget=TextAreaWidget(
            rows="5",
            cols="40",
            label="Curriculum do palestrante",
            description="Apresente, de maneira resumida, o seu curriculum.",
            label_msgid='PyConBrasil_label_curriculum',
            description_msgid='PyConBrasil_help_curriculum',
            i18n_domain='PyConBrasil',
        ),
        required=True,
        searchable=True
    ),

    ImageField(
        name='image',
        widget=ImageWidget(
            label="Foto do Palestrante",
            description="Forneça uma foto sua na proporção 3x4.",
            label_msgid='PyConBrasil_label_image',
            description_msgid='PyConBrasil_help_image',
            i18n_domain='PyConBrasil',
        ),
        storage=AttributeStorage(),
        sizes={'large': (768, 768),'preview':(400, 400),'mini':(200, 200),'thumb': (128, 128),'tile':(64, 64),'icon':(32, 32),'listing':(16, 16),},
    ),

    StringField(
        name='sexo',
        index=":schema",
        widget=SelectionWidget(
            description="Informe o seu sexo.",
            label='Sexo',
            label_msgid='PyConBrasil_label_sexo',
            description_msgid='PyConBrasil_help_sexo',
            i18n_domain='PyConBrasil',
        ),
        required=True,
        read_permission="View",
        vocabulary=['Feminino', 'Masculino'],
        enforceVocabulary=True
    ),

    StringField(
        name='email',
        index="FieldIndex:brains",
        widget=StringWidget(
            label="E-Mail",
            description="Informe o seu endereço eletrônico.",
            label_msgid='PyConBrasil_label_email',
            description_msgid='PyConBrasil_help_email',
            i18n_domain='PyConBrasil',
        ),
        required=1,
        read_permission="Modify portal content",
        validators=('isEmail',)
    ),

    StringField(
        name='telefone',
        index=":schema",
        widget=StringWidget(
            description="Informe o seu telefone para contato em caso de necessidade. Incluindo o código de área (e país caso fora do Brasil).",
            size=14,
            maxlength=20,
            label='Telefone',
            label_msgid='PyConBrasil_label_telefone',
            description_msgid='PyConBrasil_help_telefone',
            i18n_domain='PyConBrasil',
        ),
        required=True,
        read_permission="Modify portal content"
    ),

    StringField(
        name='cidade',
        index=":schema",
        widget=StringWidget(
            description="Informe o nome da cidade em que você reside.",
            label='Cidade',
            label_msgid='PyConBrasil_label_cidade',
            description_msgid='PyConBrasil_help_cidade',
            i18n_domain='PyConBrasil',
        ),
        required=True,
        read_permission="View"
    ),

    StringField(
        name='estado',
        index=":schema",
        widget=SelectionWidget(
            description="Selecione o Estado em que você reside.",
            label='Estado',
            label_msgid='PyConBrasil_label_estado',
            description_msgid='PyConBrasil_help_estado',
            i18n_domain='PyConBrasil',
        ),
        required=True,
        read_permission="View",
        vocabulary_factory='brasil.estados',
        enforceVocabulary=True
    ),

    TextField(
        name='endereco',
        index=":schema",
        widget=TextAreaWidget(
            description="Informe o endereço completo em que você reside. Será utilizado caso seja necessário enviar algo para você como por exemplo o certificado de participação.",
            label="Endereço",
            rows="5",
            cols="40",
            label_msgid='PyConBrasil_label_endereco',
            description_msgid='PyConBrasil_help_endereco',
            i18n_domain='PyConBrasil',
        ),
        read_permission="Modify portal content"
    ),

    StringField(
        name='instituicao',
        index=":schema",
        widget=StringWidget(
            description="Informe o nome da instituição que você representa.",
            label="Instituição",
            label_msgid='PyConBrasil_label_instituicao',
            description_msgid='PyConBrasil_help_instituicao',
            i18n_domain='PyConBrasil',
        ),
        read_permission="Modify portal content"
    ),

    TextField(
        name='observacoes',
        index=":schema",
        widget=TextAreaWidget(
            description="Descreva aqui qualquer observação que você achar pertinente.",
            label="Observações",
            label_msgid='PyConBrasil_label_observacoes',
            description_msgid='PyConBrasil_help_observacoes',
            i18n_domain='PyConBrasil',
        ),
        read_permission="Modify portal content"
    ),

    BooleanField(
        name='usoImagem',
        default="True",
        index="FieldIndex:brains",
        widget=BooleanWidget(
            label="Uso de imagem",
            description="Você cede o uso de sua palestra para a Associação Python Brasil disponibilizar os vídeos e materiais do evento para a comunidade?",
            label_msgid='PyConBrasil_label_usoImagem',
            description_msgid='PyConBrasil_help_usoImagem',
            i18n_domain='PyConBrasil',
        ),
        read_permission="View"
    ),

    StringField(
        name='slides',
        searchable=True,
        default = "http://",
        widget = StringWidget(
            label=u'Link Slides',
            label_msgid='label_slides',
            description='Link para slides ou outros materiais utilizados',
            description_msgid='help_slides',
        ),
        read_permission="View"
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Trabalho_schema = schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class Trabalho(UIDRenamer):
    """Classe abstrata com base comum aos trabalhos submetidos ao
    evento.
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(UIDRenamer,'__implements__',()),)

    allowed_content_types = []
    _at_rename_after_creation = True

    schema = Trabalho_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declarePrivate('getTrilhas')
    def getTrilhas(self):
        """Retorna as trilhas disponíveis
        """
        parent = self.aq_inner.aq_parent
        return parent.getTrilhas() or []

    # Manually created methods

    def Description(self):
        """Retorna o resumo do objeto no lugar de description
        """
        return self.getResumo()

    def Title(self):
        """Retorna o titulo do objeto no lugar de title
        """
        return self.getTitulo()


# end of class Trabalho

##code-section module-footer #fill in your manual code here
##/code-section module-footer



