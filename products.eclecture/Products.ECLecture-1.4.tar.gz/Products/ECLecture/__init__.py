# -*- coding: utf-8 -*-
# $Id: __init__.py 1542 2011-04-01 07:13:53Z amelung $
#
# Copyright (c) 2006-2011 Otto-von-Guericke-UniversitŠt Magdeburg
#
# This file is part of ECLecture.
#
__author__ = """Mario Amelung <mario.amelung@gmx.de>"""
__docformat__ = 'plaintext'


import os
import logging

from zope.i18nmessageid import MessageFactory

from Products.Archetypes import listTypes
from Products.Archetypes.atapi import process_types
from Products.Archetypes.utils import capitalize
from Products.CMFCore import DirectoryView
from Products.CMFCore import permissions as cmfpermissions
from Products.CMFCore import utils as cmfutils
from Products.CMFPlone.utils import ToolInit


from Products.ECLecture import config 

LOG = logging.getLogger(config.PROJECTNAME)

DirectoryView.registerDirectory('skins', config.product_globals)

ECMessageFactory = MessageFactory('eduComponents')


def initialize(context):
    """initialize product (called by zope)
    """

    # imports packages and types for registration
    import content

    # Initialize portal content
    all_content_types, all_constructors, all_ftis = process_types(
        listTypes(config.PROJECTNAME),
        config.PROJECTNAME)

    cmfutils.ContentInit(
        config.PROJECTNAME + ' Content',
        content_types      = all_content_types,
        permission         = config.DEFAULT_ADD_CONTENT_PERMISSION,
        extra_constructors = all_constructors,
        fti                = all_ftis,
        ).initialize(context)

    # Give it some extra permissions to control them on a per class limit
    for i in range(0,len(all_content_types)):
        klassname=all_content_types[i].__name__
        if not klassname in config.ADD_CONTENT_PERMISSIONS:
            continue

        context.registerClass(meta_type   = all_ftis[i]['meta_type'],
                              constructors= (all_constructors[i],),
                              permission  = config.ADD_CONTENT_PERMISSIONS[klassname])


