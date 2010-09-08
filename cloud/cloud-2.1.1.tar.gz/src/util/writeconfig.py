"""
This module, has the function writeConfig, to generate a cloudconf.py file
If invoked at the command-line, the default config will be written
TODO: Some code duplicated -- fix me


Copyright (c) 2009 `PiCloud, Inc. <http://www.picloud.com>`_.  All rights reserved.

email: contact@picloud.com

The cloud package is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This package is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this package; if not, see 
http://www.gnu.org/licenses/lgpl-2.1.html
"""

import sys
withHidden = False
doReload = False
isWriting = False

def writeConfig():    
    """Write configuration file
    Do this by loading every submodule in the cloud package and force it to register w/ cloud.cloudconfig
    """
    
    def recurser(path,prefix):        
        """(Re)load every module in cloud, forcing it to re-enter its config information"""
        files = os.listdir(path)
        for f in files:
            if f.endswith('.py'):
                endname = f[:-3]
                if endname == 'cloudconfig' or endname == '__init__' or endname == 'setup' or endname == 'writeconfig':                    
                    continue
                modname = prefix + endname
                #print modname #LOG ME                
                try:
                    __import__(modname)                
                    if doReload:
                        reload(sys.modules[modname])
                except ImportError:
                    pass                    
            elif os.path.isdir(path + f):
                newpath = path + f + os.sep
                recurser(newpath, prefix + f + '.')
        
    global isWriting
    isWriting = True
    
    import os
    import cloud.cloudconfig    
    if doReload:
        reload(cloud.cloudconfig)
    cloud.cloudconfig._needsWrite = False 
    cloud.cloudconfig.genHidden = withHidden
    
    """Reset config"""
    import cloud.util.configmanager    
    if doReload:
        cloud.cloudconfig.config = cloud.util.configmanager.ConfigManager()
    
    recurser(cloud.__path__[0] + os.sep ,'cloud.')
    cloud.cloudconfig.flushConfig()
    
    isWriting = False
        

if __name__ == '__main__':   
    if len(sys.argv) > 1 and sys.argv[1] == 'advanced':
        withHidden = True    

    doReload = True
    writeConfig()    