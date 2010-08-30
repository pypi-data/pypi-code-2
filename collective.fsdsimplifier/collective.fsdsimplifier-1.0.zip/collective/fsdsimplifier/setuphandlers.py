from Products.CMFCore.utils import getToolByName

def setupVarious(context):

    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a
    # flag to check that we actually meant for this import step to be run.
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

    if context.readDataFile('collective.fsdsimplifier_removevarious.txt') is None:
        return

    site = context.getSite()

    # update workflow mappings
    wf = getToolByName(site, 'portal_workflow')
    wf.updateRoleMappings()
        
