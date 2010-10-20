"""Definition of the FileExchangeContainer content type.
"""

from zope.interface import implements

try:
  from Products.LinguaPlone.public import *
except ImportError:
  # No multilingual support
  from Products.Archetypes.public import *

from Products.ATContentTypes.content.base import ATCTFolder

from Products.CMFPlone.interfaces import INonStructuralFolder

from Products.FileExchange.interfaces import IFileExchangeContainer
from Products.FileExchange.config import PROJECTNAME

FileExchangeContainer_schema = OrderedBaseFolder.schema.copy()

for field in FileExchangeContainer_schema.keys():
    if field is not 'title':
        FileExchangeContainer_schema[field].widget.visible = {'edit': 'invisible', 'view': 'invisible'}

class FileExchangeContainer(OrderedBaseFolder, ATCTFolder):
    """A container for file attachments used for the fileexchange"""
    implements(IFileExchangeContainer, INonStructuralFolder)

    portal_type = meta_type = "FileExchange Container"
    _at_rename_after_creation = True
    schema = FileExchangeContainer_schema

    def canSetDefaultPage(self):
        return False

registerType(FileExchangeContainer, PROJECTNAME)