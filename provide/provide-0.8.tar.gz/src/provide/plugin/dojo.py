from provide.plugin.base import ProvisionPlugin
from provide.dictionarywords import DOJO_PATH, DOJO_PREFIX
import os

class Plugin(ProvisionPlugin):

    def runInstaller(self, tarballPath, installPath):
        self.chdir(installPath)
        cmd = "tar zxvf %s" % tarballPath
        if os.system(cmd):
            raise Exception("Couldn't extract tarball %s to %s" % (
                tarballPath, installPath
            ))
        for i in os.listdir(installPath):
            if i[0:4] == 'dojo':
                dojoPathOld = os.path.join(installPath, i)
                dojoPathNew = os.path.join(installPath, 'dojo')
                cmd = "mv %s %s" % (dojoPathOld, dojoPathNew)
                print cmd
                if os.system(cmd):
                    msg = "Couldn't mv extracted dojo source: dojoPathOld"
                    raise Exception(msg)
                break

