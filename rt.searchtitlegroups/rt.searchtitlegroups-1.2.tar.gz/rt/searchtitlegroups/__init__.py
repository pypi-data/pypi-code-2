from Products.PlonePAS.tools.groups import GroupsTool, NotSupported

def updateGroup(self,id,mapping):
    success=0
    managers = self._getGroupManagers()
    if not managers:
        raise NotSupported, 'No plugins allow for group management'
    for mid, manager in managers:
        success = manager.updateGroup(id,
                                      title=mapping.get('title', ''),
                                      description=mapping.get('description', ''))
    return success
        
GroupsTool.updateGroup = updateGroup

from Products.CMFCore.DirectoryView import registerDirectory
from config import SKINS_DIR, GLOBALS

registerDirectory(SKINS_DIR, GLOBALS)

