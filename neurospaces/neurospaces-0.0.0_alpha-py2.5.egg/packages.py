#!/usr/bin/env python
"""
class for performing uninstallations of genesis 3 components.
Derived from the uninstall script from wxPython.
"""
import glob
import imp
import os
import pdb
import sys
from fnmatch import fnmatchcase
from commands import getoutput
import cPickle, urllib


from __cbi__ import PackageInfo

_package_info = PackageInfo()

#---------------------------------------------------------------------------


RCPTDIR = "/Library/Receipts"
RSRCDIR = "Contents/Resources"

# Only completly clean out dirs that have one of these as a prefix.
# We do this because the file list returned from lsbom will include /,
# /usr, /usr/local, etc.
MAC_PREFIXES = [ '/Library/Python/2.3/',
             '/Library/Python/2.4/',
             '/Library/Python/2.5/',
             '/Library/Frameworks/Python.framework/Versions/2.3/lib/python2.3/site-packages/',
             '/Library/Frameworks/Python.framework/Versions/2.4/lib/python2.4/site-packages/',
             '/Library/Frameworks/Python.framework/Versions/2.5/lib/python2.5/site-packages/',
             '/usr/local/lib/',
             ]

# The files that match one of the items in this list will only be
# removed if the last installation of wxPython on the system is being
# uninstalled.
COMMON_FILES = [ '/usr/local/bin/*',]

#---------------------------------------------------------------------------

class PackageError(Exception):
    pass

class PermissionError(Exception):
    pass


#---------------------------------------------------------------------------


def findInstalled():
    installed = []
    for name in glob.glob(os.path.join(RCPTDIR, "wxPython*")):
        try:
            ir = InstalledReceipt(name)
            installed.append(ir)
        except ReceiptError:
            pass  # just skip it...

    return installed

#---------------------------------------------------------------------------

_module_directory = os.path.join( os.path.dirname(os.path.abspath(__file__)))

#---------------------------------------------------------------------------

#
# A link with some good info on uninstalling and managing packages installed
# via egg.
# http://peak.telecommunity.com/DevCenter/EasyInstall#uninstalling-packages
#

class PackageManager:
    """
    Performs diagnostic management of installed GENESIS3 packages. The PackageManager
    operates under the assumption that it is the root directory for for all neurospaces
    packages like so:

        neurospaces.heccer
        neurospaces.model_container
        neurospaces.experiment

    It searches for the __cbi__.py identifier file located in each independent package
    and compiles a list with the info and install location.
    """
    
    def __init__(self, directory=_module_directory, identifier="__cbi__.py", verbose=False):

        self.neurospaces_directory = directory

        # a cache variable
        self.root_directory = None
        
        self.identifier = identifier
                
        self.install_recipts = []

        self.find_installed()

#---------------------------------------------------------------------------

    def get_version(self):

        return "version %s (%s)" % (_package_info.GetVersion(), _package_info.GetRevisionInfo())

#---------------------------------------------------------------------------
        
    def get_installed_packages(self):
        
        self.find_installed()
        
        return self.install_recipts

#---------------------------------------------------------------------------

    def get_package_names(self):

        # refresh package list

        self.find_installed()
        
        package_names = []
        
        for r in self.install_recipts:

            p_name = r['info'].GetName()

            package_names.append(p_name)


        return package_names

#---------------------------------------------------------------------------

    def find_installed(self):
        """

        """

        self.install_recipts = []
        
        for path, directories, files in os.walk( self.neurospaces_directory ):
            
            if os.path.isfile( os.path.join( path, self.identifier )):
                
                cbi_identifier = os.path.join(path, self.identifier)

                package_info = self.get_package_info(cbi_identifier)

                recipt = dict(info=package_info,
                              installed=os.path.abspath(path))

                self.install_recipts.append(recipt)

        self.find_egg_info()

#---------------------------------------------------------------------------

    def find_egg_info(self):
        """

        """
        
        if self.root_directory is None:
        
            self.root_directory = self.neurospaces_directory.rstrip('neurospaces')


        for r in self.install_recipts:

            package_name = r['info'].GetName()

            sys.version_info

            reg_exp = os.path.join(self.root_directory, "%s*py%d.%d*.egg-info" % (package_name, sys.version_info[0], sys.version_info[1]))

            info_files = glob.glob(reg_exp)

            if info_files:

                r['egg-info'] = info_files[0]

        
#---------------------------------------------------------------------------

    def get_package_info(self, cbi_identifier):

        package_info = None

        mod_name,file_ext = os.path.splitext(os.path.split(cbi_identifier)[-1])

        py_mod = imp.load_source(mod_name, cbi_identifier)

        if not 'PackageInfo' in dir(py_mod):

            raise PackageError("No 'PackageInfo' class found in the cbi identifier file")

        else:

            try:

                package_info = py_mod.PackageInfo()

            except Exception, e:

                raise

        return package_info

#---------------------------------------------------------------------------

    def get_recipt(self, package):

        for recipt in self.install_recipts:

            if recipt['info'].GetName() == package:

                return recipt

        return None

#---------------------------------------------------------------------------

    def have_access(self, path):

        return os.path.exists(path) and os.access(path, os.W_OK) 

#---------------------------------------------------------------------------

    def uninstall(self, package):

        recipt = self.get_recipt(package)

        if recipt is None:

            raise PackageError("The package '%s' is not installed" % package)

        try:
            
            package_name = recipt['info'].GetName()
            package_rev = recipt['info'].GetRevisionInfo()
            package_version = recipt['info'].GetVersion()

            install_dir = recipt['installed']

        except KeyError, e:

            raise PackageError("%s" % e)

        if not self.have_access(install_dir):

            #raise PermissionError("Unable to uninstall, need permission: %s" % e.args[0])

            getoutput("sudo rm -rf %s" % install_dir)

            # now we remove the egg-info file if present
            if recipt.has_key('egg-info'):

                print "\tRemoving egg-info file '%s'" % recipt['egg-info']
                
                os.unlink(recipt['egg-info'])

        else:
    
            print "Removing: %s installation at '%s'" % (package_name, install_dir)

            files = os.listdir(install_dir)

            if files:
                
                for f in files:
                    
                    fname = os.path.join(install_dir, f)
                    
                    if not os.path.isdir(fname):
                        
                        os.unlink(fname)
                        
            files = os.listdir(install_dir)
            
            #if not files:  # perhaps some stale symlinks, or .pyc files
            #os.rmdir(install_dir)

            # we remove all of the install directory

            if self.have_access(install_dir):

                getoutput("rm -rf %s" % install_dir)

            else:
                
                getoutput("sudo rm -rf %s" % install_dir)


            # now we remove the egg-info file if present
            if recipt.has_key('egg-info'):

                print "\tRemoving egg-info file '%s'" % recipt['egg-info']
                
                os.unlink(recipt['egg-info'])
            
                

            # after uninstalling we refresh the package list.
            self.find_installed()
                

#---------------------------------------------------------------------------

