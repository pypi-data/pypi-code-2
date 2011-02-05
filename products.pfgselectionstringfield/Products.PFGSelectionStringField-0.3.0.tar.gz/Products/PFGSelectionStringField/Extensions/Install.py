from StringIO import StringIO
import transaction
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.Extensions.utils import installTypes
from Products.Archetypes.Extensions.utils import install_subskin
from Products.Archetypes.public import listTypes
from Products.PFGSelectionStringField.config import PROJECTNAME, product_globals
PRODUCT_DEPENDENCIES = ('PloneFormGen',)

def install(self, reinstall=False):
    out = StringIO()
    print >> out, "Installing PFGSelectionStringField"

    # Install dependencies
    installer = getToolByName(self, 'portal_quickinstaller')
    for product in PRODUCT_DEPENDENCIES:
        if reinstall and installer.isProductInstalled(product):
            installer.installProducts([product],reinstall=True)
            transaction.savepoint()
        elif not installer.isProductInstalled(product):
            installer.installProducts([product])
            transaction.savepoint()

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
    if 'PFGSelectionStringField' not in types:
        types.append('PFGSelectionStringField')
        factory.manage_setPortalFactoryTypes(listOfTypeIds = types)

    print >> out, "Added PFGSelectionStringField to portal_factory"

    propsTool = getToolByName(self, 'portal_properties')
    siteProperties = getattr(propsTool, 'site_properties')

    # Remove from use_folder_tabs
    useFolderTabs = list(siteProperties.getProperty('use_folder_tabs'))
    if 'PFGSelectionStringField' in useFolderTabs:
        useFolderTabs.remove('PFGSelectionStringField')
    siteProperties.manage_changeProperties(use_folder_tabs = useFolderTabs)

    # Remove from typesLinkToFolderContentsInFC 
    typesLinkToFolderContentsInFC = list(siteProperties.getProperty('typesLinkToFolderContentsInFC'))
    if 'PFGSelectionStringField' in typesLinkToFolderContentsInFC:
        typesLinkToFolderContentsInFC.remove('PFGSelectionStringField')
    siteProperties.manage_changeProperties(typesLinkToFolderContentsInFC = typesLinkToFolderContentsInFC)

    # Allow PFGSelectionStringField to be added to FormFolder
    pt = getToolByName(self, 'portal_types')
    allowed_types = list(pt['FormFolder'].allowed_content_types)
    pfgv = 'PFGSelectionStringField'
    if pfgv not in allowed_types:
        allowed_types.append(pfgv)
        pt['FormFolder'].allowed_content_types = allowed_types
    print >> out, "Installed types"

    propsTool = getToolByName(self, 'portal_properties')
    siteProperties = getattr(propsTool, 'site_properties')
    navtreeProperties = getattr(propsTool, 'navtree_properties')

    # Add PFGSelectionStringField to types_not_searched
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
    wft.setChainForPortalTypes(('PFGSelectionStringField',), ())
    print >> out, "Set up empty field workflow."

    return out.getvalue()
