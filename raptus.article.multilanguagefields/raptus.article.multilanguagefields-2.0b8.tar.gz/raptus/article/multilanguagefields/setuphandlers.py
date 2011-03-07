from raptus.article.multilanguagefields import modifier

from Products.CMFCore.utils import getToolByName

modifiers = [modifier.ArticleModifier,
             modifier.TeaserModifier,
             modifier.AdditionalwysiwygModifier,
             modifier.MapsModifier,
             modifier.MarkerModifier]

indexes = ('SearchableText', 'Subject', 'Title', 'Description', 'sortable_title',)

def reindex(portal):
    catalog = getToolByName(portal, 'portal_catalog')
    for index in indexes:
        catalog.reindexIndex(index, portal.REQUEST)

def install(context):

    if context.readDataFile('raptus.article.multilanguagefields_install.txt') is None:
        return
    
    portal = context.getSite()
    quickinstaller = getToolByName(portal, 'portal_quickinstaller')

    sm = portal.getSiteManager()
    for modifier in modifiers:
        if quickinstaller.isProductInstalled(modifier.for_package):
            sm.registerAdapter(modifier, name='MultilanguageArticle%s' % modifier.__name__)
        
    reindex(portal)
    
def uninstall(context):
    if context.readDataFile('raptus.article.multilanguagefields_install.txt') is None and \
       context.readDataFile('raptus.article.multilanguagefields_uninstall.txt') is None:
        return
    
    portal = context.getSite()
    sm = portal.getSiteManager()
    for modifier in modifiers:
        sm.unregisterAdapter(modifier, name='MultilanguageArticle%s' % modifier.__name__)
        
    reindex(portal)
    