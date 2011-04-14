#
# ghettovcb.py
#
# mksbackup ghettovcb frontent
#

import os, string, subprocess, fnmatch, platform, time
import posixpath, ftplib
import threading, random

from datetime import datetime, timedelta
import Queue

import paramiko
import scp


from archiver import *
import ftpd
import cron

GHETTO_VERSION='2011_03_14_1'

exit_code_re=re.compile('^\s*exit_code\s*=\s*([0-9]+)\s*$')

# ---------------------------------------------------------------------------
class MySCPClient(scp.SCPClient):
    """MySCPClient.put converts all '\r\n' into '\n'
       MySCPClient.get downloads the remote dir at same level as local dir
    """ 
    
    # -----------------------------------------------------------------------
    def _send_files(self, files):
        for name in files:
            basename = os.path.basename(name)
            (mode, size, mtime, atime) = self._read_stats(name)
            if self.preserve_times:
                self._send_time(mtime, atime)
            file_hdl = file(name, 'rb')
            buffer=file_hdl.read()
            file_hdl.close()
            buffer=buffer.replace('\r', '')
            size=len(buffer)
            self.channel.sendall('C%s %d %s\n' % (mode, size, basename))
            self._recv_confirm()
            file_pos = 0
            buff_size = self.buff_size
            chan = self.channel
            while file_pos < size:
                buf=buffer[file_pos:file_pos+buff_size]
                chan.sendall(buf)
                file_pos += len(buf) 
                if self.callback:
                    self.callback(file_pos, size)
            chan.sendall('\x00')

    # -----------------------------------------------------------------------
    def get(self, remote_path, local_path = '',
            recursive = False, preserve_times = False):
        self._recv_topdir = local_path or os.getcwd()
        return scp.SCPClient.get(self, remote_path, local_path, recursive, preserve_times)
    
    # -----------------------------------------------------------------------
    def _recv_pushd(self, cmd):
        parts = cmd.split()
        try:
            mode = int(parts[0], 8)
            path = os.path.join(self._recv_dir, parts[2])
        except:
            self.channel.send('\x01')
            raise scp.SCPException('Bad directory format')
        else:
            if self._recv_dir==self._recv_topdir and (not os.path.exists(self._recv_dir) or os.path.isdir(self._recv_dir)):
                # use self._recv_dir instead of os.path.join(self._recv_dir, parts[2])
                path=self._recv_dir
                self._recv_topdir=''

        try:
            if not os.path.exists(path):
                os.mkdir(path, mode)
            elif os.path.isdir(path):
                os.chmod(path, mode)
            else:
                raise scp.SCPException('%s: Not a directory' % path)
            self._dirtimes[path] = (self._utime)
            self._utime = None
            self._recv_dir = path
        except (OSError, scp.SCPException), e:
            self.channel.send('\x01'+e.message)
            raise
        

# ---------------------------------------------------------------------------
def RunCommand(t, command, log=None):
    chan=t.open_session()
    exit_code=None
    chan.set_combine_stderr(True)
    cmd_line=command+' ; echo exit_code=$?'
    chan.exec_command(cmd_line)
    output=''
    while 1:
        try:
            x=chan.recv(1024)
            if len(x)==0:
                break
            output+=x
        except socket.timeout:
            break

    exit_code=chan.recv_exit_status()
    chan.close()
    
    # ESX(i) don't return any usable exit_code, use the one returned by  "echo exit_code=$?" 
    pos1=output.rfind('exit_code=')
    pos2=output.find('\n', pos1)
    exit_code=int(output[pos1+10:pos2])
    output=output[:pos1]

    if log:
        l=log.debug
        if exit_code!=0:
            l=log.warning
            
        if output or exit_code!=0:
            l('exit_code=%d command=%s', exit_code, cmd_line)
            for line in output.split('\n'):
                l('> %s', line)
        
    return exit_code, output
  

class Ghettovcb(Archiver):
    
    name='ghettovcb'
    exe='ghettovcb'

    types=dict( backup='backup', copy='copy', move='move',)
    variables=dict(vm='vm_name')


    ghetto_version_format1=re.compile(r'(?P<year>\d{4})_(?P<month>\d{2})_(?P<day>\d{2})')

    initiate_backup_re=re.compile(r'.*info: Initiate backup for (?P<name>.+)')
    backup_duration_re=re.compile(r'.*info: Backup Duration:')
    config_vm_backup_volume_re=re.compile(r'.*info:\s*CONFIG\s*-\s*VM_BACKUP_VOLUME\s*=\s*(?P<vm_backup_volume>.+)')
    config_vm_backup_dir_naming_convention_re=re.compile(r'.*info:\s*CONFIG\s*-\s*VM_BACKUP_DIR_NAMING_CONVENTION\s*=\s*(?P<vm_backup_dir_naming_convention>.+)')
    find_vmdk_re=re.compile(r'.*debug: findVMDK\(\) - Searching for VMDK: "(?P<vmdk>.+)" to backup')
    ftp_url_re=ftp_url_re

    # -----------------------------------------------------------------------
    def __init__(self):
        Archiver.__init__(self)
        
        self.host=None
        self.login=None
        self.password=None
        self.local=None
        self.remote_temp=None
        self.vm_list=[]
        self.vm_exclude=[]
        
        self.ghettovcb=None
        self.ghettovcb_bin=None
        self.ghettovcb_version='unknown'
        self.global_conf=None
        self.temp_target=None
        self.default_var=None

        self.ghettovcb_wait_nfs=None
        
        self.destination=None
        self.type='backup'
        
        self.scp_bin=None
        self.scp_args=None
        
        self.upload_status=''
        self.upload_status_code=None
        self.upload_thread=None
        self.upload_queue=Queue.Queue()
        self.uploaded_filenames=dict()
        self.ftp_local=None
        self.ftp_local_default=None
        self.ftp_server=None
        self.ftp_thread=None  

    # -----------------------------------------------------------------------
    def read_vm_conf(self, filename, default={}):
        """load important variables from VM configuration backup script""" 
        values=default.copy()
        for line in open(filename, 'r'):
            for var in ('VM_BACKUP_VOLUME', 'ENABLE_COMPRESSION', 'LAST_MODIFIED_DATE', 'VER', 'VERSION', 'ENABLE_NON_PERSISTENT_NFS',):
                if line.startswith('printUsage() {'):
                    break
                if line.startswith('%s=' % var):
                    _k, v=line.split('=', 1)
                    values[var]=v.strip()
                    
        return values
    
    # -----------------------------------------------------------------------
    def load(self, job, manager):
        
        self.log=log=manager.log
        now=manager.now
        
        errors, warnings, extra={}, {}, ''

        try:
            self.host=job['host'].encode('ascii')
        except KeyError:
            errors['host']='option mandatory'
        except UnicodeEncodeError:
            errors['host']='invalid hostname or ip address'
            
        else:
            if not valid_ipRE.match(self.host):
                if not valid_hostnameRE.match(self.host):
                    errors['host']='invalid hostname or ip address'
                else:
                    try:
                        ip=socket.gethostbyname(self.host)
                    except socket.gaierror:
                        errors['host']='cannot resolve hostname'

        try:
            self.port=int(job.get('port', 22))
        except ValueError:
            errors['port']='must be an integer'
        else:
            if not (0<self.port and self.port<65535):
                errors['port']='must be an integer between 1 and 65535'

        for name in ('login', 'password', 'local'):
            value=job.get(name, None)
            if not value:
                errors[name]='option mandatory'
            else:
                setattr(self, name, value)
                if name=='password':
                    self.register_password(value)

        self.remote_temp=job.get('remote_temp', '/tmp')

        try:
            self.vm_list=quoted_string_list(job.get('vm_list', ''))
        except ValueError:
            errors['vm_list']='not a valid quoted string list'

        try:
            self.vm_exclude=quoted_string_list(job.get('vm_exclude', ''))
        except ValueError:
            errors['vm_exclude']='not a valid quoted string list'

        if job.get('target', None):
            self.target=job['target']

        self.global_conf=job.get('global_conf', None)

        self.script=job.get('script', 'ghettoVCB.sh')

        self.ftp_local=job.get('ftp_local', None)
        if self.ftp_local:
            if self.ftp_url_re.match(self.ftp_local):
                password=self.ftp_url_re.match(self.ftp_local).group('password')
                if password:
                    self.register_password(password)
            else:
                errors['ftp_local']='invalid url: ftp://[username[:password]@]host[:port]/rootdir'

        if not os.path.isdir(self.local):
            errors['local']='not a directory'
        else:
            # search ghettoVCB.sh whatever the char case
            self.ghettovcb=None
            list_dir=os.listdir(self.local)
            if self.script in list_dir:
                self.ghettovcb=self.script
            else:
                for filename in os.listdir(self.local):
                    if filename.lower()==self.script.lower():
                        self.ghettovcb=filename
                        break

            if not self.ghettovcb:
                errors['local']='file not found: %s' % (self.script, )

            # search the global_conf whatever the case
            if self.global_conf:
                if not self.global_conf in list_dir:
                    global_conf=None
                    for filename in list_dir:
                        if filename.lower()==self.global_conf.lower():
                            global_conf=filename
                            break
                    if not global_conf:
                        errors['global_conf']='file not found: %s' % (global_conf, )
                        self.global_conf=None
                    else:
                        self.global_conf=global_conf
            
            # read ghettoVCB.sh and extract default variables
            self.default_var={}
            if self.ghettovcb:
                self.default_var=self.read_vm_conf(os.path.join(self.local, self.ghettovcb))
                # check ghettoVCB version
                self.ghettovcb_version=self.default_var.get('LAST_MODIFIED_DATE','')+'_'+(self.default_var.get('VER','') or self.default_var.get('VERSION', ''))
                self.ghettovcb_wait_nfs=self.ghetto_version_format1.match(self.default_var.get('LAST_MODIFIED_DATE',''))!=None
                if self.ghettovcb_wait_nfs:
                    log.debug('this version of ghettovcb wait before to unmount the NFS share')
                
                if self.ghettovcb_version!=GHETTO_VERSION:
                    warnings['local']='This version of ghettoVCB.sh (%s) script has not been tested with MKSBackup, be warned ! Check the download page for more.' % (self.ghettovcb_version, )
                
            # read and extract global_conf
            if self.global_conf:
                self.default_var=self.read_vm_conf(os.path.join(self.local, self.global_conf), self.default_var)
            
        self.destination=job.get('destination', None)
        if self.destination:
                 
            self.destination=self.destination.replace('\n','')
            try:
                self.destination=Destinations(self.destination, self)
            except (DestinationSyntaxError, cron.CronException), e:
                errors['destination']='syntax error: %s' % (str(e), )

        if job.get('scp_bin', None):
            try:
                self.scp_args=quoted_string_list(job.get('scp_bin'))
            except ValueError:
                errors['scp_bin']='not a valid quoted string list'
            else:
                self.scp_bin=self.scp_args[0]
                self.scp_args[0]=os.path.basename(self.scp_args[0])
                if not os.path.isfile(self.scp_bin):
                    errors['scp_bin']='file not found'

        if not errors and self.destination and self.vm_list:
            # very limited check of target directory
            for vm in self.vm_list:
                type, target=self.destination.match(now, self.night_shift, variables=dict(vm=vm))
                # I cannot check more than dirname because when COMPRESSED is 1
                # target is a filename and not a directory 
                if type in ('move', 'copy') and not target.startswith('ftp://'):
                    dirname=os.path.dirname(target)
                    try:
                        os.makedirs(dirname)
                    except:
                        pass
                    if not os.path.isdir(dirname):
                        errors['destination']='directory not found: %s' % (dirname, )
                    
        if not errors:
            # upload and setup files on the VMWARE server

            t=paramiko.Transport((self.host, self.port))
            t.connect(username=self.login, password=self.password)
            
            scpclient=MySCPClient(t)
            scpclient.put(self.local, self.remote_temp, recursive=True)

            self.temp_target=posixpath.join(self.remote_temp, os.path.basename(self.local))
            self.ghettovcb_bin=posixpath.join(self.temp_target, self.ghettovcb)
            
            self.include_vm_file=posixpath.join(self.temp_target, 'include_vm')
            self.exclude_vm_file=posixpath.join(self.temp_target, 'exclude_vm')
            
            _exit_code, _output=RunCommand(t, 'chmod +x "%s"' % (self.ghettovcb_bin, ), log)

            self.cmd_line='cd "%s" ; ./"%s" -d debug -c "%s"' % (self.temp_target, self.ghettovcb, self.temp_target)
            
            if self.vm_list:
                self.cmd_line+=' -f "%s"' % (self.include_vm_file,)       
                for i, vm in enumerate(self.vm_list):
                    if i==0:
                        _exit_code, _output=RunCommand(t, 'echo "%s" > "%s"' % (vm, self.include_vm_file), log)
                    else:
                        _exit_code, _output=RunCommand(t, 'echo "%s" >> "%s"' % (vm, self.include_vm_file), log)
            else:
                self.cmd_line+=' -a'       
                if self.vm_exclude:
                    self.cmd_line+=' -e "%s"' % (self.exclude_vm_file,)       
                    for i, vm in enumerate(self.vm_exclude):
                        if i==0:
                            _exit_code, _output=RunCommand(t, 'echo "%s" > "%s"' % (vm, self.exclude_vm_file), log)
                        else:
                            _exit_code, _output=RunCommand(t, 'echo "%s" >> "%s"' % (vm, self.exclude_vm_file), log)
            if self.global_conf:
                self.cmd_line+=' -g "%s"' % (posixpath.join(self.temp_target, self.global_conf),)
            
            self.cmd_line+=' ; echo exit_code=$?' # ESXi don't return the exit_code   

            extra+='cmd_line=%s\n' % self.cmd_line
            t.close()
            
            if self.scp_bin:
                self.scp_args+=[ '-P', str(self.port), '-q' ]
                if sys.platform in ('win32', ):
                    # putty allow cmd line password
                    self.scp_args+=[ '-batch', '-pw', self.password ]
                extra+='scp_cmd=%s %s@%s:%%source%% %%destination%%\n' % (self.hide_password(' '.join(self.scp_args)), self.login, self.host, ) 
                
        return errors, warnings, extra

    # -----------------------------------------------------------------------
    def upload_queue_add(self, protocol, con, vm, source, destination):
        self.upload_queue.put((protocol, con, vm, source, destination))
        if not self.upload_thread:
            self.upload_thread=threading.Thread(target=self.uploader_thread, name='uploader')
            self.upload_thread.daemon=True
            self.upload_thread.start()
        
    # -----------------------------------------------------------------------
    def uploader_thread(self):
        current_vm=None
        self.upload_status=''
        if self.upload_status_code==None:
            self.upload_status_code='OK'
        while True:
            protocol, con, vm, source, destination=self.upload_queue.get(True)
            if vm!=current_vm:
                if current_vm!=None:
                    # just finished  current_vm
                    if status!='OK':
                        self.upload_status_code='ERR'
                    self.upload_status+='upload_status-%s=%s\r\n' % (current_vm, status)
                    self.upload_status+='upload_end-%s=%s\r\n' % (current_vm, time.ctime(end))
                    self.upload_status+='upload_end_epoch-%s=%d\r\n' % (current_vm, end)

                start=time.time()
                current_vm=vm
                if current_vm!=None:
                    # start a new vm
                    start=time.time()
                    status='OK'
                    self.upload_status+='upload_start-%s=%s\r\n' % (current_vm, time.ctime(start))
                    self.upload_status+='upload_start_epoch-%s=%d\r\n' % (current_vm, start)
                    self.upload_status+='upload_src-%s=%s\r\n' % (current_vm, source)
                    self.upload_status+='upload_dst-%s=%s\r\n' % (current_vm, destination)

            if protocol=='done':
                break
                                           
            if protocol=='ftp':
                ftp_line='ftpput -P %s -u "%s" -p "%s" %s "%s" "%s"' % (con['port'], con['username'], con['password'], con['host'], destination, source)
                self.log.info('start upload of "%s" to "%s"', source, destination)
                cmd_line=self.hide_password(ftp_line)
                self.log.debug('ftp command: %s', cmd_line)
                exit_code, output=RunCommand(self.t, ftp_line, log=None)
                if exit_code==0:
                    self.log.debug('file uploaded: %s', destination)
                else:
                    status='ERR'
                    self.log.error('upload failed %s (%s)', destination, output)
            elif protocol=='ssh':
                self.log.info('start download from "%s" to "%s"', source, destination)

                if not self.scp_bin:
                    # use paramiko
                    try:
                        scpclient=MySCPClient(self.t, buff_size=65536)
                        self.log.debug('scp %s %s', source, destination)
                        scpclient.get(source, os.path.dirname(destination))
                    except scp.SCPException:
                        self.log.error('download failed: %s (%s)', destination, output)
                        status='ERR'
                else:
                    # use local SCP
                    scp_args=self.scp_args[:]
                    scp_args+=[ '%s@%s:%s' % (self.login, self.host, source), destination]
                    scp_cmd=self.hide_password(' '.join(scp_args))
                    self.log.debug('scp_cmd=%s', scp_cmd)
                    if sys.platform in ('win32', ):
                        scp_args=param_encode(scp_args, self.manager.default_encoding)
                    scp_process=subprocess.Popen(scp_args, executable=self.scp_bin, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    scp_out, scp_err=scp_process.communicate()
                    if scp_out:
                        self.log.debug('copying %s: %s', source, scp_out)
                    if scp_err:
                        self.log.debug('copying %s: %s', source, scp_err)

                    if scp_process.returncode!=0:
                        self.log.error('download failed: %s (%s)', destination, scp_out+scp_err)
                        status='ERR'

            end=time.time()
        self.upload_status='upload_status=%s\r\n%s' % (self.upload_status_code, self.upload_status)

    # -----------------------------------------------------------------------
    def start_ftp_server(self):
        if self.ftp_server:
            return True

        rndpass=reduce(lambda x, y:x+random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'), range(8), '')
        self.register_password(rndpass)

        if self.ftp_local:  
            ftp=self.ftp_url_re.match(self.ftp_local).groupdict()
        else:
            ftp=dict(host='localhost')

        for k, v in dict(username=rndpass, password=rndpass, directory='/', port='0').iteritems():
            if ftp.get(k)==None:
                ftp[k]=v
        
        if ftp['host']=='localhost':
            ftp['host']=socket.gethostbyname(socket.gethostname())
            host=''        
        else:
            host=socket.gethostbyname(ftp['host'])

        if sys.platform in ('win32', ):
            # convert posix directory into windows path 
            # /c/backup => C:\backup 
            root=ftp['directory']
            if re.match('^/[a-zA-Z]/', root):
                root=root[1]+':'+root[2:].replace('/', '\\')
            else:
                root=''
            ftp['directory']=root
        
        
        try:
            if ftp['directory']:
                os.makedirs(ftp['directory'])
        except:
            pass
        
        if not ftp['directory'] or not os.path.isdir(ftp['directory']):
            self.log.error('Cannot start built-in ftp server, wrong root directory: "%s"', ftp['directory'])            
            return False

        self.ftp_server=ftpd.FTPserver(addr=(host, int(ftp['port'])), root=ftp['directory'], user=ftp['username'], password=ftp['password']) # allowed=self.host
        self.ftp_thread=threading.Thread(target=self.ftp_server.serve_forever, name='ftpserver', )
        self.ftp_thread.daemon=True
        self.ftp_thread.start()
        
        ftp['port']=self.ftp_server.socket.getsockname()[1]
        self.ftp_local_default=ftp

        return True
         
    # -----------------------------------------------------------------------
    def upload_vmdk(self, vm, root_backup_dir, vmdk, now):
        type, target=self.destination.match(now, self.night_shift, variables=dict(vm=vm))
        # print "ASX upload_vmdk vm=%s type=%s target=%s root_backup_dir=%s vmdk=%s" %(vm, type, target, root_backup_dir, vmdk)
        if target and type in ('move', 'copy'):
            ftp_match=self.ftp_url_re.match(target)

            if ftp_match:
                ftp=ftp_match.groupdict()
                if ftp['directory']==None:
                    ftp['directory']=''
                    
                if ftp['host']=='localhost':
                    if not self.ftp_server:
                        try:
                            res=self.start_ftp_server()
                        except Exception, e:
                            self.log.exception('starting ftp server')
                            return
                        else:
                            if res:
                                self.log.info('ftpserver listening on %s:%d', self.ftp_server.socket.getsockname()[0], self.ftp_server.socket.getsockname()[1])
                            else:
                                return
                    ftp['host']=self.ftp_local_default['host']
                    for k in ('port', 'username', 'password'):
                        if ftp.get(k)==None:
                            ftp[k]=self.ftp_local_default[k]
                
                else:
                    # try to create directories on the remote ftp server from 
                    # this host. If it fail the directory must already exist.   
                    try:
                        ftpcli=ftplib.FTP(ftp['host'], ftp['username'], ftp['password'], timeout=10)
                        dir=ftp['directory']
                        dirs=[]
                        while dir and dir!='/':
                            dirs.insert(0, dir)
                            dir=posixpath.dirname(dir)
                            print dir

                        for dir in dirs:
                            try:
                                ftpcli.mkd(dir)
                            except:
                                pass
                        try:
                            ftpcli.quit()
                        except:
                            pass
                        ftpcli.close()
                    except:
                        pass
                            
                                
                target=ftp['directory']
                protocol, con='ftp', ftp
                
            else:
                # create the target dir, if don't exist
                try:
                    if not os.path.isdir(target):
                        os.makedirs(target)
                except Exception, e:
                    self.log.error('creating directory %s: %s', target, e)
                    return

                protocol, con='ssh', self.t

            # search for files older than vmdk
            if vmdk:
                # file older then vmdk
                find_cmd='find "%s" -type f \! -newer "%s"' % (root_backup_dir, posixpath.join(root_backup_dir, vmdk))
            else:
                # all files in the directory
                find_cmd='find "%s" -type f' % (root_backup_dir, )
                
            exit_code, output=RunCommand(self.t, find_cmd, log=None)
            # print 'ASX\n', output
            if exit_code:
                self.log.error('cannot list %s: %r',root_backup_dir, output)
                self.upload_status_code='ERR'                
            else:
                for filename in output.split('\n'):
                    filename=filename.strip()
                    if filename and not filename.startswith('.lck-') and filename not in self.uploaded_filenames:
                        self.uploaded_filenames[filename]=None
                        relfilename=filename[len(root_backup_dir):]
                        relfilename=relfilename.lstrip('/')
                        if protocol=='ftp':
                            destination=posixpath.join(target, relfilename)
                        else:
                            destination=os.path.join(target, relfilename)
                        self.upload_queue_add(protocol, con, vm, filename, destination)

    # -----------------------------------------------------------------------
    def run(self, command, job, manager):

        self.log=log=manager.log
        self.manager=manager
        
        now=manager.now
        log.info('ghettoVCB.sh version is: %s  nfs_wait=%r', self.ghettovcb_version, self.ghettovcb_wait_nfs)
        start=int(time.time())

        self.t=t=paramiko.Transport((self.host, self.port))
        # t.get_security_options()._set_ciphers(['blowfish-cbc', ]) # don't speed up anything and don't work with 3.5 
        t.connect(username=self.login, password=self.password)
        # t.set_keepalive(300) # make the backup fail
        chan=t.open_session()
        chan.set_combine_stderr(True)
        log.info('start: %s', self.cmd_line)
        chan.exec_command(self.cmd_line)

        attachments=[]
        
        output=''
        state='waiting_for_start'
        current_vmdk=None
        for line in socket_readlines(chan):
            # I'm reading the socket in this loop,
            # I CANNOT DO SOMETHING TIME CONSUMING or do it in background 
            output+=line+'\n'
            log.debug(line)
            
            match=self.config_vm_backup_volume_re.match(line)
            if match:
                vm_backup_volume=match.group('vm_backup_volume')
                continue

            match=self.config_vm_backup_dir_naming_convention_re.match(line)
            if match:
                vm_backup_dir_naming_convention=match.group('vm_backup_dir_naming_convention')
                continue
            
            match=self.initiate_backup_re.match(line)
            if match:
                # start a new VM
                state='started'
                current_vm=match.group('name')

                # read vm config file if it exist
                filename=os.path.join(self.local, current_vm)
                if os.path.isfile(filename):
                    vm_var=self.read_vm_conf(filename, self.default_var)
                else:
                    vm_var=self.default_var
                    
                # use vm_backup_volume instead of vm_var['VM_BACKUP_VOLUME']
                # because the first one as been recalculated by ghettoVCB to take care of 
                # ENABLE_NON_PERSISTENT_NFS
                target=posixpath.join(vm_backup_volume, current_vm)
                compress=vm_var['ENABLE_COMPRESSION']=='1'

                continue

            match=self.find_vmdk_re.match(line)
            if match:
                # start a new disk
                if current_vmdk and vm_var['ENABLE_NON_PERSISTENT_NFS']!='1' and self.destination:
                    # if needed, now we can upload the previous disk
                    _res=self.upload_vmdk(current_vm, root_backup_dir, current_vmdk, now)
                     
                # store current vmdk
                current_vmdk=match.group('vmdk')
                root_backup_dir=posixpath.join(vm_backup_volume, current_vm, current_vm+'-'+vm_backup_dir_naming_convention)
                continue

            match=self.backup_duration_re.match(line)
            if match:
                """the backup just finished"""
                if current_vmdk and vm_var['ENABLE_NON_PERSISTENT_NFS']!='1' and self.destination:
                    # if needed, now we can upload the previous disk
                    _res=self.upload_vmdk(current_vm, root_backup_dir, current_vmdk, now)
            
                # search the target and make a directory listing 
                
                dir_lst, up_lst, scp_process=None, None, None
                if vm_var['ENABLE_NON_PERSISTENT_NFS']=='1' and not self.ghettovcb_wait_nfs:
                    log.warning('cannot retrieve data from non persistent NFS share on old version of ghettoVCB.sh')
                else:
                    if compress:
                        _exit_code, dir_lst=RunCommand(t, 'ls -l "%s"' % target, log)
                        dir_lst='== directory '+target+'\n'+dir_lst
                    else:
                        _exit_code, up_lst=RunCommand(t, 'ls "%s"' % target, log)
                        dir_lst=None
                        # search the target directory, take the last one
                        target_name=''
                        for line in up_lst.split('\n'):
                            if line.endswith('-symlink'):
                                continue
                            if line.startswith(current_vm):
                                if line>target_name:
                                   target_name=line
                        up_lst='== directory '+target+'\n'+up_lst
                        if target_name: 
                            target=posixpath.join(target, target_name)
                            _exit_code, dir_lst=RunCommand(t, 'ls -l "%s"' % target, log)
                            dir_lst='== directory '+target+'\n'+dir_lst
    
                    if dir_lst:
                        attachments.append(('dir-%s.txt' % (current_vm,), None, dir_lst, 'text', 'plain', 'utf-8'))
            
                    if up_lst:
                        attachments.append(('dirup-%s.txt' % (current_vm,), None, up_lst, 'text', 'plain', 'utf-8'))
            
        
        ghettovcb_exit_code=chan.recv_exit_status()
        chan.close()
        # log.debug('ghettovcb return unreliable ssh exit code: %d', ghettovcb_exit_code)
        end_ghettovcb=int(time.time())
        
        # ESX(i) (dropbear) returns an unreliable exit_code   
        pos1=output.rfind('exit_code=')
        pos2=output.find('\n', pos1)
        ghettovcb_exit_code=int(output[pos1+10:pos2])
        output=output[:pos1]

        attachments.insert(0, ('output.txt', None, output, 'text', 'plain', 'utf-8') )
        
        # make the disk space usage
        _exit_code, df=RunCommand(t, 'df', log)
        
        # make volume listing 
        _exit_code, ls_volumes=RunCommand(t, 'ls -l /vmfs/volumes', log)
        ls_volumes='== directory /vmfs/volumes\n'+ls_volumes

        # Nothing more to upload    
        self.upload_queue_add('done', None, None, None, None)
        # wait for end of upload /download
        if not self.upload_queue.empty():
            log.info('waiting end of upload...')
            while not self.upload_queue.empty():
                time.sleep(5)

        end=int(time.time())

        t.close()

        if ghettovcb_exit_code==0:
            ghettoVCB_status='OK'
            backup_status='OK'
        else:
            ghettoVCB_status='ERR'
            backup_status='ERR'

        if self.upload_status_code and self.upload_status_code!='OK':
            backup_status='ERR'

        status=u''
        status+='name=%s\r\n' % job['name']
        status+='program=%s\r\n' % self.name
        status+='version=%s\r\n' % self.__version__
        status+='status=%s\r\n' % backup_status
        status+='hostname=%s\r\n' % manager.hostname
        
        status+='exit_code=%d\r\n' % ghettovcb_exit_code
        status+='start=%s\r\n' % time.ctime(start)
        status+='end_ghettovcb=%s\r\n' % time.ctime(end_ghettovcb)
        status+='end=%s\r\n' % time.ctime(end)
        status+='start_epoch=%d\r\n' % start
        status+='end_epoch=%d\r\n' % end
        status+='end_ghettovcb_epoch=%d\r\n' % end_ghettovcb

        status+='type=%s\r\n' % self.type
        status+='ghettovcb_status=%s\r\n' % ghettoVCB_status
        status+=self.upload_status

        if df:
            attachments.insert(0, ('df.txt', None, df, 'text', 'plain', 'utf-8'),)

        if ls_volumes:
            attachments.insert(0, ('ls_volumes.txt', None, ls_volumes, 'text', 'plain', 'utf-8'),)
        
        return backup_status, status, attachments
