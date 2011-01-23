#!/usr/bin/env python
#import clsIniUtils
from logger import Logger
# The MIT License
# 
# Copyright (c) 2007 Suncoast Partnership 
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# 

import fileutils
import os
import ftplib
from clsexceptions import FTPUploadFailureError, VPNFailure
from conf import settings
import paramiko
from conf import outputConfiguration
from datetime import datetime

class ClsPostProcessing(FTPUploadFailureError, VPNFailure):
    def __init__(self, vendorID):
        self.settings = settings
        self.systemMode = settings.MODE
        debug = settings.DEBUG
        if debug == True:
            self.debug = True
        else:
            self.debug = False
        
        iniFile = 'logging.ini'
        self.debugMessages = Logger(iniFile)
        
        # pull the vendor output parameters (this is a Dictionary)
        self.outputConfig = outputConfiguration.Configuration[vendorID]
        
    def processFile(self):
        pass
    
    def setINI(self, iniSettings):
        self.settings = iniSettings
        self.systemMode = iniSettings['options.systemmode']
    
    def processFileSFTP(self, filesToTransfer=[]):
        self.establishSFTP()
        self.transferSFTP(filesToTransfer)
        self.disconnectSFTP()
    
    def processFileVPN(self, pFiles):
        #self.fileList = pFiles
        rc = self.establishVPN() 
        if rc <> 0:
            # failure out
            comm = self.settings['%s_options.vpnconnect' % (self.systemMode)]
            theError = (1095, 'VPN Process failed to connect with command: %s.  Return from command was: %s.  Stopping processing until this can be resolved.  In order to complete processing you can execute command python clspostprocessing.py which will upload the XML files for Bowman Processing.' % (comm, rc), 'processFile(self)')            
            raise VPNFailure, theError
        
        rc = self.establishFTP(pFiles)

        # disconnect from the VPN
        rc = self.disconnectVPN()
        if rc <> 0:
            # failure out
            comm = self.settings['%s_options.vpndisconnect' % (self.systemMode)]
            theError = (1096, 'VPN Process failed to disconnect with command: %s.  Return from command was: %s.  Stopping processing until this can be resolved.  In order to complete processing you can execute command %s' % (comm, rc, comm), 'processFile(self)')            
            raise VPNFailure, theError
        
        print 'Processing completed'
    
    def establishSFTP(self):
        self.ssh = paramiko.SSHClient()
    
        self.ssh.set_missing_host_key_policy(
            paramiko.AutoAddPolicy())
        
        #ssh.connect('192.168.0.208', username='user', password='password')
        # establish an SSH connection to the host
        try:
            self.ssh.connect(self.outputConfig['destinationURL'],
                    username=self.outputConfig['username'],
                    password=self.outputConfig['password']
                    )
        except:
            pass
        
        # Create FTP Object
        self.ftp = self.ssh.open_sftp()
        
    def transferSFTP(self, filesToTransfer):
        
        # first change locations on remote system
        destPath = self.outputConfig['outputpath']
        if destPath <> "":
            self.ftp.chdir(destPath)
        
        # put this source on the server
        for file in filesToTransfer:
            if self.debug:
                print 'writing file: %s to server: %s to dest file: %s' % (file, destPath, os.path.split(file)[1])
            # split the filename from the path.
            
            destFile = os.path.split(file)[1]
            self.ftp.put(file, destFile)
            # test if we need to change owner
            if self.outputConfig['owner'] <> '':
                pass
            # test if we need to change the MODe
            if self.outputConfig['chmod'] <> '':
                self.ftp.chmod(destFile, self.outputConfig['chmod'])
            if self.outputConfig['group'] <> '':
                pass
        
            
            print self.ftp.stat(destFile)
        
        # see if the file is there
        self.ftp.chdir('..')
        print self.ftp.listdir(path=destPath)
            
    
    def disconnectSFTP(self):
        self.ftp.close()
        
    def establishVPN(self):
        #command = 'vpnc baisix'
        command = self.settings['%s_options.vpnconnect' % (self.systemMode)]
        print 'Establishing VPN Connection using command: %s' % (command)    
        rc = self.spawnProcess(command)
        #rc = os.system(command)
        return rc
        
    def establishFTP(self, pFiles):
        command = 'ftp baisix.servicept.com'
        print 'Connecting to FTP '
        self.ftp(pFiles)
    
    def disconnectVPN(self):
        print 'Disconnecting from VPN'
        command = self.settings['%s_options.vpncdisconnect' % (self.systemMode)]
        print 'Disconnecting from VPN Connection using command: %s' % (command)    
        # rc = os.system(command)
        rc = self.spawnProcess(command)
        return rc
        
    def ftp(self, pFiles):
        #processor = fileutils.FileUtilities(debug=debug, debugMessages=debugMessages)
        #processor = fileutils.FileUtilities()
        outputDir = self.settings['filelocations.outputlocation']
        
        # login to FTP
        url = self.settings['%s_options.ftpxmlupload' % (self.systemMode)]
        uname = self.settings['%s_options.ftpuname' % (self.systemMode)]
        passwd = self.settings['%s_options.ftppwd' % (self.systemMode)]
        destdir = self.settings['%s_options.ftpdestdir' % (self.systemMode)]
        
        # SBB20071012 adding sleep and retries to the process
        ftpsleep = self.settings['options.ftpsleep']
        ftpretries = self.settings['options.ftpretries']
        ftpinitialsleep = self.settings['options.ftpinitialsleep']
        
        if self.debug:
            self.debugMessages.log('url: %s\n' % url, 1)
            self.debugMessages.log('uname: %s\n' % uname, 1)
            self.debugMessages.log('passwd: %s\n' % passwd, 1)
            self.debugMessages.log('destdir: %s\n' % destdir, 1)
        
        # connect to the server (Loop (ftpUploaded = True) until )
        attempt = 0
        ftpUploaded = False
        
        # SBB20100210 Adding an initial sleep (maybe the vpn is taking a while to establish the tunnel)
        fileutils.sleep(int(ftpinitialsleep))
        
        while not ftpUploaded:
            print "Connecting to: %s" % url
            attempt =+ 1
            print "Attempting FTP Process: %s" % (attempt)
            
            # check the number of retries, we can't do this all day. retries out
            if attempt > ftpretries:
                theError = (1090, 'FTP Process failed to upload file: %s.  Process timeout parm: %s and sleep parm: %s.  Please check the VPN Connection or the FTP Server at: %s' % (str(pFiles), ftpretries, ftpsleep, url), 'ftp(self)')
                raise FTPUploadFailureError, theError
            
            try:        
                f=ftplib.FTP(url, uname, passwd)
            except ftplib.all_errors:
                # sleep the process.  VPN/FTP happening too quickly
                self.debugMessages.log("General FTP Error.  Possibly process is happening too quickly.  Sleeping for %s seconds and trying again." % ftpsleep, 1)
                fileutils.sleep(int(ftpsleep))
                continue
            
            print "Connected"
            
            print 'Changing Directories to: %s' % destdir
            print f.cwd(destdir)
            
            if len(pFiles) > 0:
                for file in pFiles:
                    print 'Uploading file: %s' % file
                    fo = open(file, 'r')
                    fname = os.path.basename(file)
                    rc = f.storlines('STOR '+fname, fo)
            
                    if rc == '226 Transfer complete.':
                        # rename the file
                        self.renameFile(file, True)
                    else:
                        badFile = self.renameFile(file, False)
                        theError = (1080, 'FTP Error during upload of file: %s.  FTP Server returned: %s.  Stopping the upload process.  Please investigate and start the process again to complete the upload.  File was renamed to: %s' % (fname, rc, badFile), 'ftp(self)')
                        raise FTPUploadFailureError, rc    
                        print 'Done uploading files'
                        
                        fo.close()
            
            ftpUploaded = True
            
            
            break
            
        # Close FTP connection
        # Echo the result of the close command
        print f.close()
        print 'FTP Processing Completed, disconnected'
        return 0
    
    def renameFile(self, fileName, bSuccess=True):
        # if our upload worked, rename the file with .uploaded, if it failed, rename accordingly
        if bSuccess:
            renameExt = self.settings['filelocations.uploaded_file_extensions']
        else:
            renameExt = self.settings['filelocations.uploaded_failed_file_extensions']
            
        # make the filename unique (use ISO format for stamping)
        lsNowISO = datetime.now().isoformat()
        
        # craft up the name
        destFile = "%s.%s.%s" % (fileName, lsNowISO, renameExt)
        
        # rename the file
        fileutils.renameFile(fileName, destFile)
        
        #fileutils.moveFile(fileName, destFile)
        
        return destFile
    
    def spawnProcess(self, command):
        cmdParts = command.split(' ')
        #rc = os.spawnl(os.P_WAIT, cmdParts[0], cmdParts[1])
        rc = os.system(command)
        print 'Return Code is: %s' % rc
        return rc
    
if __name__ == '__main__':
    #cp = clsIniUtils.clsConfigParser('fileConverter.ini')
    #pd = cp.getConfig()
    pprocess = ClsPostProcessing('5678')
    pprocess.processFile()
    