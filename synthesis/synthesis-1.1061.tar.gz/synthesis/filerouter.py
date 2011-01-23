#!/usr/bin/env python
import fileutils
from conf import settings

class router:
    
    def moveFile(self, source_file, destination_location):
        fileutils.moveFile(source_file, destination_location)
    
    def moveUsed(self, file_name):
        if settings.DEBUG:
            print "moving ", file_name, "to", settings.USEDFILES_PATH
        fileutils.moveFile(file_name, settings.USEDFILES_PATH)

    def moveFailed(self, fileName):
        fileutils.moveFile(fileName, settings.FAILEDFILES_PATH)

