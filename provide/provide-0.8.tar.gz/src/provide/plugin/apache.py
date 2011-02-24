from provide.plugin.base import ProvisionPlugin
import os, os.path

# Todo: Verify download integrity of (mirrored) downloads.

class Plugin(ProvisionPlugin):

    tarballBaseName = 'httpd'

    def assertServicePurpose(self, *args, **kwds):
        pass

    def runInstaller(self, *args, **kwds):
        pass

    def createServiceDirs(self, service):
        super(Plugin, self).createServiceDirs(service)
        builder = ApacheBuilder(self, service)
        builder.build()


class ApacheBuilder(object):

    def __init__(self, plugin, service):
        self.plugin = plugin
        self.service = service
        self.httpdName = 'httpd-%s' % service.application.name
        self.httpdProgramName = 'apache2provided'
        self.httpdPort = '80'
        self.targetPath = self.plugin.makeInstallPath(service) 
 
    def build(self):
        # setup
        self.checkSystem()
        self.checkSource()
        self.assertTargetExists()
        # apache
        self.enterTargetDir()
        self.extractHttpdSource()
        self.enterHttpdSource()
        self.configureHttpdSource()
        self.make()
        self.makeInstall()
        # mod_python
        self.enterTargetDir()
        self.extractModPythonSource()
        self.fixModPythonSource()
        self.enterModPythonSource()
        self.configureModPythonSource()
        self.make()
        self.makeInstallDso()
        self.fixModPythonConfig()
        # serf
        self.enterTargetDir()
        self.extractSerfSource()
        self.enterSerfSource()
        self.configureSerfSource()
        self.make()
        self.makeInstall()
        # mod_svn, mod_svn_dav
        self.enterTargetDir()
        self.extractModSvnSource()
        self.enterModSvnSource()
        self.configureModSvnSource()
        self.make()
        self.makeInstall()
        # mod_fastcgi
        self.enterTargetDir()
        self.extractModFastcgiSource()
        self.enterModFastcgiSource()
        self.configureModFastcgiSource()
        self.makeModFastcgi()
        self.makeModFastcgiInstall()
        self.fixModFastcgiConfig()
        # teardown
        self.enterTargetDir()
        self.removeModFastcgiSource()
        self.removeModSvnSource()
        self.removeSerfSource()
        self.removeModPythonSource()
        self.removeHttpdSource()
        print "OK"
        return
    
    def getDependency(self, name):
        return self.service.application.dependencies[name]

    def checkSystem(self):
        # Debian-specific package management.
        cmd = "sudo aptitude install libssl-dev"
        msg = "install libssl-dev"
        self.plugin.system(cmd, msg)
        cmd = "sudo aptitude remove libapr1-dev"
        msg = "remove libapr1-dev"
        self.plugin.system(cmd, msg)

    def checkSource(self):
        path = self.plugin.makeApplicationTarballPath(self.service.application)
        self.checkFile(path)
        for name in ['mod_python', 'subversion', 'mod_fastcgi', 'serf']:
            dependency = self.getDependency(name)
            path = self.plugin.makeDependencyPath(dependency)
            self.checkFile(path)

    def checkFile(self, path):
        print "Checking file exists %s" % path
        if not os.path.exists(path):
            raise Exception("No file found: %s" % path)

    def assertTargetExists(self):
        print "Checking target path exists: %s" % self.targetPath
        if not os.path.exists(self.targetPath):
            raise Exception("Target doesn't exist: %s" % self.targetPath)

    def enterTargetDir(self):
        print "Entering target dirs: %s" % self.targetPath
        self.plugin.chdir(self.targetPath)

    def extractHttpdSource(self):
        tarballPath = self.plugin.makeApplicationTarballPath(self.service.application)
        print "Extracting Apache source: %s" % tarballPath
        cmd = 'tar zxvf %s' % tarballPath
        msg = "extract Apache source: %s" % tarballPath
        self.plugin.system(cmd, msg)

    def makeApacheSourceDirPath(self):
        tarballPath = self.plugin.makeApplicationTarballPath(self.service.application)
        dirName = self.getArchiveDirName(tarballPath)
        return os.path.join(self.targetPath, dirName)

    def makeDependencySourceDirPath(self, name):
        tarballPath = self.plugin.makeDependencyPath(self.getDependency(name))
        dirName = self.getArchiveDirName(tarballPath)
        return os.path.join(self.targetPath, dirName)

    def enterHttpdSource(self):
        sourcePath = self.makeApacheSourceDirPath()
        print "Entering httpd source dirs: %s" % sourcePath
        self.plugin.chdir(sourcePath)

    def getArchiveDirName(self, archivePath):
        return archivePath.split('/')[-1].split('.tar.gz')[0].split('.tgz')[0].split('.tar.bz2')[0]

    def configureHttpdSource(self):
        print "Configuring Apache source..."
        cmd = './configure --prefix=%s/apache --enable-dav --enable-dav-fs --enable-ssl --with-program-name=%s --with-port=%s --with-mpm=worker' % (self.targetPath, self.httpdProgramName, self.httpdPort)
        msg = "configure Apache source"
        self.plugin.system(cmd, msg)

    def make(self):
        print "Running make..."
        cmd = 'make'
        msg = "run 'make'"
        self.plugin.system(cmd, msg)

    def makeInstall(self):
        print "Running make install..."
        cmd = 'make install'
        msg = "run 'make install'"
        self.plugin.system(cmd, msg)

    def extractModPythonSource(self):
        path = self.plugin.makeDependencyPath(self.getDependency('mod_python'))
        print "Extracting modPython '%s' source..." % path
        cmd = 'tar zxvf %s' % path
        msg = "extract mod_python source: %s" % path
        self.plugin.system(cmd, msg)

    def enterModPythonSource(self):
        path = self.makeDependencySourceDirPath('mod_python')
        print "Entering mod_python source: %s" % path
        self.plugin.chdir(path)

    def fixModPythonSource(self):
        print "Fixing mod_python source (APR_BRIGADE_SENTINEL issue)..."
        cmd = "perl -pi -e 's/APR_BRIGADE_SENTINEL\(b\)/APR_BRIGADE_SENTINEL(bb)/' `find . -name connobject\.c`"
        msg = "fix mod_python source (APR_BRIGADE_SENTINEL issue)"
        self.plugin.system(cmd, msg)

    def configureModPythonSource(self):
        print "Configuring modPython source..."
        cmd = './configure --with-apxs=%s/apache/bin/apxs --prefix=%s' % (self.targetPath, self.targetPath)
        msg = "configure mod_python source"
        self.plugin.system(cmd, msg)

    def fixModPythonConfig(self):
        cmd = "perl -pi -e 's/# LoadModule foo_module modules\/mod_foo\.so/# LoadModule foo_module modules\/mod_foo.so\nLoadModule python_module     modules\/mod_python.so/' %s/apache/conf/%s.conf" %(self.targetPath, self.httpdProgramName)
        msg = "fix Apache config for mod_python"
        self.plugin.system(cmd, msg)

    def makeInstallDso(self):
        print "Running make install_dso..."
        cmd = 'make install_dso'
        msg = "run 'make install_dso'"
        self.plugin.system(cmd, msg)

    def extractSerfSource(self):
        path = self.plugin.makeDependencyPath(self.getDependency('serf'))
        print "Extracting Serf source: %s" % path
        cmd = 'tar jxvf %s' % path
        msg = "extract Serf source: %s" % path
        self.plugin.system(cmd, msg)

    def enterSerfSource(self):
        path = self.makeDependencySourceDirPath('serf')
        print "Entering Serf source: %s" % path
        self.plugin.chdir(path)

    def makeAprOneConfigPath(self):
        # Decide which apr-1-config script to use.
        import commands
        (whichErrStatus, whichCmdOutput) = commands.getstatusoutput('which apr-1-config')
        if whichErrStatus == 0:
            aprOneConfigPath = whichCmdOutput
        elif whichCmdOutput == '':
            aprOneConfigPath = "%s/apache/bin/apr-1-config" % self.targetPath
        else:
            msg = "Error executing 'which' command: %s" % whichCmdOutput 
        if not os.path.exists(aprOneConfigPath):
            raise Exception("Can't figure out where 'apr-1-config' is. Not on path and not in Apache installation. Debian package 'libapr1-dev' does provide '/usr/bin/apr-1-config', but Apache should build it if it's not installed. So, something is up with the Apache build, but you can get round this by installing the correct Apache runtime development files.")
        return aprOneConfigPath
            
    def configureSerfSource(self):
        httpdSrcPath = self.makeApacheSourceDirPath()
        print "Configuring Serf source..."
        aprOneConfigPath = self.makeAprOneConfigPath()
        cmd = "./configure --prefix=%s/serf --with-apr=%s --with-apr-util=%s/srclib/apr-util/" % (self.targetPath, aprOneConfigPath, httpdSrcPath)
        msg = "configure Serf source"
        self.plugin.system(cmd, msg)

    def extractModSvnSource(self):
        path = self.plugin.makeDependencyPath(self.getDependency('subversion'))
        print "Extracting subversion '%s' source..." % path
        cmd = 'tar zxvf %s' % path
        msg = "extract subversion source: %s" % path
        self.plugin.system(cmd, msg)

    def enterModSvnSource(self):
        path = self.makeDependencySourceDirPath('subversion')
        print "Entering subversion source: %s" % path
        self.plugin.chdir(path)

    def configureModSvnSource(self):
        print "Configuring subversion source..."
        httpdSrcPath = self.makeApacheSourceDirPath()
        aprOneConfigPath = self.makeAprOneConfigPath()
        cmd = "./configure --prefix=%s/subversion --with-apxs=%s/apache/bin/apxs --with-apr=%s --with-apr-util=%s/srclib/apr-util/ --with-ssl --with-serf=%s/serf" % (self.targetPath, self.targetPath, aprOneConfigPath, httpdSrcPath, self.targetPath)
        msg = "configure subversion source: %s" % cmd
        self.plugin.system(cmd, msg)

    def extractModFastcgiSource(self):
        path = self.plugin.makeDependencyPath(self.getDependency('mod_fastcgi'))
        print "Extracting mod_fastcgi '%s' source..." % path
        cmd = 'tar zxvf %s' % path
        msg = "extract mod_fastcgi source: %s" % path
        self.plugin.system(cmd, msg)

    def enterModFastcgiSource(self):
        sourcePath = self.makeDependencySourceDirPath('mod_fastcgi')
        print "Entering mod_fastcgi source: %s" % sourcePath
        self.plugin.chdir(sourcePath)

    def configureModFastcgiSource(self):
        print "Configuring mod_fastcgi source..."
        cmd = 'cp Makefile.AP2 Makefile'
        msg = "configure mod_fastcgi source"
        self.plugin.system(cmd, msg)

    def makeModFastcgi(self):
        print "Running make for mod_fastcgi..."
        cmd = 'make top_dir=%s/apache' % (self.targetPath)
        msg = "run 'make' (for mod_fastcgi)"
        self.plugin.system(cmd, msg)

    def makeModFastcgiInstall(self):
        print "Running make install for mod_fastcgi..."
        cmd = 'make install top_dir=%s/apache' % (self.targetPath)
        msg = "run 'make install' (for mod_fastcgi)"
        self.plugin.system(cmd, msg)

    def fixModFastcgiConfig(self):
        print "Configuring Apache to load mod_fastcgi..."
        cmd = "perl -pi -e 's/# LoadModule foo_module modules\/mod_foo\.so/# LoadModule foo_module modules\/mod_foo.so\nLoadModule fastcgi_module     modules\/mod_fastcgi.so/' %s/apache/conf/%s.conf" %(self.targetPath, self.httpdProgramName)
        msg = "insert LoadModule for mod_fastcgi"
        self.plugin.system(cmd, msg)

    def removeHttpdSource(self):
        print "Removing httpd source dirs..."
        sourcePath = self.makeApacheSourceDirPath()
        cmd = 'rm -rf %s' % sourcePath
        msg = "extract source dir: %s" % sourcePath
        self.plugin.system(cmd, msg)

    def removeModPythonSource(self):
        print "Removing mod_python source dirs..."
        sourcePath = self.makeDependencySourceDirPath('mod_python')
        cmd = 'rm -rf %s' % sourcePath
        msg = "remove mod_python source: %s" % sourcePath
        self.plugin.system(cmd, msg)

    def removeSerfSource(self):
        print "Removing Serf source dirs..."
        sourcePath = self.makeDependencySourceDirPath('serf')
        cmd = 'rm -rf %s' % sourcePath
        msg = "remove Serf source: %s" % sourcePath
        self.plugin.system(cmd, msg)
    
    def removeModSvnSource(self):
        print "Removing Subversion source dirs..."
        sourcePath = self.makeDependencySourceDirPath('subversion')
        cmd = 'rm -rf %s' % sourcePath
        msg = "remove Subversion source: %s" % sourcePath
        self.plugin.system(cmd, msg)

    def removeModFastcgiSource(self):
        print "Removing mod_fastcgi source dirs..."
        sourcePath = self.makeDependencySourceDirPath('mod_fastcgi')
        cmd = 'rm -rf %s' % sourcePath
        msg = "remove mod_fastcgi source: %s" % sourcePath
        self.plugin.system(cmd, msg)

