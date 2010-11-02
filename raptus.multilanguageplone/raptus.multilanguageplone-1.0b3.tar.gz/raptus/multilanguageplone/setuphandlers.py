from archetypes.schemaextender.interfaces import ISchemaExtender

from raptus.multilanguageplone.extender import folder, document, event, file, image, link, newsitem, topic

from Products.CMFCore.utils import getToolByName

extenders = [folder.FolderExtender,
             document.DocumentExtender,
             event.EventExtender,
             file.FileExtender,
             image.ImageExtender,
             link.LinkExtender,
             newsitem.NewsItemExtender,
             topic.TopicExtender,]

try:
    from raptus.multilanguageplone.extender.file import BlobFileExtender, BlobFileModifier
    extenders.append(BlobFileExtender)
    extenders.append(BlobFileModifier)
    from raptus.multilanguageplone.extender.image import BlobImageExtender, BlobImageModifier
    extenders.append(BlobImageExtender)
    extenders.append(BlobImageModifier)
except ImportError:
    pass

indexes = ('SearchableText', 'Subject', 'Title', 'Description', 'sortable_title',)

def reindex(portal):
    catalog = getToolByName(portal, 'portal_catalog')
    for index in indexes:
        catalog.reindexIndex(index, portal.REQUEST)

def install(context):
    if context.readDataFile('raptus.multilanguageplone_install.txt') is None:
        return
    portal = context.getSite()
    
    sm = portal.getSiteManager()
    for extender in extenders:
        sm.registerAdapter(extender, name='Multilanguage%s' % extender.__name__)
    
    reindex(portal)
    
def uninstall(context):
    if context.readDataFile('raptus.multilanguageplone_install.txt') is None and \
       context.readDataFile('raptus.multilanguageplone_uninstall.txt') is None:
        return
    
    portal = context.getSite()
    
    sm = portal.getSiteManager()
    for extender in extenders:
        try:
            sm.unregisterAdapter(extender, name='Multilanguage%s' % extender.__name__)
        except:
            pass
        
    reindex(portal)
    