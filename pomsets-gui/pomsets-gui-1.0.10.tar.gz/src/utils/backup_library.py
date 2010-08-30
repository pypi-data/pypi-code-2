import sys
import os
import user

import pomsets_app.utils as UtilsModule

def main(args):

    configDir = UtilsModule.getDefaultConfigDir()
    libraryDir = os.path.join(configDir, 'library')

    UtilsModule.backupLibrary(libraryDir)
    
    return


if __name__=="__main__":
    main(sys.argv)
