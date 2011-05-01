##############################################################################
#
# Copyright (c) 2004-2006 CompositePack Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Composite Portlet : this has an reference to a portlet template.

$Id: portlets.py 25210 2006-09-05 08:35:15Z jladage $
"""

from Products.Archetypes.public import *
from Products.CompositePage.interfaces import ICompositeElement
from Products.CompositePack.config import PROJECTNAME, TOOL_ID
from Products.CompositePack.exceptions import CompositePackError
from Products.CMFCore.utils import getToolByName
from DocumentTemplate.DT_Util import safe_callable
from Acquisition import aq_base, aq_parent, aq_inner
from zope.interface import implements

TARGET = 'target'
VIEWLET = 'viewlet'

class Portlet(BaseContentMixin):
    """A basic, Archetypes-based Composite Element
    that uses references instead of path, and a dropdown
    for selecting templates
    """
    implements(ICompositeElement)
    meta_type = portal_type = 'CompositePack Portlet'
    archetype_name = 'Portlet'
    global_allow = 0

    _at_rename_after_creation = True

    schema = MinimalSchema + Schema((
        StringField(
        'portlet',
        widget=SelectionWidget(label='Portlet',
	                       vocabulary='getAvailablePortlets',
                               visible={'edit':'invisible',
                                        'view':'invisible'},
                            description=('Composite page containing this portlet.'))
        ),
        ReferenceField(
        'viewlet',
        vocabulary='_get_viewlets',
        relationship=VIEWLET,
        widget=ReferenceWidget(label='Viewlet',
                               description=('The viewlet to be used '
                                            'for rendering the '
                                            'Context Object'))
        )))

    def getAvailablePortlets(self):
        """ Return a list of tuples available portlets in the portal. This will scan
        for all page templates that define a macro called portlet.
        """
        vocab = []
        skins = getToolByName(self, 'portal_skins')
        results = self.zopeFind(skins, obj_searchterm='metal:define-macro="portlet"', search_sub=1,)
        for brain in results:
            if brain['id'] in ids:
                id = brain['id']
                title = id[7:].capitalize()
                item = (id, title)
                vocab.append(item)
                
        return Displaylist(vocab)

    def _get_viewlets(self):
        obj = self.dereference()
        tool = getToolByName(self, TOOL_ID)
        v = tool.getViewletsFor(obj)
        if v is None:
            return DisplayList()
        viewlets = filter(None, (v.get('default'),) + tuple(v.get('viewlets')))
        options = tuple([(i['viewlet'].UID(), i['title'])
                   for i in viewlets])
        return DisplayList(options)

    def getViewlet(self):
        # refresh vocabulary
        self.schema['viewlet'].vocabulary = self._get_viewlets()
        return self.getField('viewlet').get(self)

    def getCurrentViewlet(self):
        refs = self.getRefs(VIEWLET)
        viewlet = refs and refs[0] or None
        if viewlet is None:
            obj = self.dereference()
            tool = getToolByName(self, 'composite_tool')
            viewlets = tool.getViewletsFor(obj)
            if viewlets is None:
                return None
            else:
                viewlet = viewlets.get('default')['viewlet']
        return viewlet
        
    def template(self):
        """ Returns the template referenced by this composite element.
        """
        viewlet = self.getCurrentViewlet()
        return viewlet and viewlet.getTemplate() or viewlet

    # ICompositeElement implementation
    def dereference(self):
        """Returns the object referenced by this composite element.
        """
        refs = self.getRefs(TARGET)
        if refs:
            return refs[0]
        else:
            raise CompositePackError('composite element has lost '
                'its reference to its target')

    def renderInline(self):
        """Returns a representation of this object as a string.
        """
        obj = self.dereference()
        template = self.template()
        if template is not None:
            if obj is not None:
                # Rewrap the template to give it the right context
                template = aq_base(template).__of__(obj)
            slot = aq_parent(aq_inner(self))
            slots = aq_parent(aq_inner(slot))
            composite = aq_parent(aq_inner(slots))
            viewlet = self.getCurrentViewlet() 
            return template(composite=composite, slots=slots, slot=slot,
                viewlet=viewlet)
        # No viewlet, try to call the object
        if safe_callable(obj):
            return obj()
        return str(obj)

    def queryInlineTemplate(self, slot_class_name=None):
        """Returns the name of the inline template this object uses.
        """
        # XXX What does this do?
        return 'Viewlet'

    def setInlineTemplate(self, template):
        """Sets the inline template for this object.
        """
        # XXX What does this do?
        return 'Viewlet'

    def listAllowableInlineTemplates(self, slot_class_name=None):
        """Returns a list of inline template names allowable for this object.
        """
        tool = getToolByName(self, 'composite_tool', None)
        if tool is not None:
            obj = self.dereference()
            viewlets = tool.getViewletsFor(obj)
            return [(i['id'], i['title']) for i in viewlets]
        # No tool found, so no inline templates are known.
        return ()

    def SearchableText(self):
        '''Titles shouldn't be indexed in their own right'''
        return None

    def indexObject(self):
        '''element is never catalogued'''
        pass

    def reindexObject(self, idxs=[]):
        '''element is never catalogued'''
        pass

    def unindexObject(self):
        '''element is never catalogued'''
        pass

registerType(Portlet, PROJECTNAME)
