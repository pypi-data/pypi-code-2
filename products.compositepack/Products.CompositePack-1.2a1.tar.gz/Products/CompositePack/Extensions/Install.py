##############################################################################
#
# Copyright (c) 2004-2006 CompositePack Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""CMF/Plone install

$Id: Install.py 238387 2011-04-30 19:58:15Z hathawsh $
"""

from cStringIO import StringIO
from Products.Archetypes.public import listTypes
from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.CompositePack.config import PROJECTNAME, GLOBALS, TOOL_ID
from Products.CompositePack.config import COMPOSABLE
from Products.CompositePack.config import get_COMPOSABLES_ATCT
from Products.CompositePack.config import get_ATCT_TYPES
from Products.CompositePack.config import INSTALL_DEMO_TYPES
from Products.CompositePack.config import HAS_ATCT, HAVEAZAX
from Products.CompositePack.config import PLONE21
from Products.CompositePack.config import STYLESHEETS, JAVASCRIPTS
from Products.CMFCore.utils import getToolByName
from Products.kupu.plone.plonelibrarytool import PloneKupuLibraryTool

KUPU_TOOL_ID = PloneKupuLibraryTool.id

COMPO_TYPE = 'CMF Composite Page'

class toolWrapper:
    def __init__(self, tool):
        self.tool = tool
        
    def registerAsComposite(self, items):
        if type(items) not in (tuple, list):
            items = (items,)

        items = [ item for item in items if not self.tool.isComposite(item) ]
        if items:
            self.tool.registerAsComposite(items)

    def registerAsComposable(self, items):
        if type(items) not in (tuple, list):
            items = (items,)

        items = [ item for item in items if not self.tool.isComposable(item) ]
        if items:
            self.tool.registerAsComposable(items)

    def registerLayout(self, id, description, skin_method):
        layout = self.tool.getLayoutById(id)
        if layout:
            return layout
        return self.tool.registerLayout(id, description, skin_method)

    def registerViewlet(self, id, description, skin_method):
        viewlet = self.tool.getViewletById(id)
        if viewlet:
            return viewlet
        return self.tool.registerViewlet(id, description, skin_method)

    def __getattr__(self, name):
        if hasattr(self.tool, name):
            return getattr(self.tool, name)
        else:
            raise AttributeError(name)

def install_tool(self, out):
    if not hasattr(self, TOOL_ID):
        self.manage_addProduct['CompositePack'].manage_addCompositeTool()
    tool = toolWrapper(getattr(self, TOOL_ID))

    if INSTALL_DEMO_TYPES:
        tool.registerAsComposite('Composable Document')
    tool.registerAsComposite('Navigation Page')

    if HAS_ATCT:
        tool.registerAsComposable(get_COMPOSABLES_ATCT(self))
    tool.registerAsComposable('CompositePack Titles')
    tool.registerAsComposable('CompositePack Fragments')
    
    ts = tool.registerLayout('two_slots', 'Two slots', 'two_slots')
    try:
        ts.registerForType('Navigation Page')
    except AttributeError:
        raise RuntimeError, "ts=%r" % ts

    ts = tool.registerLayout('three_slots', 'Three slots', 'three_slots')
    ts.registerForType('Navigation Page')

    ts = tool.registerLayout('two_columns', 'Two columns', 'two_columns')
    ts.registerForType('Navigation Page')
    ts.setDefaultForType('Navigation Page')
    tool.setDefaultLayout('two_columns')

    if INSTALL_DEMO_TYPES:
        ds = tool.registerLayout('document_sidebar_view',
                            'Document with sidebar',
                            'document_sidebar_view')
        ds.registerForType('Composite Document')
        ds.setDefaultForType('Composite Document')

    bv = tool.registerViewlet('title_description_with_link',
                         'Title with description',
                         'title_description_with_link')
    tool.registerViewletForDefaultSetup(bv)
    tool.registerViewlet('link_viewlet',
                         'Link Only',
                         'link_viewlet')
    tool.registerViewlet('title_viewlet',
                         'Title',
                         'title_viewlet')
    tool.registerViewlet('fragment_viewlet',
                         'HTML Fragment',
                         'fragment_viewlet')
    tool.registerViewlet('title_date_viewlet',
                         'Title and Date',
                         'title_date_viewlet')
    tool.registerViewlet('image_viewlet',
                         'Image',
                         'image_viewlet')
    tool.registerViewlet('image_title_viewlet',
                         'Image with title',
                         'image_title_viewlet')
    tool.registerViewlet('image_caption_viewlet',
                         'Image with caption',
                         'image_caption_viewlet')
    tool.registerViewlet('topic_viewlet',
                         'Topic Listing',
                         'topic_viewlet')
    tool.setViewletsForType('CompositePack Titles', ['title_viewlet'],
                            'title_viewlet')
    tool.setViewletsForType('CompositePack Fragments', ['fragment_viewlet'],
                            'fragment_viewlet')
    if HAS_ATCT:
       IMAGE_TYPE = get_ATCT_TYPES(self)['Image']
       tool.setViewletsForType(IMAGE_TYPE, ['image_viewlet',
                                            'link_viewlet',
                                            'image_title_viewlet',
                                            'image_caption_viewlet'],
                                            'image_viewlet')
       TOPIC_TYPE = get_ATCT_TYPES(self)['Topic']
       tool.setViewletsForType(TOPIC_TYPE, ['topic_viewlet'], 'topic_viewlet')
    out.write("CompositePack Tool Installed\n")

def setup_portal_factory(self, out):
    factory = getToolByName(self, 'portal_factory')
    types = factory.getFactoryTypes().keys()
    if 'Navigation Page' not in types:
        out.write('Navigation Page setup in portal_factory\n')
        types.append('Navigation Page')
        factory.manage_setPortalFactoryTypes(listOfTypeIds = types)
    if 'Navigation Titles' not in types:
        out.write('Navigation Titles setup in portal_factory\n')
        types.append('Navigation Titles')
        factory.manage_setPortalFactoryTypes(listOfTypeIds = types)
    if 'Navigation Page HTML' not in types:
        out.write('Navigation Page HTML setup in portal_factory\n')
        types.append('Navigation Page HTML')
        factory.manage_setPortalFactoryTypes(listOfTypeIds = types)

def uninstall_tool(self, out):
    if hasattr(self, TOOL_ID):
        out.write("CompositePack Tool not removed\n")

def install_kupu_resource(self, out):
    if hasattr(self, KUPU_TOOL_ID):
        kupu_tool = getattr(self, KUPU_TOOL_ID)
        composables = (
            'File',
            'Link',
            'Image',
            'Event',
            'Topic',
            'Document',
            'News Item',
            'CompositePack Titles',
#            'CompositePack Portlet',
            'CompositePack Fragments',
            )
        try:
            kupu_tool.addResourceType(COMPOSABLE, composables)
            out.write("Composable Resource added in Kupu Library Tool\n")
        except KeyError:
            out.write("Composable Resource not added in Kupu Library Tool, already present\n")
    else:
        out.write("Kupu Library Tool not available\n")

def uninstall_kupu_resource(self, out):
    if hasattr(self, KUPU_TOOL_ID):
        kupu_tool = getattr(self, KUPU_TOOL_ID)
        try:
            kupu_tool.deleteResourceTypes([COMPOSABLE])
            out.write("Composable Resource deleted in Kupu Library Tool\n")
        except KeyError:
            pass
    else:
        out.write("Kupu Library Tool not available\n")

def install_customisation(self, out):
    """Default settings may be stored in a customisation policy script so
    that the entire setup may be 'productised'"""

    # Skins are cached during the request so we (in case new skin
    # folders have just been added) we need to force a refresh of the
    # skin.
    self.changeSkin(None)

    scriptname = '%s-customisation-policy' % PROJECTNAME.lower()
    cpscript = getattr(self, scriptname, None)
    if cpscript:
        cpscript = cpscript.__of__(self)

    if cpscript:
        print >>out,"Customising %s" % PROJECTNAME
        print >>out,cpscript()
    else:
        print >>out,"No customisation policy", scriptname

def install_fixuids(self, out):
    # If upgrading from version 0.1.0 the uids may need migrating
    ct = getattr(self, TOOL_ID)
    for id, viewlet in ct.viewlets.objectItems():
        uid = viewlet.UID()
        viewlet.setStableUID()
        if uid != viewlet.UID():
            out.write("Migrated UID for viewlet %s\n" % id)

def installDependencies(self, out):
    qi = self.portal_quickinstaller
    if not qi.isProductInstalled('Archetypes'):
        qi.installProduct('Archetypes',locked=1)
        print >>out, 'Installing Archetypes'
    if not qi.isProductInstalled('kupu'):
        qi.installProduct('kupu')
        print >>out, 'Installing kupu'
    if HAS_ATCT and not qi.isProductInstalled('ATContentTypes'):

        qi.installProduct('ATContentTypes')
        print >>out, 'Installing ATContentTypes'

def addToDefaultPageTypes(self, out):
    # We want a Navigation Page to be selectable as default page in Plone.
    site_props = self.portal_properties.site_properties
    if site_props.hasProperty('default_page_types'):
        dptypes = site_props.getProperty('default_page_types')
        if not 'Navigation Page' in dptypes:
            dptypes = list(dptypes)
            dptypes.append('Navigation Page')
            site_props._updateProperty('default_page_types', dptypes)
            print >>out, 'Added Navigation Page to the list of default page types'

def registerResources(self, out, toolname, resources):
    tool = getToolByName(self, toolname)
    existing = tool.getResourceIds()
    cook = False
    for resource in resources:
        if not resource['id'] in existing:
            # register additional resource in the specified registry...
            if toolname == "portal_css":
                tool.registerStylesheet(**resource)
            if toolname == "portal_javascripts":
                tool.registerScript(**resource)
            print >> out, "Added %s to %s." % (resource['id'], tool)
        else:
            # ...or update existing one
            parameters = tool.getResource(resource['id'])._data
            for key in [k for k in resource.keys() if k != 'id']:
                originalkey = 'original_'+key
                original = parameters.get(originalkey)
                if not original:
                    parameters[originalkey] = parameters[key]
                parameters[key] = resource[key]
                print >> out, "Updated %s in %s." % (resource['id'], tool)
                cook = True
    if cook:
        tool.cookResources()
    print >> out, "Successfuly Installed/Updated resources in %s." % tool

def resetResources(self, out, toolname, resources):
    # Revert resource customizations
    tool = getToolByName(self, toolname)
    for resource in [tool.getResource(r['id']) for r in resources]:
        if resource == None:
            continue
        for key in resource._data.keys():
            originalkey = 'original_'+key
            if resource._data.has_key(originalkey):
                try: # <- BBB
                    resource._data[key] = resource._data[originalkey]['value']
                except TypeError:
                    resource._data[key] = resource._data[originalkey]
                del resource._data[originalkey]

def sort_skins(self):
    STANDARD_SKINS = ('Plone Default', 'Plone Tableless')
    CP_LAYERS = ('compositepack_layouts','compositepack_layouts_azax')
    skintool = getToolByName(self, 'portal_skins')
    skin_selections = skintool.getSkinSelections()
    for skin_selection in skin_selections:
        if skin_selection not in STANDARD_SKINS:
            continue
        path = skintool.getSkinPath(skin_selection)
        path = [p.strip() for p in path.split(',') if p]
        if CP_LAYERS[0] in path and CP_LAYERS[1] in path:
            cl_index = path.index(CP_LAYERS[0])
            cla_index = path.index(CP_LAYERS[1])
            if cl_index < cla_index and HAVEAZAX:
                path[cl_index] = CP_LAYERS[1]
                path[cla_index] = CP_LAYERS[0]
            elif cla_index < cl_index and not HAVEAZAX:
                path[cl_index] = CP_LAYERS[1]
                path[cla_index] = CP_LAYERS[0]
            skintool['selections'][skin_selection] = ",".join(path)
                
def install(self):
    out = StringIO()

    installDependencies(self, out)
    installTypes(self, out, listTypes(PROJECTNAME), PROJECTNAME)
    archetype_tool = getToolByName(self, 'archetype_tool')
    archetype_tool.setCatalogsByType('CompositePack Viewlet', ())   
    archetype_tool.setCatalogsByType('CompositePack Viewlet Container', ())   
    archetype_tool.setCatalogsByType('CompositePack Element', ())   
    archetype_tool.setCatalogsByType('CompositePack Layout', ())   
    archetype_tool.setCatalogsByType('CompositePack Layout Container', ())   
    install_subskin(self, out, GLOBALS)
    # The skins need to be sorted differently depending on whether Azax
    # is available or not.
    sort_skins(self)
    install_tool(self, out)
    install_customisation(self, out)
    registerResources(self, out, 'portal_css', STYLESHEETS)
    registerResources(self, out, 'portal_javascripts', JAVASCRIPTS)
    install_fixuids(self, out)
    if PLONE21:
        setup_portal_factory(self, out)
        addToDefaultPageTypes(self, out)
    install_kupu_resource(self, out)
        
    out.write("Successfully installed %s.\n" % PROJECTNAME)
    return out.getvalue()

def uninstall(self):
    out = StringIO()
    uninstall_tool(self, out)
    uninstall_kupu_resource(self, out)
    resetResources(self, out, 'portal_css', STYLESHEETS)
    resetResources(self, out, 'portal_javascripts', JAVASCRIPTS)
    out.write("Successfully uninstalled %s.\n" % PROJECTNAME)
    return out.getvalue()    
