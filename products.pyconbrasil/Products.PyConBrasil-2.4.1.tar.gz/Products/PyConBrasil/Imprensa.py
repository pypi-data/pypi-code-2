# -*- coding: utf-8 -*-
#
# File: Imprensa.py
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
##/code-section module-header

schema = Schema((

    StringField(
        name='nome',
        widget=StringWidget(
            description="Informe o seu nome completo.",
            label='Nome',
            label_msgid='PyConBrasil_label_nome',
            description_msgid='PyConBrasil_help_nome',
            i18n_domain='PyConBrasil',
        ),
        required=1
    ),

    StringField(
        name='email',
        widget=StringWidget(
            label="E-Mail",
            description="Informe o seu endereço eletrônico.",
            label_msgid='PyConBrasil_label_email',
            description_msgid='PyConBrasil_help_email',
            i18n_domain='PyConBrasil',
        ),
        required=1,
        validators=('isEmail',)
    ),

    StringField(
        name='telefone',
        widget=StringWidget(
            description="Informe o seu telefone para contato em caso de necessidade. Incluindo o código DDD.",
            size=14,
            maxlength=20,
            label='Telefone',
            label_msgid='PyConBrasil_label_telefone',
            description_msgid='PyConBrasil_help_telefone',
            i18n_domain='PyConBrasil',
        ),
        required=1
    ),

    StringField(
        name='instituicao',
        widget=StringWidget(
            description="Informe o nome da instituição de imprensa que você representa.",
            label="Instituição",
            label_msgid='PyConBrasil_label_instituicao',
            description_msgid='PyConBrasil_help_instituicao',
            i18n_domain='PyConBrasil',
        ),
        required=1
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
        )
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Imprensa_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here

Imprensa_schema['title'].required = 0
Imprensa_schema['title'].widget.visible = {'view':'invisible', 'edit':'invisible'}

##/code-section after-schema

class Imprensa(UIDRenamer, BaseContent):
    """Profissional da imprensa que acompanhara o evento fazendo
    registros jornalisticos.
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(UIDRenamer,'__implements__',()),) + (getattr(BaseContent,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'Imprensa'

    meta_type = 'Imprensa'
    portal_type = 'Imprensa'
    allowed_content_types = []
    filter_content_types = 0
    global_allow = 0
    content_icon = 'imprensa_icon.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "Inscrição de um profissional ou órgão de imprensa."
    typeDescMsgId = 'description_edit_imprensa'

    _at_rename_after_creation = True

    schema = Imprensa_schema
    for schemata in ['settings','categorization','metadata','dates','ownership']:
        for field in schema.getSchemataFields(schemata):
            field.widget.visible={'edit':'invisible','view':'invisible'}
    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    # Manually created methods

    def Title(self):
        """Retorna o nome como titulo
        """

        return self.getNome()


def modify_fti(fti):
    # Hide unnecessary tabs (usability enhancement)
    for a in fti['actions']:
        if a['id'] in ['metadata', 'sharing']:
            a['visible'] = 0
    return fti

registerType(Imprensa, PROJECTNAME)
# end of class Imprensa

##code-section module-footer #fill in your manual code here
##/code-section module-footer



