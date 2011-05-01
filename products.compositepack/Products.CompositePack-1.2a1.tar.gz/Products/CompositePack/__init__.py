##############################################################################
#
# Copyright (c) 2004-2006 CompositePack Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Product initialization module.

$Id: __init__.py 238392 2011-05-01 03:46:07Z hathawsh $
"""

# Kickstart Install to make sure it works
from Products.CompositePack.Extensions import Install
del Install

from Products.CMFCore import utils as cmf_utils
from Products.CMFCore.DirectoryView import registerDirectory

from Products.CMFPlone import MigrationTool
import Products.CMFPlone.interfaces

from Products.Archetypes.public import *
from Products.Archetypes import listTypes

from Products.CompositePage import tool as base_tool

from Products.CompositePack.config import *
from Products.CompositePack import design
#from Products.CompositePack.ConfigurationMethods import GeneralSetup

from Products.GenericSetup import profile_registry
from Products.GenericSetup import EXTENSION


registerDirectory('skins', GLOBALS)
base_tool.registerUI('plone', design.PloneUI())


def initialize(context):
    from Products.CompositePack import tool, viewlet
    from Products.CompositePack.composite import archetype
    from Products.CompositePack.viewlet import container
    from Products.CompositePack.composite import navigationpage
    from Products.CompositePack.composite import titles
    from Products.CompositePack.composite import fragments
    from Products.CompositePack.composite import portlets

    if INSTALL_DEMO_TYPES:
        from Products.CompositePack.demo import ATCompositeDocument

    # register archetypes content with the machinery
    content_types, constructors, ftis = process_types(listTypes(PROJECTNAME),
                                                      PROJECTNAME)
    tools = (tool.CompositeTool,)

    cmf_utils.ContentInit(
        PROJECTNAME + ' Content',
        content_types = content_types,
        permission = ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti = ftis).initialize(context)

    registerClasses(context, PROJECTNAME, ['CompositePack Element',
                                           'CompositePack Viewlet',
                                           'CompositePack Layout',
                                           'CompositePack Titles',
                                           'CompositePack Fragments',
                                           'CompositePack Viewlet Container',
                                           'CompositePack Layout Container',
                                           'CompositePack Portlet'])

    context.registerClass(
        tool.CompositeTool,
        meta_type=TOOL_NAME,
        constructors=(tool.manage_addCompositeTool,),
        icon = TOOL_ICON)

    cmf_utils.ToolInit(TOOL_NAME,
                       tools = tools,
                       icon=TOOL_ICON
                   ).initialize(context)

    profile_registry.registerProfile(
        name='default',
        title='Composite Site',
        description='Profile for Composite Pack',
        path='profiles/default',
        product='CompositePack',
        profile_type=EXTENSION,
        for_=Products.CMFPlone.interfaces.IPloneSiteRoot)

    #MigrationTool.registerSetupWidget(GeneralSetup)


if True:
    # Provide a custom factory dispatcher that makes it possible for
    # the ZMI factory forms to use Archetypes fields.  (Otherwise, we get
    # an error saying the aq_inner attribute is unauthorized because
    # the container has no security assertions; the container is a
    # __FactoryDispatcher__.)

    from App.FactoryDispatcher import FactoryDispatcher
    from AccessControl import ClassSecurityInfo
    from Globals import InitializeClass

    class __FactoryDispatcher__(FactoryDispatcher):
        security = ClassSecurityInfo()
        security.declareObjectPublic()

    InitializeClass(__FactoryDispatcher__)
