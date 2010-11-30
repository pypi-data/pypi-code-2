
from OFS.Folder import Folder

import logging
log = logging.getLogger('anthill.customexport')

def patch_ofs_folder():
    Folder.manage_options += \
            ({'label' : 'FS-Export', 'action' : '@@customexport', }, )

log.info('Patching OFS.interfaces.IFolder to make export of custom folder possible')
