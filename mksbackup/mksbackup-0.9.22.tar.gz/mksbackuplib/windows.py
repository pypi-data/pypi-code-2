#
# mkbackup/windows.py
#
# windows code


import os, sys, time, locale, platform, re, subprocess, urllib2
import _winreg

import archiver


default_encoding=locale.getdefaultlocale()[1]
console_encoding=sys.stderr.encoding


#======================================================================
#
# Event Viewer  logging
#
#======================================================================
import win32evtlog
import win32evtlogutil
import winerror
import win32con
import pywintypes

evt_dict={
        win32con.EVENTLOG_AUDIT_FAILURE:'AUDIT_FAILURE',
        win32con.EVENTLOG_AUDIT_SUCCESS:'AUDIT_SUCCESS',
        win32con.EVENTLOG_INFORMATION_TYPE:'INF',
        win32con.EVENTLOG_WARNING_TYPE:'WAR',
        win32con.EVENTLOG_ERROR_TYPE:'ERR'
        }

# ---------------------------------------------------------------------
def FormatEv(ev_obj, logtype):
    computer=str(ev_obj.ComputerName)
    # cat=str(ev_obj.EventCategory)
    level=str(ev_obj.EventType )
    record=str(ev_obj.RecordNumber)
    evt_id=str(winerror.HRESULT_CODE(ev_obj.EventID))
    evt_type=evt_dict.get(ev_obj.EventType, 'UNK')
    msg=win32evtlogutil.SafeFormatMessage(ev_obj, logtype)
    epoch=int(ev_obj.TimeGenerated)
    msg=u'=== eventid=%d eventtype=%s epoch=%d time="%s" ===\r\n%s' % ( ev_obj.EventID, evt_type, epoch, time.ctime(epoch), msg)
    #print ev_obj.EventID, evt_type, int(ev_obj.TimeGenerated), level, msg.encode('UTF-8')
    return msg 

# ---------------------------------------------------------------------
def ReadEvLog(logtype, source, log, start, end=None):
    # If any event is not 'INFO' => return 'ERR'
    # If the last event is not an 'INFO' => return 'WAR' (in fact when not event are present)
    # Else return 'OK'
    flags = win32evtlog.EVENTLOG_BACKWARDS_READ|win32evtlog.EVENTLOG_SEQUENTIAL_READ
    try:
        hand=win32evtlog.OpenEventLog(None, logtype) # None for localhost
    except pywintypes.error, e:
        log.error('EventLog error %r', e)
        return 'ERR', u'EventLog error %r' % (e, )
    else:
        cont, output, status=True, u'', ''
        while cont:
            events=win32evtlog.ReadEventLog(hand,flags,0)
            for ev_obj in events:
                if str(ev_obj.SourceName)!=source:
                    continue
                if int(ev_obj.TimeGenerated)<start:
                    cont=False
                    break
                if ev_obj.EventType!=win32con.EVENTLOG_INFORMATION_TYPE:
                    status='ERR'
    
                if ev_obj.EventID==8019 and ev_obj.EventType==win32con.EVENTLOG_INFORMATION_TYPE and status!='ERR':
                    status='OK'
                        
                if output:
                    output=FormatEv(ev_obj, logtype)+u'\r\n'+output
                else:
                    output=FormatEv(ev_obj, logtype)
    
            cont=cont and events
        win32evtlog.CloseEventLog(hand)
        
    if status=='':
        status='ERR'

    return status, output

# ---------------------------------------------------------------------
def WindowsErrorDecode(exception, encoding=default_encoding):
    """convert WindowsError or OSError exception into unicode string, 
    some message can contains non ascii chars in non US windows version"""
    
    # if isinstance(exception, (WindowsError, OSError))

    st=str(exception)
    try:
        return st.decode(encoding)
    except UnicodeDecodeError:
        return st.decode('ascii', 'replace')

# ---------------------------------------------------------------------------
def windows_list_dir(target_dir, log, encoding=default_encoding):
    try:
        dir_out, total_size=archiver._list_dir(target_dir, log) 
    except Exception, e:
        log.error('listing target directory: %s', WindowsErrorDecode(e, encoding))
        dir_out='error listing directory "%s": %s\r\n' % (target_dir, WindowsErrorDecode(e, encoding))
        total_size=0
        
    return dir_out, total_size


# =====================================================================
class Registry:

    sub_key="SOFTWARE\\MagiKSys\\MKSBackup\\%s"

    def __init__(self, master_key):
        self.home_key=self.sub_key % (master_key, )
        self.reg=None
        try:
            self.reg=_winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, self.home_key, 0, _winreg.KEY_READ|_winreg.KEY_WRITE)
        except EnvironmentError:
            self.reg=_winreg.CreateKey(_winreg.HKEY_LOCAL_MACHINE, self.home_key)
            _winreg.CloseKey(self.reg)
            self.reg=_winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, self.home_key, 0, _winreg.KEY_READ|_winreg.KEY_WRITE)
        
    def LoadValues(self, keys=[]):
        values=dict()
        try:
            i=0
            while True:
                k, v, _t=_winreg.EnumValue(self.reg, i)
                i+=1
                if not keys or k in keys:
                    values[k]=v
        except WindowsError:
            pass
        
        return values    
                
    def SaveValues(self, values):
        for k, v in values.iteritems():
            _winreg.SetValueEx(self.reg, k, None, _winreg.REG_SZ, str(v))

    def Close(self):
        if self.reg:
            _winreg.CloseKey(self.reg)


def raw_input_with_default(msg, prompt, default):

#    try:
#        import pyreadline as readline
#            
#        def pre_input_hook():
#            readline.insert_text(default)
#            readline.redisplay()
#        
#        readline.set_pre_input_hook(pre_input_hook)
#        try:
#            return raw_input(msg+prompt)
#        finally:
#            readline.set_pre_input_hook(None)
#    except ImportError, e:
#        print 'ERROR', e
        if default:
            line="%s [%s]%s" % (msg, default, prompt)
        else:
            line="%s%s" % (msg, prompt)
        value=raw_input(line)
        if value=='' and default:
            return default
        return value

# =====================================================================
def Install():
    """Install the exe, setup a default .ini and create task in scheduler"""

    choice=raw_input_with_default('Do you want to install MKSBackup ? (y/n)', '>', 'y')
    if choice!='y':
        print 'bye'
        return 0
        
    target=raw_input_with_default('Installation directory ', '>', 'C:\Magik')
    mksbackup_target=os.path.join(target, 'MKSBackup')
    if os.path.isdir(mksbackup_target):
        print 'Directory %s already exists, continue.' % (mksbackup_target,)
    else:
        try:
            os.makedirs(mksbackup_target)
        except Exception, e:
            print 'Error creating directory %s (%s)', (mksbackup_target, e)
        else:
            print 'Directory created'

    import shutil
    
    # copy .exe
    source=os.path.dirname(sys.argv[0])
    if os.path.realpath(sys.argv[0])==os.path.realpath(mksbackup_target):
        """.exe already in place"""
    else:
        print 'Copy %s' % (os.path.basename(sys.argv[0]))
        shutil.copy(sys.argv[0], mksbackup_target)

    # copy and rename sample.ini
    doc_src=os.path.join(source, 'doc')
    sample_ini=os.path.join(doc_src, 'sample.ini')
    if os.path.isfile(sample_ini):
        sample_ini_data=open(sample_ini).read()
    else:
        print 'Retrieve sample.ini file from http://www.magikmon.com/download/mksbackup/sample.ini ...'
        try:
            sample_ini_data=urllib2.urlopen('http://www.magikmon.com/download/mksbackup/sample.ini', None).read()
        except (urllib2.URLError, urllib2.HTTPError, Exception), e:
            sample_ini_data='# mksbackup.ini\n more on http://www.magikmon.com/mksbackup'
            pass
    # convert text fine in windows format 
    sample_ini_data=re.sub('(?<!\r)\n','\r\n', sample_ini_data)
    mksbackup_ini=os.path.join(target, 'mksbackup.ini')
    
    if os.path.isfile(mksbackup_ini):
        print 'Config file already exists: %s' % (mksbackup_ini, )
    else:
        print 'Create sample config file: %s' % (mksbackup_ini, )
        open(mksbackup_ini, 'w').write(sample_ini_data)

    # copy doc
    if os.path.isdir(doc_src):
        doc_dst=os.path.join(mksbackup_target, 'doc')
        try:
            os.mkdir(doc_dst)
        except Exception:
            pass
        try:
            for filename in os.listdir(doc_src):
                shutil.copy(os.path.join(doc_src, filename), doc_dst)
        except Exception, e:
            print 'Error copying documentation, continue'
        else:
            print 'Copy documentation'
    else:
        # try to get Readme
        print 'Documentation not found, try to retrieve Readme.txt'
        print 'from http://www.magikmon.com/download/mksbackup/readme.txt ...'
        try:
            readme_txt_data=urllib2.urlopen('http://www.magikmon.com/download/mksbackup/README.txt', None).read()
        except (urllib2.URLError, urllib2.HTTPError, Exception), e:
            readme_txt_data='more on http://www.magikmon.com/mksbackup\n'
        open(os.path.join(mksbackup_target, 'Readme.txt'), 'w').write(readme_txt_data)

    # create task in scheduler if not already exists
    stdout, stderr=subprocess.Popen('SCHTASKS /Query', stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    if stdout.find('MKSBackup')==-1:
        print 'create task MKSBackup in scheduler'
        jobs=raw_input_with_default('Enter your job names separated by spaces', '>', 'BACKUP_JOB')
        cmd='"%s" -q -l "%s" -c "%s" backup %s' % (os.path.join(mksbackup_target, os.path.basename(sys.argv[0])), os.path.join(target, 'mksbackup.log'), os.path.join(target, 'mksbackup.ini'), jobs) 
        schtasks_cmd=[ 'SCHTASKS', '/Create', '/SC', 'DAILY', '/TN', 'MKSBackup', '/ST', '22:45:00', '/RU', os.getenv('USERNAME'),  '/TR', cmd ]
        if sys.getwindowsversion()[0]>5:
            # under 2008 backup require HIGHEST privilege
            schtasks_cmd.insert(2, 'HIGHEST')
            schtasks_cmd.insert(2, '/RL')
            # under 2008, to force the system to ask for the password, set empty password 
            i=schtasks_cmd.index('/RU')+2
            schtasks_cmd.insert(i, '')
            schtasks_cmd.insert(i, '/RP')
        else:
            pass
            
        # print ' '.join(schtasks_cmd)
        process=subprocess.Popen(schtasks_cmd)
        _code=process.wait()
    else:
        print 'task MKSBackup already exists, skip'

    print 'Open task scheduler'
    subprocess.Popen([ 'control.exe',  'schedtasks', ])  # taskschd.msc works under 2008 not on XP
    print 'Open config file in notepad'    
    subprocess.Popen([ 'notepad', mksbackup_ini] )
    print 'Update or review your configuration and task'
    print 'More on http://www.magikmon.com/mksbackup' 
    raw_input('Install completed, press ENTER to quit')

    return 0