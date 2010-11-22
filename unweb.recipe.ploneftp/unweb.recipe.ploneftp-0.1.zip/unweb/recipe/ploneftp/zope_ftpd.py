#!/opt/local/bin/python2.6
#/usr/bin/env python
"""
A FTP service around Zope - allows resumable large file uploads into Zope.

It attempts to authentication using the same username/password against a Zope
server. When the file is completely uploaded from the user, it then FTPs the 
file into a Plone-style folder hierarchy using the inbuilt Zope FTP server.

"""

"""
    Plone FTP wrapper 
    Copyright (C) 2010 unweb.me
    Based on the plumiftp package by Andy Nicholson, Victor Rajewski, 
    EngageMedia Collective Inc.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    see LICENSE.txt in the source distribution for the GNU GPL v3 details. 
"""

import os
import ftplib
import threading
import imp

from pyftpdlib import ftpserver

#dict to keep filenames to delete when user logs out
FilesToDelete = {}
DeleteThreadLock = threading.Lock() #and a threadlock for that dict

class ZopeAuthorizer(ftpserver.DummyAuthorizer):

    def __init__(self, TmpDir, ZopeFTPServerAddr, ZopeFTPServerPort,
                 ZopePathString, RealFTPMsgLogin, RealFTPMsgQuit):
        self.TmpDir = TmpDir
        self.ZopeFTPServerAddr = ZopeFTPServerAddr
        self.ZopeFTPServerPort = ZopeFTPServerPort
        self.ZopePathString = ZopePathString
        self.RealFTPMsgLogin = RealFTPMsgLogin
        self.RealFTPMsgQuit = RealFTPMsgQuit
        ftpserver.DummyAuthorizer.__init__(self)

    def validate_authentication(self, username, password):

	#
	# proxied Zope FTP server authentication.
	#
        zopeftp=ftplib.FTP()
        try: 
	    #Zope FTP lets you in with an incorrect password.
	    # however, if you get it wrong, you can't see any files or write
        # anything. hence --> we need a test here to do something remotely 
        # and really check if we got the password wrong. Trying to 'cd' 
        # into our Members area is good enough to raise an 'not authenicated' 
        # error.

            ftpserver.log("authenticating to Zope FTP server %s:%s \
                           with username %s" % (self.ZopeFTPServerAddr, 
                           self.ZopeFTPServerPort, username))
            try:
                zopeftp.connect(self.ZopeFTPServerAddr, self.ZopeFTPServerPort)
                zopeftp.login(username, password)
    	        #login to our plone site's members area ..
                try:
                    zopeftp.cwd(self.ZopePathString % username)
                except:
                    zopeftp.cwd(self.ZopePathString)

            except ftplib.all_errors, detail:
                ftpserver.log("Error authenticating to Zope FTP server %s:%s \
                              with username %s : %s" % (self.ZopeFTPServerAddr, 
                              self.ZopeFTPServerPort, username, detail))
                return False
        finally:
            zopeftp.close()


	# Local server setup.
	#
        #create user path if not already present. If present and not a dir
        #then delete it and create a dir (shouldn't happen, but...)
        userpath = self.TmpDir + "/" + username
        try:
            if os.path.exists(userpath):
                if not os.path.isdir(userpath):
                    os.remove(userpath) 
                    os.makedirs(userpath)
            else:
                os.makedirs(userpath)
        except OSError, detail:
            #if there is a problem creating the folders then the ftp server
            #will return 'Authentication failed'
            ftpserver.log("Error creating temporary user directory %s: %s" 
                          % (userpath, detail))
            return False

	# 
	# successfully logged in for our purposes.
	#
	ftpserver.log('authenticated successfully with Plone FTP')
        return True

    def has_perm(self, username, perm, path=None):
        return True

    def get_perms(self, username):
        return 'elradfmw'

    def get_home_dir(self, username):
        return self.TmpDir + "/" + username

    def get_msg_login(self, username):
        return self.RealFTPMsgLogin

    def get_msg_quit(self, username):
        return self.RealFTPMsgQuit

class ZopeHandler(ftpserver.FTPHandler):
    

    def __init__(self, conn, server):
        self.config = imp.load_source('config',os.path.join(os.environ["PLONEFTP_ROOT"],"config.py"))
        ftpserver.FTPHandler.__init__(self,conn,server)

    def ftp_QUIT(self, line):
        ftpserver.FTPHandler.ftp_QUIT(self,line)
        ftpserver.log("ZopeHandler got a QUIT")
        self.deletePendingFiles()

    def handle_close(self):
        ftpserver.FTPHandler.handle_close(self)
        ftpserver.log("ZopeHandler got a closed connection")
        self.deletePendingFiles()

    def deletePendingFiles(self):
        global FilesToDelete, DeleteThreadLock
        DeleteThreadLock.acquire()
        if self.username in FilesToDelete:
            files = FilesToDelete[self.username]
            del FilesToDelete[self.username]
        else:
            files = []
        DeleteThreadLock.release()

        while files:
            file = files.pop()
            ftpserver.log("deleting %s from user %s" % (file, self.username))
            try:
                os.remove(file)
            except OSError, detail:
                ftpserver.log("Error deleting temp file %s : %s"%(file, detail))

    def on_file_received(self,file):
        ftpserver.log("ZopeHandler: received %s, from user %s"
                      % (file, self.username))
        def ZopeUpload():
            #ftp it into Zope itself.
            try:
                try:
                    zopeftp=ftplib.FTP()
                    zopeftp.connect(self.config.zope_ftp_address.split(':')[0], 
                                    self.config.zope_ftp_address.split(':')[1])
                    zopeftp.set_pasv(True)
                    zopeftp.login(self.username,self.password)
                    #login to our plone site's members area ..
                    try:
                        zopeftp.cwd(self.config.path % self.username)
                    except:
                        zopeftp.cwd(self.config.path)
                    parents = file.split(self.config.tmp_dir+'/'+self.username+'/')[1].split('/')[:-1]
                    for p in parents:
                        try:
                            zopeftp.mkd(p)
                        except:
                            pass
                        zopeftp.cwd(p)
                    #upload the file
                    f = open(file,'rb')                # open file to send
                    zopeftp.storbinary('STOR %s' % os.path.basename(file), f)
                    ftpserver.log("Successfully uploaded %s to Zope FTP server"
                                 % (file))
                except ftplib.all_errors, detail:
                    ftpserver.log("Error sending file %s to Zope FTP server \
                                   %s with username %s : %s"
                                  % (file, self.config.zope_ftp_address, 
                                    self.username,  detail))
                except IOError, detail:
                    ftpserver.log("Error opening local file %s for sending to \
                                  Zope FTP : %s" % (file, detail))
            finally:
                zopeftp.close()
                try:
                    f.close()
                except:
                    pass

                #schedule file(s) to be deleted when user logs out
                global FilesToDelete, DeleteThreadLock
                ftpserver.log("Setting %s from user %s to be deleted when user logs out" % (file, self.username))
                DeleteThreadLock.acquire()
                if self.username not in FilesToDelete:
                    FilesToDelete[self.username] = []
                FilesToDelete[self.username].append(file)
                DeleteThreadLock.release()
                self.sleeping = False

        self.sleeping = True
        threading.Thread(target=ZopeUpload).start()


def main(args):
    config = imp.load_source('config',os.path.join(os.environ["PLONEFTP_ROOT"],"config.py"))
    authorizer = ZopeAuthorizer(config.tmp_dir, config.zope_ftp_address.split(':')[0], config.zope_ftp_address.split(':')[1],
                               config.path, config.login_message, config.logout_message)
    ftp_handler = ZopeHandler
    ftp_handler.authorizer = authorizer
    address = (config.address.split(':')[0], config.address.split(':')[1])
    ftpd = ftpserver.FTPServer(address, ftp_handler)
    ftpd.serve_forever()

