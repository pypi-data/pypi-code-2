from Products.CMFCore.utils import getToolByName

def setupFileExchange(context):
    # XXX: Since this is run an as extension profile, this shouldn't be
    # needed IMHO, but GS will run this step again if RD has been inspected
    # for an import_steps.xml again.
    if context.readDataFile('fileexchange_various.txt') is None:
        return

    portal = context.getSite()

    mtool = getToolByName(portal, 'portal_membership')
    mtool.memberareaCreationFlag = True