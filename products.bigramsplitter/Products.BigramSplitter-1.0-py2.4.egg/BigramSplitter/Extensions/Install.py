
from Products.CMFCore.utils import getToolByName

# def install(portal):
#     setup_tool = getToolByName(portal, 'portal_setup')
#     setup_tool.runAllImportStepsFromProfile('profile-Products.BigramSplitter:default')
#     return "Ran all import steps."

def uninstall(portal):
    catalog_tool = getToolByName(portal, 'portal_catalog')    
    catalog_tool._delObject("bigram_lexicon")
    index_ids = ('Title', 'Description', 'SearchableText')
    for idx_id in index_ids:
        catalog_tool.delIndex(idx_id)
    
    setup_tool = getToolByName(portal, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile('profile-Products.BigramSplitter:remove')
    return "Ran all uninstall steps."