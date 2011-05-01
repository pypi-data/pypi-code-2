##############################################################################
#
# Copyright (c) 2004-2006 CompositePack Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Product configuration : constants

$Id: config.py 238389 2011-04-30 22:57:12Z hathawsh $
"""
import os
import Globals
import warnings

HAS_ATCT = True
PLONE21 = True
PLONE25 = True

try:
    from Products import azax 
    from Products import Five
except ImportError:
    #warnings.warn('CompositePack performance impaired: Five and Azax recommended', DeprecationWarning)
    HAVEAZAX = False
else:
    HAVEAZAX = True

from Products.CMFCore.utils import getToolByName

if HAS_ATCT and not PLONE21:
    try:
        from Products.ATContentTypes.ATNewsItem import ATNewsItem
    except ImportError:
        from Products.ATContentTypes.types.ATNewsItem import ATNewsItem
    def isSwitchedToATCT(portal):
        pt = getToolByName(portal, 'portal_types')
        news = pt.getTypeInfo('News Item')
        if news.Metatype() == ATNewsItem.meta_type:
            return 1
        else:
            return 0

try:
    from Products.GenericSetup import tool
except ImportError:
    HAS_GS = False
else:
    HAS_GS = True
    del tool

def get_ATCT_TYPES(self):
    result = {}
    if PLONE21 or (HAS_ATCT and isSwitchedToATCT(self)):
        result["Document"] = "Document"
        result["Image"] = "Image"
        result["File"] = "File"
        result["Event"] = "Event"
        result["NewsItem"] = "News Item"
        result["Topic"] = "Topic"
        result["Link"] = "Link"
        result["Favorite"] = "Favorite"
    elif HAS_ATCT and not isSwitchedToATCT(self):
        result["Document"] = "ATDocument"
        result["Image"] = "ATImage"
        result["File"] = "ATFile"
        result["Event"] = "ATEvent"
        result["NewsItem"] = "ATNewsItem"
        result["Topic"] = "ATTopic"
        result["Link"] = "ATLink"
        result["Favorite"] = "ATFavorite"
    return result

def get_COMPOSABLES_ATCT(self):
    result = get_ATCT_TYPES(self)
    del result["Favorite"]
    return result.values()

PROJECTNAME = 'CompositePack'
ADD_CONTENT_PERMISSION = 'Add CompositePack content'
GLOBALS = globals()

TOOL_ID = 'composite_tool'
TOOL_NAME = 'CompositePack Tool'
TOOL_ICON = 'composite.gif'

COMPOSABLE = 'composable'

VIEWLETS = 'viewlets'
LAYOUTS = 'layouts'

# CHANGE this tuple of python dictionnaries to list the stylesheets that
#  will be registered with the portal_css tool.
#  'id' (required):
#    it must respect the name of the css or DTML file (case sensitive).
#    '.dtml' suffixes must be ignored.
#  'expression' (optional - default: ''): a tal condition.
#  'media' (optional - default: ''): possible values: 'screen', 'print',
#    'projection', 'handheld'...
#  'rel' (optional - default: 'stylesheet')
#  'title' (optional - default: '')
#  'rendering' (optional - default: 'import'): 'import', 'link' or 'inline'.
#  'enabled' (optional - default: True): boolean
#  'cookable' (optional - default: True): boolean (aka 'merging allowed')
#  'compression' (optional - default: 'save')
#  See registerStylesheet() arguments in
#  ResourceRegistries/tools/CSSRegistry.py
#  for the latest list of all available keys and default values.
EXPR_ISCOMPO = 'python:here.composite_tool.isComposite(here.portal_type)'
EXPR_ISCOMPO_IN_DESIGN = EXPR_ISCOMPO + ' and here.cp_container.isEditing()'
STYLESHEETS = (
    {'id': 'compo.css', 'media': 'all',
     'expression': EXPR_ISCOMPO},
    {'id': 'editstyles.css', 'media': 'all',
     'expression': EXPR_ISCOMPO_IN_DESIGN},
    {'id': 'pdstyles.css', 'media': 'all',
     'expression': EXPR_ISCOMPO_IN_DESIGN},
    )

# CHANGE this tuple of python dictionnaries to list the javascripts that
#  will be registered with the portal_javascripts tool.
#  'id' (required): same rules as for stylesheets.
#  'expression' (optional - default: ''): a tal condition.
#  'inline' (optional - default: False): boolean
#  'enabled' (optional - default: True): boolean
#  'cookable' (optional - default: True): boolean (aka 'merging allowed')
#  'compression' (optional - default: 'save')
#  See registerScript() arguments in ResourceRegistries/tools/JSRegistry.py
#  for the latest list of all available keys and default values.
JAVASCRIPTS = (
    {'id': 'pdlib.js', 'cookable': False,
     'expression': EXPR_ISCOMPO_IN_DESIGN},
    {'id': 'plone_edit.js', 'cookable': False,
     'expression': EXPR_ISCOMPO_IN_DESIGN},
    {'id': 'compopagedrawer.js', 'cookable': False,
     'expression': EXPR_ISCOMPO_IN_DESIGN},
    )

INSTALL_DEMO_TYPES = 0 ##Install the demo types

zmi_dir = os.path.join(Globals.package_home(globals()),'www')

