# -*- coding: utf-8 -*-
## Copyright (C) 2006 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
The FileSystemStorage package
$Id: __init__.py 114464 2010-04-01 16:25:17Z yboussard $
"""

__author__  = ''
__docformat__ = 'restructuredtext'

import os

from Products.CMFCore.utils import ContentInit
from Products.CMFCore import permissions as CCP

from Products.Archetypes.public import process_types, listTypes

from Products.CMFEditions.Modifiers import ConditionalTalesModifier

from iw.fss.modifier import manage_addModifier
from iw.fss.modifier import modifierAddForm
from iw.fss.modifier import MODIFIER_ID
from iw.fss import patches

def initialize(context):

    from iw.fss.config import PROJECTNAME
    from iw.fss.customconfig import (ZOPETESTCASE,
                                     INSTALL_EXAMPLE_TYPES_ENVIRONMENT_VARIABLE)

    if ZOPETESTCASE or os.environ.get(INSTALL_EXAMPLE_TYPES_ENVIRONMENT_VARIABLE):
        # Import example types
        from iw.fss import examples
        dummy = examples # No pyflakes warning
        content_types, constructors, ftis = process_types(listTypes(PROJECTNAME),
                                                          PROJECTNAME)
        ContentInit('%s Content' % PROJECTNAME,
                    content_types = content_types,
                    permission = CCP.AddPortalContent,
                    extra_constructors = constructors,
                    fti = ftis,
                    ).initialize(context)


    # Register modifier
    context.registerClass(
        ConditionalTalesModifier,
        MODIFIER_ID,
        permission=CCP.ManagePortal,
        constructors = (modifierAddForm, manage_addModifier),
        icon='modifier.gif',
        )

    # Setup module aliases to bind all Zope2 products
    import modulealiases
    dummy = modulealiases # No pyflakes warning

    # Provides 'plone' domain translations
    if not ZOPETESTCASE:
        try:
            i18n_dir = os.path.join(os.path.dirname(__file__), 'i18n')
            context._ProductContext__app.Control_Panel.TranslationService._load_i18n_dir(i18n_dir)
        except AttributeError, e:
            # No translation service obj
            # FIXME: we should find an alternate solution to push 'plone' domain translations
            import logging
            logger = logging.getLogger(PROJECTNAME)
            logger.warning("'plone' domain translations could'nt be enabled")

    return
