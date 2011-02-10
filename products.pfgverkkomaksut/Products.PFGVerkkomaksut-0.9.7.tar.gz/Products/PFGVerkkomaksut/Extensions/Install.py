from Products.CMFCore.utils import getToolByName
from Products.Archetypes.Extensions.utils import installTypes
from Products.Archetypes.Extensions.utils import install_subskin
from Products.Archetypes.public import listTypes
from StringIO import StringIO
from Products.PFGVerkkomaksut.config import (
    PROJECTNAME,
    product_globals,
)

def install(self):
    out = StringIO()
    print >> out, "Installing PFGVerkkomaksut"

    # Install types
    classes = listTypes(PROJECTNAME)
    installTypes(self, out,
                 classes,
                 PROJECTNAME)
    print >> out, "Installed types"

    # Install skin
    install_subskin(self, out, product_globals)
    print >> out, "Installed skin"

    # Enable portal_factory
    factory = getToolByName(self, 'portal_factory')
    types = factory.getFactoryTypes().keys()
    if 'PFGVerkkomaksut' not in types:
        types.append('PFGVerkkomaksut')
        factory.manage_setPortalFactoryTypes(listOfTypeIds = types)

    print >> out, "Added PFGVerkkomaksut to portal_factory"

    propsTool = getToolByName(self, 'portal_properties')
    siteProperties = getattr(propsTool, 'site_properties')
    navtreeProperties = getattr(propsTool, 'navtree_properties')

    # Remove from use_folder_tabs
    useFolderTabs = list(siteProperties.getProperty('use_folder_tabs'))
    if 'PFGVerkkomaksut' in useFolderTabs:
        useFolderTabs.remove('PFGVerkkomaksut')
    siteProperties.manage_changeProperties(use_folder_tabs = useFolderTabs)

    # Remove from typesLinkToFolderContentsInFC 
    typesLinkToFolderContentsInFC = list(siteProperties.getProperty('typesLinkToFolderContentsInFC'))
    if 'PFGVerkkomaksut' in typesLinkToFolderContentsInFC:
        typesLinkToFolderContentsInFC.remove('PFGVerkkomaksut')
    siteProperties.manage_changeProperties(typesLinkToFolderContentsInFC = typesLinkToFolderContentsInFC)

    # Allow PFGVerkkomaksut to be added to FormFolder
    pt = getToolByName(self, 'portal_types')
    allowed_types = list(pt['FormFolder'].allowed_content_types)
    pfgv = 'PFGVerkkomaksut'
    if pfgv not in allowed_types:
        allowed_types.append(pfgv)
        pt['FormFolder'].allowed_content_types = allowed_types
    print >> out, "Installed types"

    propsTool = getToolByName(self, 'portal_properties')
    siteProperties = getattr(propsTool, 'site_properties')
    navtreeProperties = getattr(propsTool, 'navtree_properties')

    # Add PFGVerkkomaksut to types_not_searched
    typesNotSearched = list(siteProperties.getProperty('types_not_searched'))
    if pfgv not in typesNotSearched:
        typesNotSearched.append(pfgv)
    siteProperties.manage_changeProperties(types_not_searched = typesNotSearched)
    print >> out, "Added form fields & adapters to types_not_searched"

    # Add the field, fieldset, thanks and adapter types to types excluded from navigation
    typesNotListed = list(navtreeProperties.getProperty('metaTypesNotToList'))
    if pfgv not in typesNotListed:
        typesNotListed.append(pfgv)
    navtreeProperties.manage_changeProperties(metaTypesNotToList = typesNotListed)
    print >> out, "Added form fields & adapters to metaTypesNotToList"


    # Set up the workflow for the field, fieldset, thanks and adapter types: there should be none!
    wft = getToolByName(self, 'portal_workflow')
    wft.setChainForPortalTypes(('PFGVerkkomaksut',), ())
    print >> out, "Set up empty adapter workflow."

    return out.getvalue()
