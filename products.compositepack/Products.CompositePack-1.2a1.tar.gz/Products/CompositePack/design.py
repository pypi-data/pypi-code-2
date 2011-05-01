##############################################################################
#
# Copyright (c) 2004-2006 CompositePack Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Plone UI for Composite Page design view.

$Id: design.py 238387 2011-04-30 19:58:15Z hathawsh $
"""
import os
import re
import Globals

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_inner, aq_parent

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFCore.FSDTMLMethod import FSDTMLMethod

from Products.CompositePage.designuis import CommonUI
from Products.CompositePage.rawfile import RawFile

from Products.CompositePack.config import PLONE21

_plone = os.path.join(os.path.dirname(__file__), 'plone')

if PLONE21:
    start_of_contentmenu_search = re.compile("(<li>[^<]*<dl[^>]*(>[^>]*){0,2}action(Plural|Singular|Menu)[^>]*)", re.IGNORECASE).search
else:
    start_of_contentmenu_search = re.compile("(<li[^>]*(>[^>]*){0,2}action(Plural|Singular|Menu)[^>]*)", re.IGNORECASE).search

class PloneUI(CommonUI):
    """Page design UI meant to fit Plone.

    Adds Plone-specific scripts and styles to a page.
    """
    security = ClassSecurityInfo()

    workspace_view_name = 'view'

    target_image = RawFile('target_image.gif', 'image/gif', _plone)
    target_image_hover = RawFile('target_image.gif', 'image/gif', _plone)
    target_image_active = RawFile('target_image.gif', 'image/gif', _plone)

    header_templates = CommonUI.header_templates + (
        PageTemplateFile('header.pt', _plone),)
    top_templates = CommonUI.top_templates + (
        PageTemplateFile('top.pt', _plone),)
    bottom_templates = (PageTemplateFile('bottom.pt', _plone),)
    if not PLONE21:
        contentmenu_templates = (PageTemplateFile('contentmenu_plone20.pt', _plone),)
    else:
        contentmenu_templates = (PageTemplateFile('contentmenu.pt', _plone),)

    security.declarePublic("getFragments")
    def getFragments(self, composite):
        """Returns the fragments to be inserted in design mode.
        """
        params = {
            "tool": aq_parent(aq_inner(aq_parent(aq_inner(self)))),
            "ui": self,
            "composite": composite,
            }
        contentmenu = ""
        for t in self.contentmenu_templates:
            contentmenu += str(t.__of__(self)(**params))
        result = CommonUI.getFragments(self, composite)
        result["contentmenu"] = contentmenu
        return result

    security.declarePrivate("render")
    def render(self, composite):
        """Renders a composite, adding scripts and styles.
        """
        text = CommonUI.render(self, composite)
        fragments = self.getFragments(composite)
        if fragments['contentmenu']:
            match = start_of_contentmenu_search(text)
            index = match and match.start(0) or -1
            text = "%s%s%s" % (text[:index], fragments['contentmenu'], text[index:])
        return text

Globals.InitializeClass(PloneUI)
