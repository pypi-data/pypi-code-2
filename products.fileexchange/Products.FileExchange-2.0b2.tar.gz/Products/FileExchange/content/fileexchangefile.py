from zope.interface import implements

from Products.ATContentTypes.content.file import ATFile
from Products.Archetypes.public import registerType
from Products.FileExchange.config import PROJECTNAME, MODIFY_PERMISSION
from Products.FileExchange.interfaces import IFileExchangeFile

FileExchangeFile_Schema = ATFile.schema.copy()
FileExchangeFile_Schema['title'].write_permission = MODIFY_PERMISSION
FileExchangeFile_Schema['file'].write_permission = MODIFY_PERMISSION

class FileExchangeFile(ATFile):
    """A file"""

    implements(IFileExchangeFile)

    schema = FileExchangeFile_Schema
    portal_type = meta_type = 'FileExchange File'

registerType(FileExchangeFile, PROJECTNAME)

