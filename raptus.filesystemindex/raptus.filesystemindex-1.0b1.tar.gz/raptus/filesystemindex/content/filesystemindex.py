"""Definition of the FileSystemIndex content type
"""
from zope.interface import implements

from plone.indexer import indexer

from Products.Archetypes import atapi
from Products.ATContentTypes.content import document
from Products.ATContentTypes.content import schemata
from Products.validation import V_REQUIRED

from raptus.filesystemindex.interfaces import IFileSystemIndex
from raptus.filesystemindex.config import PROJECTNAME
from raptus.filesystemindex import _

@indexer(IFileSystemIndex)
def is_folderish(obj):
    return True

FileSystemIndexSchema = document.ATDocumentSchema.copy() + atapi.Schema((
                                                                            
        atapi.StringField(
            'fileSystemPath',
            storage = atapi.AnnotationStorage(),
            required=True,
            widget = atapi.StringWidget(
                label = _(u'label_filesystempath', default=u'Filesystem path'),
                description=_(u'help_filesystempath',
                              default=u'The path of the folder to be displayed.'),
                ),
        ),
                                                                            
        atapi.StringField(
            'winMount',
            storage = atapi.AnnotationStorage(),
            widget = atapi.StringWidget(
                label = _(u'label_winmount', default=u'Windows mount path'),
                description=_(u'help_winmount',
                              default=u'The path to the folder when mounted on a windows machine.'),
                ),
        ),
                                                                            
        atapi.StringField(
            'unixMount',
            storage = atapi.AnnotationStorage(),
            widget = atapi.StringWidget(
                label = _(u'label_unixmount', default=u'Unix mount path'),
                description=_(u'help_unixmount',
                              default=u'The path to the folder when mounted on a unix machine.'),
                ),
        ),

    ))

FileSystemIndexSchema['title'].storage = atapi.AnnotationStorage()
FileSystemIndexSchema['description'].storage = atapi.AnnotationStorage()

for field in ('creators','allowDiscussion','contributors','location','language', 'nextPreviousEnabled', 'rights' ):
    if FileSystemIndexSchema.has_key(field):
        FileSystemIndexSchema[field].widget.visible = {'edit': 'invisible', 'view': 'invisible'}

schemata.finalizeATCTSchema(FileSystemIndexSchema, folderish=False, moveDiscussion=True)



class FileSystemIndex(document.ATDocument):
    """A folder showing the contents of a folder on the filesystem"""
    implements(IFileSystemIndex)
    
    portal_type = "FileSystemIndex"
    schema = FileSystemIndexSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    fileSystemPath = atapi.ATFieldProperty('fileSystemPath')
    winMount = atapi.ATFieldProperty('winMount')
    unixMount = atapi.ATFieldProperty('unixMount')

atapi.registerType(FileSystemIndex, PROJECTNAME)
