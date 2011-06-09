# -*- coding: utf-8 -*-

__author__ = """Jean Rodrigo Ferri / Dorneles Treméa / Fabiano Weimar / Rodrigo Senra /
Érico Andrei <contato@pythobrasil.com.br>"""
__docformat__ = 'plaintext'

import logging
logger = logging.getLogger('Products.PyConBrasil')
logger.debug('Installing Product')

try:
    import CustomizationPolicy
except ImportError:
    CustomizationPolicy = None

from Globals import package_home
from Products.CMFCore import utils as cmfutils

from Products.CMFCore import permissions as CMFCorePermissions

from Products.CMFCore import DirectoryView
from Products.CMFPlone.utils import ToolInit
from Products.Archetypes.atapi import *
from Products.Archetypes import listTypes
from Products.Archetypes.utils import capitalize

import os, os.path
from zope.i18nmessageid import MessageFactory as BaseMessageFactory
MessageFactory = BaseMessageFactory('Products.PyConBrasil')

from Products.PyConBrasil.config import *

def initialize(context):

    import Inscricoes
    import InscricaoCorporativa
    import Inscricao
    import Trabalho
    import Treinamento
    import Palestra
    import PalestraRelampago
    import Imprensa
    import UIDRenamer

    # Initialize portal content
    all_content_types, all_constructors, all_ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    cmfutils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = all_content_types,
        permission         = DEFAULT_ADD_CONTENT_PERMISSION,
        extra_constructors = all_constructors,
        fti                = all_ftis,
        ).initialize(context)

    for i in range(0,len(all_content_types)):
        klassname=all_content_types[i].__name__
        if not klassname in ADD_CONTENT_PERMISSIONS:
            continue

        context.registerClass(meta_type   = all_ftis[i]['meta_type'],
                              constructors= (all_constructors[i],),
                              permission  = ADD_CONTENT_PERMISSIONS[klassname])

