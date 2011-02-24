#
# ghettovcb.py
#
# mksbackup ghettovcb frontent
#

import os, string, subprocess, fnmatch, platform
import posixpath

from datetime import datetime, timedelta

import paramiko
import scp


from archiver import *
import cron

GHETTO_VERSION='09/28/2010'
#GHETTO_VERSION='02-13-2011_1'

exit_code_re=re.compile('^\s*exit_code\s*=\s*([0-9]+)\s*$')

# ---------------------------------------------------------------------------
class MySCPClient(scp.SCPClient):
    """MySCPClient.put will convert all '\r\n' into '\n'
       MySCPClient.get will will download the remote dir at same level as local dir
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
    
    # ESX(i) don't return any exit_code
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
        
    # -----------------------------------------------------------------------
    def read_vm_conf(self, filename, default={}):
        """load important variables from VM configuration backup script""" 
        values=default.copy()
        for line in open(filename, 'r'):
            for var in ('VM_BACKUP_VOLUME', 'ENABLE_COMPRESSION', 'LAST_MODIFIED_DATE', 'VER', 'ENABLE_NON_PERSISTENT_NFS',):
                if line.startswith('printUsage() {'):
                    break
                if line.startswith('%s=' % var):
                    _k, v=line.split('=', 1)
                    values[var]=v.strip()
                    
        return values
    
    # -----------------------------------------------------------------------
    def load(self, job, manager):
        
        log=manager.log
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

        for name in ('login', 'password', 'local', 'remote_temp',):
            value=job.get(name, None)
            if not value:
                errors[name]='option mandatory'
            else:
                setattr(self, name, value)
                if name=='password':
                    self.register_password(value)

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
                self.ghettovcb_version=self.default_var.get('LAST_MODIFIED_DATE','')+self.default_var.get('VER','')
                self.ghettovcb_wait_nfs=self.ghetto_version_format1.match(self.default_var.get('LAST_MODIFIED_DATE',''))!=None
                log.error('ghettovcb_version %r %r', self.ghettovcb_version, self.ghettovcb_wait_nfs)
                if self.ghettovcb_wait_nfs:
                    log.debug('this version of ghettovcb wait before to unmount the NFS share')
                
                if self.default_var.get('LAST_MODIFIED_DATE','')!=GHETTO_VERSION:
                    warnings['local']='This version of ghettoVCB.sh (%s) script has not been tested with MKSBackup, be warned ! Check the download page for more.' % (self.ghettovcb_version, )
                
            # read and extract global_conf
            if self.global_conf:
                self.default_var=self.read_vm_conf(os.path.join(self.local, self.global_conf), self.default_var)
            
        self.destination=job.get('destination', None)
        if self.destination:
            if not self.vm_list:
                 errors['destination']='vm_list must be set to use "destination"'
                 
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

        if not errors and self.destination:
            self.type, self.target=self.destination.match(now, self.night_shift, variables=dict(vm=self.vm_list[0]))
            if self.type in ('move', 'copy') and not os.path.isdir(os.path.dirname(self.target)):
                errors['destination']='directory not found: %s' % (os.path.dirname(self.target), )
                    
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
            
            _exit_code, _output=RunCommand(t, 'chmod +x "%s"' % self.ghettovcb_bin, log)

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
    def run(self, command, job, manager):

        any_error=False

        log=manager.log
        now=manager.now
        log.info('ghettoVCB.sh version is: %s' % self.ghettovcb_version)
        start=int(time.time())

        t=paramiko.Transport((self.host, self.port))
        # t.get_security_options()._set_ciphers(['blowfish-cbc', ]) # don't speed up anything and don't work with 3.5 
        t.connect(username=self.login, password=self.password)
        # t.set_keepalive(300) # make the backup fail
        chan=t.open_session()
        chan.set_combine_stderr(True)
        log.info('start: %s', self.cmd_line)
        chan.exec_command(self.cmd_line)

        # search in the output for the name of backed up vm
        # should be == to self.vm_list when provided
        attachments=[]
        
        vm_list=[] # that need to be scp somewhere 

        output=''
        state='waiting_for_start'
        for line in socket_readlines(chan):
            # I'm reading the socket in this loop,
            # I CANNOT DO SOMETHING TIME CONSUMING like scp 
            output+=line+'\n'
            log.debug(line)
            
            current_error=False
            
            match=self.config_vm_backup_volume_re.match(line)
            if match:
                vm_backup_volume=match.group('vm_backup_volume')
            
            match=self.initiate_backup_re.match(line)
            if match:
                state='started'
                current_vm=match.group('name')
                continue
            
            match=self.backup_duration_re.match(line)
            if match:
                """the backup just finished"""
            
                # read vm config file if it exist
                filename=os.path.join(self.local, current_vm)
                if os.path.isfile(filename):
                    vm_var=self.read_vm_conf(filename, self.default_var)
                else:
                    vm_var=self.default_var
                    
                # search the target and make a directory listing 
                
                dir_lst, up_lst, scp_process, target=None, None, None, None
                if vm_var['ENABLE_NON_PERSISTENT_NFS']=='1' and not self.ghettovcb_wait_nfs:
                    log.warning('cannot retrieve data from non persistent NFS share on old version of ghettoVCB.sh')
                else:
                    # use vm_backup_volume instead of vm_var['VM_BACKUP_VOLUME']
                    # because the first one as been recalculated by ghettoVCB to take care of 
                    # ENABLE_NON_PERSISTENT_NFS
                    target=posixpath.join(vm_backup_volume, current_vm)
                    compress=vm_var['ENABLE_COMPRESSION']=='1'
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
            
            
                    if vm_var['ENABLE_NON_PERSISTENT_NFS']!='1' and self.destination:
                        # each VM could have a different ENABLE_NON_PERSISTENT_NFS
                        # this is not true but ....
                        # if destination, move or copy backup
                        vm_list.append((current_vm, compress, target))


            any_error=any_error or current_error
        
            
        ghettovcb_exit_code=chan.recv_exit_status()
        chan.close()
        # log.debug('ghettovcb return unreliable ssh exit code: %d', ghettovcb_exit_code)
        end=int(time.time())
        
        # ESX(i) (dropbear) returns an unreliable exit_code   
        pos1=output.rfind('exit_code=')
        pos2=output.find('\n', pos1)
        ghettovcb_exit_code=int(output[pos1+10:pos2])
        output=output[:pos1]

        status=''
        for current_vm, compress, target in vm_list:
            # if destination is set, and type is move or copy backup
            # handle ssh scp and file delete
            current_error=False
            if self.destination:
                self.type, self.target=self.destination.match(now, self.night_shift, variables=dict(vm=current_vm))
                if self.type in ('move', 'copy'):
                    if not compress:
                        # create the target dir, if don't exist
                        try:
                            if not os.path.isdir(self.target):
                                os.makedirs(self.target)
                        except Exception, e:
                            log.error('creating directory %s: %s', self.target, e)
                            current_error=True

                    if not current_error:
                        start_copy=int(time.time())
                        status+='remote_target-%s=%s\r\n' % (current_vm, target)
                        status+='target-%s=%s\r\n' % (current_vm, self.target)
                        if not self.scp_bin:
                            # use paramiko
                            try:
                                scpclient=MySCPClient(t, buff_size=65536)
                                log.info('scp -r %s %s', target, self.target)
                                scpclient.get(target, self.target, recursive=True)
                            except SCPException:
                                returncode=1
                                current_error=True
                            else:
                                returncode=0
                            status+='scp_exit_code-%s=%d\r\n' % (current_vm, returncode)
                        else:
                            # use local SCP
                            scp_args=self.scp_args[:]
                            if not compress:
                                if sys.platform in ('win32', ):
                                    scp_args.append('-unsafe')
                                #scp_args.append('-r')
                                wildcard='/*'
                            else:
                                wildcard=''
                                
                            scp_args+=[ '%s@%s:%s%s' % (self.login, self.host, target, wildcard), self.target]
                            scp_cmd=self.hide_password(' '.join(scp_args))
                            log.info('scp_cmd=%s', scp_cmd)
                            if sys.platform in ('win32', ):
                                scp_args=param_encode(scp_args, manager.default_encoding)
                            scp_process=subprocess.Popen(scp_args, executable=self.scp_bin, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            scp_out, scp_err=scp_process.communicate()
                            if scp_out:
                                attachments.append(('scp_out-%s.txt' % (current_vm,), None, scp_out, 'text', 'plain', manager.console_encoding))
                            if scp_err:
                                attachments.append(('scp_err-%s.txt' % (current_vm,), None, scp_err, 'text', 'plain', manager.console_encoding))
                            status+='scp_cmd-%s=%s\r\n' % (current_vm, scp_cmd)
                            status+='scp_exit_code-%s=%d\r\n' % (current_vm, scp_process.returncode)
                            
                            if scp_process.returncode!=0:
                                current_error=True
                            
                        log.info('scp end')
                        
                        if self.type=='move':
                            # delete the source
                            log.info('delete %s', target)
                            _exit_code, _rm_out=RunCommand(t, 'rm -r "%s"' % target, log)
    
                        try:
                            total_free_bytes=free_space(self.target, log)
                        except Exception, e:
                            log.error('checking target directory: %s', e)
                            status+='target_free_space-%s=%s\r\n' % (current_vm, e)
                        else:
                            status+='target_free_space-%s=%d\r\n' % (current_vm, total_free_bytes)
            
                        dir_out, _total_size=list_dir(self.target, log)        
                        attachments.append(('target_dir-%s.txt' % (current_vm,), None, dir_out.encode('utf-8'), 'text', 'plain', 'utf-8'))

                        end_copy=int(time.time())
                        status+='scp_start-%s=%s\r\n' % (current_vm, time.ctime(start_copy))
                        status+='scp_end-%s=%s\r\n' % (current_vm, time.ctime(end_copy))
                        status+='scp_start_epoch-%s=%d\r\n' % (current_vm, start_copy)
                        status+='scp_end_epoch-%s=%d\r\n' % (current_vm, end_copy)

            any_error=any_error or current_error


        attachments.insert(0, ('output.txt', None, output, 'text', 'plain', 'utf-8') )
        
        # make the disk space usage
        _exit_code, df=RunCommand(t, 'df', log)
        
        # make volume listing 
        _exit_code, ls_volumes=RunCommand(t, 'ls -l /vmfs/volumes', log)
        ls_volumes='== directory /vmfs/volumes\n'+ls_volumes

        t.close()

        if ghettovcb_exit_code==0 and not any_error:
            backup_status='OK'
        else:
            backup_status='ERR'

        status_pre=u''
        status_pre+='name=%s\r\n' % job['name']
        status_pre+='program=%s\r\n' % self.name
        status_pre+='version=%s\r\n' % self.__version__
        status_pre+='status=%s\r\n' % backup_status
        status_pre+='hostname=%s\r\n' % manager.hostname
        
        status_pre+='exit_code=%d\r\n' % ghettovcb_exit_code
        status_pre+='start=%s\r\n' % time.ctime(start)
        status_pre+='end=%s\r\n' % time.ctime(end)
        status_pre+='start_epoch=%d\r\n' % start
        status_pre+='end_epoch=%d\r\n' % end

        status_pre+='type=%s\r\n' % self.type
        status=status_pre+status
        
        if df:
            attachments.insert(0, ('df.txt', None, df, 'text', 'plain', 'utf-8'),)

        if ls_volumes:
            attachments.insert(0, ('ls_volumes.txt', None, ls_volumes, 'text', 'plain', 'utf-8'),)

        
        return backup_status, status, attachments
