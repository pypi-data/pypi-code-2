##############################################################################
#
# Copyright (c) 2004-2006 CompositePack Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""
$Id: compositetool.py 18879 2006-02-02 15:27:55Z jladage $
"""
from zope.app import zapi
from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.utils import XMLAdapterBase
from Products.GenericSetup.utils import ObjectManagerHelpers
from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects
from Products.Archetypes.utils import shasattr
from Products.CompositePack.interfaces import ICompositeTool
from Products.CompositePack.Extensions.Install import toolWrapper
from Products.CompositePack.config import LAYOUTS, VIEWLETS

class CompositeToolXMLAdapter(XMLAdapterBase, ObjectManagerHelpers):
    """
    Node im- and exporter for composite tool.
    """
    __used_for__ = ICompositeTool
    name = 'composite_tool'

    def _exportNode(self):
        """
        Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractCompositeConfiguration())
        self._logger.info("Composite settings exported.")
        return node

    def _importNode(self, node):
        """
        Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeObjects()

        self._initObjects(node)
        
    def _purgeObjects(self):
        """
        Keep the following folders:
          -  CompositePack Layout Container
          -  CompositePack Viewlet Container
          -  Slot Class Folder
        but delete all child object inside those folders
        """
        # This should be using the tools api instead.
        # not tested yet.
        tool = self.context
        for id, subobj in tool.objectItems():
            for sub_id in subobj.objectIds():
                subobj._delObject(sub_id)

    def _extractCompositeConfiguration(self):
        """
        Generate the composite_tool.xml from the current configuration.
        """
        fragment = self._doc.createDocumentFragment()
        tool = self.context

        # Lets start with the composites.
        compositesElement = self._doc.createElement('composites')
        compositesElement.setAttribute('name', 'composites')
        for composite in tool.getRegisteredComposites():
            child = self._doc.createElement('composite')
            child.setAttribute('name', composite)
            compositeElement = compositesElement.appendChild(child)

            layoutsForType = tool.getRegisteredLayoutsForType(composite)
            layoutsForType = [l.getId() for l in layoutsForType]
            for layout in layoutsForType:
                child = self._doc.createElement('c_layout')
                child.setAttribute('name', layout)
                default_layout = tool.getDefaultLayoutForType(composite).getId()
                if default_layout == layout and len(layoutsForType) > 1:
                    child.setAttribute('default', 'True')
                compositeElement.appendChild(child)
        fragment.appendChild(compositesElement)

        # Now for the composables.
        composablesElement = self._doc.createElement('composables')
        composablesElement.setAttribute('name', 'composites')
        for composable in tool.getRegisteredComposables():
            child = self._doc.createElement('composable')
            child.setAttribute('name', composable)
            composableElement = composablesElement.appendChild(child)

            viewletsForType = tool.getRegisteredViewletsForType(composable)
            viewletsForType = [v.getId() for v in viewletsForType]
            for viewlet in viewletsForType:
                child = self._doc.createElement('c_viewlet')
                child.setAttribute('name', viewlet)
                default_viewlet = tool.getDefaultViewletForType(composable).getId()
                if default_viewlet == viewlet and len(viewletsForType) > 1:
                    child.setAttribute('default', 'True')
                composableElement.appendChild(child)
        fragment.appendChild(composablesElement)

        # Let's add some viewlet!
        viewletsElement = self._doc.createElement('viewlets')
        viewletsElement.setAttribute('name', 'viewlets')
        for viewlet in tool.getAllViewlets():
            child = self._doc.createElement('viewlet')
            child.setAttribute('name', viewlet.getId())
            child.setAttribute('title', viewlet.Title())
            child.setAttribute('skin_method', viewlet.getSkinMethod())
            viewletsElement.appendChild(child)
        fragment.appendChild(viewletsElement)

        # Let's add some layouts!
        layoutsElement = self._doc.createElement('layouts')
        layoutsElement.setAttribute('name', 'layouts')
        for layout in tool.getAllLayouts():
            child = self._doc.createElement('layout')
            child.setAttribute('name', layout.getId())
            child.setAttribute('title', layout.Title())
            child.setAttribute('skin_method', layout.getSkinMethod())
            if layout.getId() == tool.getDefaultLayout():
                child.setAttribute('default', "true")
            layoutsElement.appendChild(child)
        fragment.appendChild(layoutsElement)

        return fragment

    def _configureComposables(self, node):
        """ Configure the mapping between content types and layouts
        """
        wtool = toolWrapper(self.context)
        comp_items = list()
        # Register composables first
        for composable in _filterNodes(node.childNodes):
            comp_items.append(composable.getAttribute('name'))
        wtool.registerAsComposable(comp_items)
        for composable in _filterNodes(node.childNodes):
            composable_id = composable.getAttribute('name')
            default_viewlet = ''
            c_viewlets = list()
            # Now register viewlets for each composable
            for c_viewlet in _filterNodes(composable.childNodes):
                c_viewlet_id = c_viewlet.getAttribute('name')
                c_viewlets.append(c_viewlet_id)
                if c_viewlet.hasAttribute('default'):
                    default_viewlet = c_viewlet_id
            if default_viewlet == '':
                if c_viewlets == []:
                    raise ValueError
                default_viewlet = c_viewlets[0]
            wtool.setViewletsForType(composable_id, c_viewlets, default_viewlet)
            self._logger.info('Composable: "%s" registered with viewlets: "%s"' % (composable_id,' '.join(c_viewlets)))
            self._logger.info('Default layout for "%s" is set to: "%s"' % (composable_id, default_viewlet))

    def _configureComposites(self, node):
        """
        Configure the mapping between content types and layouts
        """
        wtool = toolWrapper(self.context)
        comp_items = list()
        # Register composites first
        for composite in _filterNodes(node.childNodes):
            comp_items.append(composite.getAttribute('name'))
        wtool.registerAsComposite(comp_items)
        for composite in _filterNodes(node.childNodes):
            composite_id = composite.getAttribute('name')
            default_id = ''
            c_layouts = list()
            # Now register layouts for each composable
            for c_layout in _filterNodes(composite.childNodes):
                c_layout_id = c_layout.getAttribute('name')
                c_layouts.append(c_layout_id)
                if c_layout.hasAttribute('default'):
                    default_id = c_layout_id

            if default_id == '':
                if c_layouts == []:
                    raise ValueError
                default_id = c_layouts[0]

            for c_layout in c_layouts:
                layout = wtool.getLayoutById(c_layout)
                wtool.registerLayoutForType(layout, composite_id)

            default_layout = wtool.getLayoutById(default_id)
            wtool.setDefaultLayoutForType(default_layout, composite_id)
            self._logger.info('Composite: "%s" registered with layouts: "%s"' % (composite_id,' '.join(c_layouts)))
            self._logger.info('Default layout for "%s" is set to: ""%s"' % (composite_id, default_id))

    def _configureLayouts(self, node):
        """ Configure the layouts
        """
        wtool = toolWrapper(self.context)

        # Make sure the layouts folder exists.
        if not shasattr(self.context, LAYOUTS):
            from Products.CompositePack.viewlet import container
            container.addLayoutContainer(self.context, id=LAYOUTS,
                                  title='A Container for registered Layouts')
        # Register the layouts
        for layout in _filterNodes(node.childNodes):
            layout_id = layout.getAttribute('name')
            layout_title = layout.getAttribute('title')
            layout_skin_method = layout.getAttribute('skin_method')
            wtool.registerLayout(layout_id.encode(), layout_title.encode(), layout_skin_method.encode())
            self._logger.info('Layout: "%s" registered' % layout_title.encode())
            if layout.hasAttribute('default'):
                wtool.setDefaultLayout(layout_id)
                self._logger.info('Layout: "%s" set as tool default layout' % layout_title.encode())
            
    def _configureViewlets(self, node):
        """ Configure the Viewlets
        """
        wtool = toolWrapper(self.context)

        # Make sure the viewlets folder exists.
        if not shasattr(self.context, VIEWLETS):
            from Products.CompositePack.viewlet import container
            container.addViewletContainer(self.context, id=VIEWLETS,
                                 title='A Container for registered Viewlets')
        # Register the viewlets
        for viewlet in _filterNodes(node.childNodes):
            viewlet_id = viewlet.getAttribute('name')
            viewlet_title = viewlet.getAttribute('title')
            viewlet_skin_method = viewlet.getAttribute('skin_method')
            wtool.registerViewlet(viewlet_id.encode(), viewlet_title.encode(), viewlet_skin_method.encode())
            self._logger.info('Viewlet: "%s" registered' % viewlet_title.encode())

    def _initObjects(self, node):
        """
        Base on the nodeName of the DOM we create the corresponding type of object.
        One Issue though, layouts have to be registered before composites!
        """
        
        top_nodes = {
            "layouts"     : self._configureLayouts,
            "viewlets"    : self._configureViewlets,
            "composites"  : self._configureComposites,
            "composables" : self._configureComposables,
        }

        # Need to change the order, layouts first.
        for child in _filterNodes(node.childNodes):
            if child.nodeName in ('viewlets', 'layouts'):
                top_nodes.get(child.nodeName)(child)

        for child in _filterNodes(node.childNodes):
            if child.nodeName in ('composites', 'composables'):
                top_nodes.get(child.nodeName)(child)
        self.context.updateKupuLibraryTool()

def _filterNodes(nodes):
    """
    return a list of nodes with textnodes filtered out.
    """
    return [node for node in nodes if not shasattr(node, 'data')]


def importCompositeTool(context):
    """ Import composite tool properties.
    """
    site = context.getSite()
    logger = context.getLogger('composite tool properties')
    tool = getToolByName(site, 'composite_tool')

    body = context.readDataFile('composite_tool.xml')
    if body is None:
        body = context.readDataFile('compositetool.xml')
        if body is None:
            logger.info('Composite tool: Nothing to import.')
            return
        logger.info('Composite tool: deprecation warning, please rename your profile to composite_tool.xml.')

    importer = zapi.queryMultiAdapter((tool, context), IBody)
    if importer is None:
        logger.warning('Composite tool: Import adapter misssing.')
        return

    importer.body = body
    importObjects(tool, '', context)

def exportCompositeTool(context):
    """ Export composite tool properties.
    """

    site = context.getSite()
    logger = context.getLogger('composite tool')
    tool = getToolByName(site, 'composite_tool', None)
    if tool is None:
        logger.info('Nothing to export.')
        return

    exportObjects(tool, '', context)

