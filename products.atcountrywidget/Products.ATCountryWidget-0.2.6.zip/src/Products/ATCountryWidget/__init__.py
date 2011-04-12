# Copyright (c) 2004 gocept. All rights reserved.
# See also LICENSE.txt
# $Id: __init__.py 236779 2011-04-01 05:51:02Z nilo $

# Zope, Plone
from Products.Archetypes.public import process_types, listTypes
from Products.CMFCore import utils as cmfcutils
from Products.CMFCore.DirectoryView import registerDirectory
from Products.validation import validation

# siblings
from config import SKINS_DIR, GLOBALS, PROJECTNAME, access_contents_information, INSTALL_DEMO_TYPE
from validators import CountryValidator

registerDirectory(SKINS_DIR, GLOBALS)

def initialize(context):
    #tool
    import CountryTool
    tool = cmfcutils.ToolInit('Country Tool', tools=(CountryTool.CountryUtils,),
                          product_name='Country_Tool', icon='www/tool.gif')
    tool.initialize(context)

    #validator
    validation.register(CountryValidator('isValidISOCountry'))

    #demo-type
    if INSTALL_DEMO_TYPE:
        import ATCWDemoType
    
    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    cmfcutils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = access_contents_information,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)


    context.registerClass(
        CountryTool.CountryUtils,
        constructors=(CountryTool.manage_addCountryUtils,),
        icon='www/tool.gif')


