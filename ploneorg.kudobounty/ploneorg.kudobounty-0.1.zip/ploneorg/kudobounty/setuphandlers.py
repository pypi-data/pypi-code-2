from ploneorg.kudobounty.config import FORM_ID
from ploneorg.kudobounty.config import TOPIC_ID
from ploneorg.kudobounty.config import CONTAINER_ID
from ploneorg.kudobounty.config import CONTAINER_TITLE

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from Products.ATContentTypes.lib import constraintypes

from Products.GenericSetup.context import TarballExportContext, TarballImportContext
from Products.GenericSetup.interfaces import IFilesystemExporter, IFilesystemImporter

CREATE_SCRIPT_BODY = """
formProcessor = ploneformgen.restrictedTraverse('@@processBountyForm')
formProcessor()
return {}
"""

def createTopic(container, wftool, logger):
    """
    Located in: /bounty-mission/aggregator
    Item Type = ["Bounty Program Submission",]
    state = ['published',]
    sort_on = "creation"    
    """
    topic = getattr(container, TOPIC_ID, None)
    if topic is None:
        # Add criteria
        _createObjectByType('Topic', container, id=TOPIC_ID,
                            title=CONTAINER_TITLE)
        topic = getattr(container, TOPIC_ID, None)
        crit = topic.addCriterion('Type','ATPortalTypeCriterion')
        crit.setValue(["Bounty Program Submission",])
        crit = topic.addCriterion('review_state','ATSelectionCriterion')
        crit.setValue("published")
        crit = topic.addCriterion('created','ATSortCriterion') 
        topic.setLayout('folder_summary_view')
        topic.unmarkCreationFlag()

        if wftool.getInfoFor(topic, 'review_state') != 'published':
            wftool.doActionFor(topic, 'publish')
        
        logger.info("Bounty submissions aggregator added")
    else:
        logger.info("Bounty submissions aggregator already exist at %s" % \
                    topic.absolute_url())

def createPFGForm(context, container, wftool, logger):
    """
    """
    form = getattr(container, FORM_ID, None)
    if form is None:
        container.invokeFactory(id=FORM_ID, type_name="FormFolder",
                               title="Bounty Submission Form")
        form = getattr(container, FORM_ID)
        # cleanup form and import data from the archive
        form.manage_delObjects(ids=form.objectIds())
        pfg_data = context.readDataFile("submissions-form.tar.gz")
        ctx = TarballImportContext(form, pfg_data)
        IFilesystemImporter(form).import_(ctx, 'structure', True)
        # Fix importing PFG via GS bug
        #   - it adds extra indentation, wchich breaks the script.
        create_bounty_script = form["create-bounty-submission"]
        create_bounty_script.setScriptBody(CREATE_SCRIPT_BODY)
        # Update and pubhish the form
        form.update(**{"actionAdapter":["create-bounty-submission",],})
        form.unmarkCreationFlag()
        form.reindexObject()
        if wftool.getInfoFor(form, 'review_state') != 'published':
            wftool.doActionFor(form, 'publish')
        logger.info("Bounty submission form created") 
    else:
        logger.info("Bounty submissions form already exist at %s" % \
                    form.absolute_url())

def createStructure(context, logger):
    site = context.getSite()
    wftool = getToolByName(site, "portal_workflow")

    # CONTAINER
    folder = getattr(site, CONTAINER_ID, None)
    if  folder is None:
        _createObjectByType('Folder', site, id=CONTAINER_ID,
                            title=CONTAINER_TITLE)
        folder = getattr(site, CONTAINER_ID)
        folder.setOrdering('unordered')
        folder.setConstrainTypesMode(constraintypes.ENABLED)
        #folder.setLocallyAllowedTypes(["Bounty Program Submission"])
        #folder.setImmediatelyAddableTypes(["Bounty Program Submission"])
        folder.setDefaultPage(TOPIC_ID)
        folder.unmarkCreationFlag()

        if wftool.getInfoFor(folder, 'review_state') != 'published':
            wftool.doActionFor(folder, 'publish')

        logger.info("Submissions container added")
    else:
        logger.info("Submissions container already exist at %s" % \
                    folder.absolute_url())

    createTopic(folder, wftool, logger)
    createPFGForm(context, folder, wftool, logger)


def addPortletsToPortal(context, logger):
    site = context.getSite()
    setup_tool = getToolByName(site, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile(
        "profile-ploneorg.kudobounty:portlets", purge_old=False)


def importVarious(context):
    """ Various import steps
    """
    if context.readDataFile('ploneorg_kudobounty.txt') is None:
        return
    logger = context.getLogger("ploneorg.kudobounty")
    createStructure(context, logger)
    addPortletsToPortal(context, logger)

