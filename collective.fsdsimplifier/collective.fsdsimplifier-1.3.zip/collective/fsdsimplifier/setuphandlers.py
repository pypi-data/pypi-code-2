import logging
from zope.interface import noLongerProvides
from Products.CMFCore.utils import getToolByName
from plone.browserlayer.utils import unregister_layer 
from archetypes.schemaextender.interfaces import ISchemaModifier

from collective.fsdsimplifier.browser.interfaces import IFsdSimplifierLayer
from collective.fsdsimplifier.person import PersonModifier

def setupVarious(context):

    # Check that we actually meant for this import step to be run.
    # The file is found in profiles/default.

    if context.readDataFile('collective.fsdsimplifier_various.txt') is None:
        return 

    site = context.getSite()
    
    # remove incorrectly configured FSD types from versioning configuration
    pr = getToolByName(site, 'portal_repository')
    versionable_types = [t for t in pr.getVersionableContentTypes() if not t.startswith('FSD')]
    pr.setVersionableContentTypes(versionable_types)
    
    # update workflow mappings
    wf = getToolByName(site, 'portal_workflow')
    wf.updateRoleMappings()
    
def removeVarious(context):

    # Check that we actually meant for this import step to be run.
    # The file is found in profiles/uninstall.

    if context.readDataFile('collective.fsdsimplifier_removevarious.txt') is None:
        return

    site = context.getSite()

    # update workflow mappings
    wf = getToolByName(site, 'portal_workflow')
    wf.updateRoleMappings()

    # Remove the FSD-Simplifier layer
    unregister_layer(name='collective.fsdsimplifier')
    noLongerProvides(site, IFsdSimplifierLayer)
    
    # Unregister the adapter
    sm = site.getSiteManager()
    extenderClass = PersonModifier
    sm.unregisterAdapter(extenderClass, provided=ISchemaModifier)
 
def upgrade_to_1_3(context, logger=None):
    """Update actions configuration
    """
	
    if logger is None:
        # Called as upgrade step: define our own logger.
        logger = logging.getLogger('collective.fsdsimplifier')
		
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile('profile-collective.fsdsimplifier:default', 'actions')
	
    logger.info("Upgraded to version 1.3")
