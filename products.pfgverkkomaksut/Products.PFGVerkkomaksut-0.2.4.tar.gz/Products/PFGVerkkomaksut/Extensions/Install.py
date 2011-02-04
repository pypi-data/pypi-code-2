from Products.CMFCore.utils import getToolByName
from Products.CMFFormController.FormAction import FormActionKey
from Products.Archetypes.Extensions.utils import installTypes
from Products.Archetypes.Extensions.utils import install_subskin
from Products.Archetypes.public import listTypes

from StringIO import StringIO

#from Products.CMFDynamicViewFTI.migrate import migrateFTIs

from Products.PFGVerkkomaksut.config import *
#from Products.PFGVerkkomaksut.Extensions.utils import *

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

#    # Migrate FTI, to make sure we get the necessary infrastructure for the
#    # 'display' menu to work.
#    migrated = migrateFTIs(self, product=PROJECTNAME)
#    print >>out, "Switched to DynamicViewFTI: %s" % ', '.join(migrated)

#    # Install stylesheet
#    portal_css = getToolByName(self, 'portal_css')
#    portal_css.manage_addStylesheet(id = 'richdocument.css',
#                                    expression = 'python:object.getTypeInfo().getId() == "PFGVerkkomaksut"',
#                                    media = 'all',
#                                    title = 'PFGVerkkomaksut styles',
#                                    enabled = True)

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
#    if hasattr(self.aq_explicit, '_v_pfg_old_allowed_types'):
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
#    for f in fieldTypes + adapterTypes + thanksTypes + fieldsetTypes:
#        if f not in typesNotSearched:
#            typesNotSearched.append(f)
    if pfgv not in typesNotSearched:
        typesNotSearched.append(pfgv)
    siteProperties.manage_changeProperties(types_not_searched = typesNotSearched)
    print >> out, "Added form fields & adapters to types_not_searched"

    # Add the field, fieldset, thanks and adapter types to types excluded from navigation
    typesNotListed = list(navtreeProperties.getProperty('metaTypesNotToList'))
#    for f in fieldTypes + adapterTypes + thanksTypes + fieldsetTypes:
#        if f not in typesNotListed:
#            typesNotListed.append(f)
    if pfgv not in typesNotListed:
        typesNotListed.append(pfgv)
    navtreeProperties.manage_changeProperties(metaTypesNotToList = typesNotListed)
    print >> out, "Added form fields & adapters to metaTypesNotToList"


    # Set up the workflow for the field, fieldset, thanks and adapter types: there should be none!
    wft = getToolByName(self, 'portal_workflow')
    wft.setChainForPortalTypes(('PFGVerkkomaksut',), ())
    print >> out, "Set up empty adapter workflow."

#    # Add to default_page_types
#    defaultPageTypes = list(siteProperties.getProperty('default_page_types'))
#    if 'PFGVerkkomaksut' not in defaultPageTypes:
#        defaultPageTypes.append('PFGVerkkomaksut')
#    siteProperties.manage_changeProperties(default_page_types = defaultPageTypes)

#    # Add to parentMetaTypesNotToQuery
#    parentMetaTypesNotToQuery = list(navtreeProperties.getProperty('parentMetaTypesNotToQuery'))
#    if 'PFGVerkkomaksut' not in parentMetaTypesNotToQuery:
#        parentMetaTypesNotToQuery.append('PFGVerkkomaksut')
#    navtreeProperties.manage_changeProperties(parentMetaTypesNotToQuery = parentMetaTypesNotToQuery)

#    # Set up form controller actions for the widgets to work
#    registerAttachmentsFormControllerActions(self, contentType = 'PFGVerkkomaksut', template = 'atct_edit')
#    registerImagesFormControllerActions(self, contentType = 'PFGVerkkomaksut', template = 'atct_edit')
#    print >> out, "Added actions for the image and attachment controls to the atct_edit form controller."

#    # Register form controller actions for LinguaPlone translate_item
#    registerAttachmentsFormControllerActions(self, contentType = 'PFGVerkkomaksut', template = 'translate_item')
#    registerImagesFormControllerActions(self, contentType = 'PFGVerkkomaksut', template = 'translate_item')
#    print >> out, "Added actions for the image and attachment controls to the translate_item form controller."

#    # Set up the workflow for the widget types
#    setupFileAttachmentWorkflow(self)
#    setupImageAttachmentWorkflow(self)
#    print >> out, "Set up FileAttachment and ImageAttachment workflows."

#    # Make the widget types use the /view action when linked to
#    setupFileAttachmentView(self)
#    setupImageAttachmentView(self)
#    print >> out, "Set up FileAttachment and ImageAttachment to use /view."

#    # Add the FileAttachment and ImageAttachment types to types_not_searched
#    # (this is configurable via the Search settings control panel)
#    typesNotSearched = list(siteProperties.getProperty('types_not_searched'))
#    if 'FileAttachment' not in typesNotSearched:
#        typesNotSearched.append('FileAttachment')
#    if 'ImageAttachment' not in typesNotSearched:
#        typesNotSearched.append('ImageAttachment')
#    siteProperties.manage_changeProperties(types_not_searched = typesNotSearched)
#    print >> out, "Added FileAttachment and ImageAttachment to types_not_searched"

#    # Add FileAttachment and ImageAttachment to kupu's linkable and media
#    # types
#    kupuTool = getToolByName(self, 'kupu_library_tool')
#    linkable = list(kupuTool.getPortalTypesForResourceType('linkable'))
#    mediaobject = list(kupuTool.getPortalTypesForResourceType('mediaobject'))
#    if 'FileAttachment' not in linkable:
#        linkable.append('FileAttachment')
#    if 'ImageAttachment' not in linkable:
#        linkable.append('ImageAttachment')
#    if 'PFGVerkkomaksut' not in linkable:
#        linkable.append('PFGVerkkomaksut')
#    if 'ImageAttachment' not in mediaobject:
#        mediaobject.append('ImageAttachment')
#    # kupu_library_tool has an idiotic interface, basically written purely to
#    # work with its configuration page. :-(
#    kupuTool.updateResourceTypes(({'resource_type' : 'linkable',
#                                   'old_type'      : 'linkable',
#                                   'portal_types'  :  linkable},
#                                  {'resource_type' : 'mediaobject',
#                                   'old_type'      : 'mediaobject',
#                                   'portal_types'  :  mediaobject},))
#    print >> out, "Added FileAttachment and ImageAttachment to kupu's linkable and mediaobject types"

    return out.getvalue()
