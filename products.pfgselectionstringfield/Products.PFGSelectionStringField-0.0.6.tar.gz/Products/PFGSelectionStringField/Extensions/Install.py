from Products.CMFCore.utils import getToolByName
#from Products.CMFFormController.FormAction import FormActionKey
from Products.Archetypes.Extensions.utils import installTypes
from Products.Archetypes.Extensions.utils import install_subskin
from Products.Archetypes.public import listTypes

from StringIO import StringIO

#from Products.CMFDynamicViewFTI.migrate import migrateFTIs

from Products.PFGSelectionStringField.config import PROJECTNAME, product_globals

def install(self):
    out = StringIO()
    print >> out, "Installing PFGSelectionStringField"

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
#    navtreeProperties = getattr(propsTool, 'navtree_properties')

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
#    if hasattr(self.aq_explicit, '_v_pfg_old_allowed_types'):
    pt = getToolByName(self, 'portal_types')
    allowed_types = list(pt['FormFolder'].allowed_content_types)
    pfgv = 'PFGSelectionStringField'
    if pfgv not in allowed_types:
        allowed_types.append(pfgv)
        pt['FormFolder'].allowed_content_types = allowed_types
    print >> out, "Installed types"

    # Set up the workflow for the field, fieldset, thanks and adapter types: there should be none!
    wft = getToolByName(self, 'portal_workflow')
    wft.setChainForPortalTypes(('PFGSelectionStringField',), ())
    print >> out, "Set up empty field workflow."

    return out.getvalue()
