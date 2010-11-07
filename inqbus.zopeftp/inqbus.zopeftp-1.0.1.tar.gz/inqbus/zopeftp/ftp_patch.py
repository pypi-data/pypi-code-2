from App.config import getConfiguration
import logging
logger = logging.getLogger('inqbus.zopeftp')

global ftppath
ftppath = ''

def patch_ftpserver():
    """ Monkey patched zope_ftp_channel.cmd_pass, this add a ftp config
        parameter for ftp-start-path which can used in zope.conf
    """

    def get_ftppath_from_zopeconfig():
        """ load ftppath from zope.conf and 
            store it in the global ftppath variable
        """
        config = getConfiguration().product_config
        if config is not None:
            task_config = config.get('inqbus.zopeftp', None)
            if task_config:
                return task_config
        return {}

    zopeftp_config = get_ftppath_from_zopeconfig()
    if zopeftp_config.has_key('ftppath'):
        ftppath = zopeftp_config['ftppath']


    def patched_cmd_pass(self, line):
        # add fix path to username to authenticate and chroot the user
        # to that path if the username does not contain already a path.
        global ftppath
        if ftppath and ftppath != '':
            startpath = ftppath
        else:
            startpath = ''
        i=self.userid.find('@')
        if i==-1 and startpath:
            logger.info("Add start-path \"%s\" to ftp username \"%s\"" %
                         (startpath, self.userid))
            self.userid += '@' + startpath
            logger.info("New ftp-username is: \"%s\"" % self.userid)
        return self.orig_cmd_pass(line)

    from ZServer.FTPServer import zope_ftp_channel
    zope_ftp_channel.orig_cmd_pass = zope_ftp_channel.cmd_pass
    zope_ftp_channel.cmd_pass = patched_cmd_pass
    logger.info('Monkey patched zope_ftp_channel.cmd_pass, this add a ftp config parameter for ftp-start-path which can used in zope.conf!')




#def cmd_pass(self, line):
#        'specify password'
#        if len(line) < 2:
#            pw = ''
#        else:
#            pw = line[1]
#        self.password=pw
#        i=self.userid.find('@')
#        i=1
#        if i ==-1:
#            print("userid: %s" % self.userid)
#            if self.server.limiter.check_limit(self):
#                self.respond ('230 Login successful.')
#                self.authorized = 1
#                self.anonymous = 1
#                self.log_info ('Successful login.')
#            else:
#                self.respond('421 User limit reached. Closing connection.')
#                self.close_when_done()
#        else:
#            #path=self.userid[i+1:]
#            path = 'campus/dokumente/ftp-server'
#            #self.userid=self.userid[:i]
#            self.userid=self.userid
#            self.anonymous=None
#            response=make_response(self, self.pass_completion,
#                    self._join_paths('/',path))
#            request=FTPRequest(path,'PASS',self,response)
#            handle(self.module,request,response)
#
