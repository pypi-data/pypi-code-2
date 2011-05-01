##############################################################################
#
# Copyright (c) 2004-2006 CompositePack Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Navigation Page :

$Id: navigationpage.py 238387 2011-04-30 19:58:15Z hathawsh $
"""
from Acquisition import aq_base
from AccessControl import ClassSecurityInfo
from zope.interface import Interface 
from zope.interface import implements

from Products.Archetypes.public import BaseSchema

from Products.CompositePack.config import PROJECTNAME
from Products.CompositePack.composite import packcomposite
from Products.CompositePack.public import BaseFolder, registerType

from Products.CMFPlone.interfaces.structure import INonStructuralFolder


class INavigationPage(Interface):
    """ Marker interface
    """

class NavigationPage(BaseFolder):
    """A page composed of content selected manually."""
    meta_type = portal_type = 'Navigation Page'
    archetype_name = 'Navigation Page'
    
    typeDescription= 'A page composed of content selected manually.'
    typeDescMsgId  = 'description_edit_navigation_page'
    
    _at_rename_after_creation = True

    # Add INonStructuralFolder to tell Plone that even though
    # this type is technically a folder, it should be treated as a standard
    # content type. This ensures the user doesn't perceive a Navigation Page as
    # a folder.
    implements((INavigationPage, INonStructuralFolder))

    security = ClassSecurityInfo()
    
    schema = BaseSchema.copy()
    # Move the description field into the edit view.
    schema['description'].isMetadata = False
    schema['description'].schemata = 'default'
    actions = packcomposite.actions
    
    factory_type_information={
            'content_icon':'composite.gif',
            }

    def SearchableText(self):
        """Return text for indexing"""
        # Want title, description, and all Title and fragment content.
        # Fragments are converted from HTML to plain text.
        texts = [self.Title(), self.Description()]
        if getattr(aq_base(self.cp_container), 'titles', None) is not None:
            titles = self.cp_container.titles.objectValues()
            for o in titles:
        	      if hasattr(o, 'ContainerSearchableText'):
        		    texts.append(o.ContainerSearchableText())

        return " ".join(texts)

registerType(NavigationPage, PROJECTNAME)
