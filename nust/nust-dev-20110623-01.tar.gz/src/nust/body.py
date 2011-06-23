# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function 

import pwd
import os
import glob
import stat
import re
import sys
import time
import hashlib
import shelve
import shlex, subprocess
import argparse
import ConfigParser

from utils import ping_uwsgi

CL_ARGS = argparse.Namespace()
VhStart = []
Pname   = None
DB      = {}
config  = ConfigParser.SafeConfigParser()

#---------------------------------------------------------------
#---------------------------------------------------------------
# for non-required fields default must be:
# ''   -- if not need
# None -- if None -- no keys
VhostInitialConfig = { #default key                     Required
              'OK' : [False,    None,                   None],
             'ERR' : [None,     None,                   None],
            'USER' : [None,     '--uid',                True],
         'WORKERS' : [2,        '--workers',            False],
#         'THREADS' : [None,     '-T',                  False],
          'MODULE' : ['django_wsgi','--module',         True],
             'PRJ' : ['No Name',None,                   False],
            'HOME' : [None,     '--pythonpath',         True],
              'VE' : [None,     '--virtualenv',         True],
             'LOG' : ['var/log/uwsgi.log','--daemonize',True],
             'PID' : ['var/run/uwsgi.pid','--pidfile2', False],
          'SOCKET' : [None,     '--socket',             True],
        'HARAKIRI' : [120,      '--harakiri',           False],
         'MAX_REQ' : [1024,     '--max-requests',       False],
             'FILE': [None,     None,                   False],
         'FILEHASH': [None,     None,                   False],
}
VIC_paths = ['VE','LOG','SOCKET','PID',]
#---------------------------------------------------------------
#---------------------------------------------------------------
def u8(c):
    return c.encode('utf-8')
#---------------------------------------------------------------
#---------------------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(
                description='Parsing Nginx\'s vhost\'s configs and start uwsgi daemons.',
                )
    parser.add_argument('-c', '--config', dest='config',
                action='store', nargs=1, 
                required=True, type=str,
                help='path to config file'
                )
    parser.add_argument('-q', '--quiet', dest='quiet',
                action='store_const', default=False, const=True,
                help='don\'t print status messages to stdout'
                )
    parser.add_argument('-t', '--test', dest='test', 
                action='store_const', default=True, const=True,
                help='don\'t start workers, but print start line'
                )
    parser.add_argument('-s', '--start', dest='start', 
                action='store_const', const=True,
                help='Start workers.'
                )
    parser.add_argument('--sleep-term', dest='sleep_term',
                action='store', default=5, nargs=1, type=int, metavar='NN',
                help='sleep time (sec) after kill uwsgi process'
                )
    parser.add_argument('--sleep-kill', dest='sleep_kill',
                action='store', default=1, nargs=1, type=int, metavar='NN',
                help='sleep time (sec) after kill -9  uwsgi process'
                )
    rv = parser.parse_args(namespace=CL_ARGS)
    if (CL_ARGS.start == None):
        if CL_ARGS.test:  
            CL_ARGS.start = False 
    elif (CL_ARGS.start == True):
        CL_ARGS.test  = False 
    else:
        pass
    # parsing .conf file for local options
    if not config.read(CL_ARGS.config):
        print('can\'t open config file {}'.format(CL_ARGS.config)) 
        rv = False
    return rv
#---------------------------------------------------------------
#---------------------------------------------------------------
def kill_process_rec(pid):
    PIPE = subprocess.PIPE
    args = '{} -p {}'.format(PStree,pid)
    args = shlex.split(u8('{}'.format(args)))
    res = subprocess.check_output(args)
    d = re.findall('\((\d+)\)',res)
    if d:
        dd = ' '.join(d)
        p = subprocess.call(shlex.split(u8('{} {}'.format(kill,dd))))
        time.sleep(CL_ARGS.sleep_term)
        for i in d:
            try:
                st = os.stat('/proc/{}'.format(i))
                p = subprocess.call(shlex.split(u8('{} {}'.format(kill_k9,i))))
                time.sleep(CL_ARGS.sleep_kill)
            except:
                pass
    return True
#---------------------------------------------------------------
#---------------------------------------------------------------
def start_uwsgi(PRC,U):
    uu = ' '.join(U)
    start = False
    pid = None
    ILH = '[{:16s}]: '.format(PRC['PRJ'])
    Q = CL_ARGS.quiet
    PRINT=''
    try:
        with open(PRC['PID'],'r') as f:
            pid = f.readline(8)
            try:
                pid = int(pid)
            except ValueError:
                pid=-1
        t = ''
        try:
            with open('/proc/{}/cmdline'.format(pid),'r') as f:
                t = f.readline(len(U[0]))
        except:
            pass
        if (t == U[0]):
	    rv = ping_uwsgi(PRC['SOCKET'])
	    if (rv[0]):
	        pass
	    else:
                if not Q: PRINT+='{}PING failed (), need restart\n'.format(ILH,rv[1])
                kill_process_rec(pid)
                start = True
        else:
            if not Q: PRINT+='{}Has old PID-file, but no workers\n'.format(ILH)
            start = True
    except:
        if (pid):
            if not Q: PRINT+='{}Process with PID={} does not exists, need starting.\n'.format(ILH,pid)
        else:
            if not Q: PRINT+='{}PID file {} not found, need starting.\n'.format(ILH,PRC['PID'])
        start = True

    args = u8('{} {}'.format(uu,PRC['COMMAND']))
    if (CL_ARGS.test):
        if (start):
            PRINT+='{}will be started with options:\n\t{}\n'.format(ILH, args)
        else:
            PRINT+='{}already started, all OK!\n'.format(ILH)

    rc = 0
    if (start and CL_ARGS.start):
        PRINT+='{}starting... '.format(ILH)
        args = shlex.split(args)
        try:
            rv = subprocess.check_output(args,stderr=subprocess.STDOUT)
            if (rv != ''):
                PRINT+='\n{}RC={} {}\n'.format(ILH,rc,rv)
            else:
                PRINT+='OK.\n'
        except subprocess.CalledProcessError, e:
            rc = e.returncode
            rv = e.output
            PRINT+='\n{}Can\'t start uwsgi server :( RC={}\n{}\n'.format(ILH,rc,rv)
    if PRINT: print(PRINT)
    return rc
#---------------------------------------------------------------
#---------------------------------------------------------------
def glob_homedir(user,v):
    if (v[0:2] == '~{}'.format(os.sep)):
        try:
            ui = pwd.getpwnam(user)
            hd = ui.pw_dir
        except:
            hd = ''
        v = '{0}{1}{2}'.format(hd,os.sep,v[2:])
    return v
#---------------------------------------------------------------
#---------------------------------------------------------------
def get_file_hash(filename):
    rv = None
    with open(filename) as fd:
        h = hashlib.new('sha512')
        h.update(fd.read())
        rv = h.hexdigest()
    return rv
#---------------------------------------------------------------
#---------------------------------------------------------------
def get_pname():
    pname = sys.argv[0].split(os.sep)[-1]
    pname = pname.split('.')[0]
    return pname
#---------------------------------------------------------------
#---------------------------------------------------------------
def remove_pidfile():
    pname = get_pname()
    pidfile = '{}/{}.pid'.format(config.get('nust','dbdir'),pname)
    rv = [None,None]
    try:
        os.remove(pidfile)
        rv = [True,'OK']
    except OSError, e:
        rv = [False, e]
    return rv
#---------------------------------------------------------------
#---------------------------------------------------------------
def get_or_create_pidfile():
    pid = os.getpid()
    pname = get_pname()
    pidfile = '{}/{}.pid'.format(config.get('nust','dbdir'),pname)
    oldpid = 0
    rv = [None,None]
    try:
        with open(pidfile,'r') as f:
            oldpid = f.readline(6)
            oldpid = int(oldpid)
        # PID-file found
        t = ''
        try:
            with open('/proc/{}/cmdline'.format(oldpid),'r') as p:
                pass
            rv = [False,'ERROR! PID file ({}) found, {} process already running with PID={}.'.format(pidfile,pname,oldpid)]
        except:
            # PID-file found, but no process
            rv = [None,'WARNING! PID file ({}) found, but no process with PID={}. File removed.'.format(pidfile,oldpid)]
            oldpid = 0
    except ValueError:
        # PID-file found, but empty or not PID-file.
        oldpid = 0
        rv = [None,'WARNING! PID file ({}) found, but it\'s no PID-file. File removed.'.format(pidfile)]
    except IOError, e:
        try:
            with  open(pidfile,'w') as f:
                oldpid = 0
                rv[1] = ''
        except IOError, e:
            rv = [False,'Can\'t create PID-file ({}), exiting...\n{}\n'.format(pidfile,e)]
    # creating NEW pidfile
    if (oldpid == 0):
        try:
            with  open(pidfile,'w') as f:
                f.seek(0)
                f.write('{}'.format(pid))
            rv[0] = True
        except IOError, e:
            rv = [False,'Can\'t create PID-file ({}), exiting...\n{}\n'.format(pidfile,e)]
    return rv
#---------------------------------------------------------------
#---------------------------------------------------------------
def get_or_create_db(pname=None, dbdir=None, dbmode=0600):
    tk = True
    if not (pname or dbdir):
        return None
    dbfname = '{0}{2}{1}.db'.format(dbdir,pname,os.sep)    
    db = shelve.open(dbfname)    
    t = db.get(u8('VhostInitialConfig'),None)
    if (t != VhostInitialConfig):
        db[u8('VhostInitialConfig')] = VhostInitialConfig
        tk = False
    t = db.get(u8('CHECKSUMS'),None)
    if (not t) or (not tk):
        db[u8('CHECKSUMS')] = {}
    t = db.get(u8('CONFIGS'),None)
    if (not t) or (not tk):
        db[u8('CONFIGS')] = {}
    db.sync()
    return db
#---------------------------------------------------------------
#---------------------------------------------------------------
def get_vhosts_conf(DB,files):
    VH = []
    cfg_line=re.compile(r'#uwsgi#\s+(\w+)\s+(.+)')
    cfg_get_socks=re.compile(r'uwsgi_pass\s+([\w\:\-\/]+)')
    cfg_line_rem_comments = re.compile(r'(.+)#')
    for cf in files:
        cf_hash = get_file_hash(cf)
        t = DB.get(u8('CHECKSUMS'),None)
        if t:
            t = t.get(cf,None)
        if (t and t == cf_hash):
            #print('F:{}  -- hash not changed'.format(cf))
            continue
        fname = cf.split(os.sep)[-1]
        lines = {}
        socks = []
        linesc = 0
        try:
            f = open(cf,'r')
        except:
            continue
        for cline in f.xreadlines():
            re_m = cfg_line.match(cline)
            if (re_m):
                v = re_m.group(2)
                re_mm = cfg_line_rem_comments.match(v)
                if (re_mm):
                    v = re_mm.group(1)
                if (v):
                    linesc += 1
                    lines[re_m.group(1).upper()] = v.strip()
            else:
                re_m = cfg_get_socks.search(cline)
                if (re_m):
                    s = re_m.group(1)
                    if (s.startswith('unix:')):
                        s = s.rpartition(':')[2]
                    socks.append(s)
        if (linesc < 1):
            continue
        else:
            if not lines.get('SOCKET',None):
                try:
                    lines['SOCKET'] = socks[0]
                except:
                    pass
            lines['FILE'] = cf
            lines['FILEHASH'] = cf_hash
            VH.append(lines.copy())
    return VH
#---------------------------------------------------------------
def parse_conf(DB,C):
    H = DB.get(u8('VhostInitialConfig'),{})
    opts = H.keys()
    opts.sort()
    #opts.extend(['FILE','FILEHASH'])
    for i in opts:
        v = C.get(i,None)
        if v:
            H[i][0] = v
    return H
#---------------------------------------------------------------
def mk_conf(DB,CFS):
    VH = []
    for N in CFS:
        H = parse_conf(DB,N)
        VH.append(H.copy())
    # error detection 
    for cfg in VH:
        err = []
        ui = None
        for i in cfg.keys():
            if (cfg[i][2] and not cfg[i][0]):
                err.append(i)
                continue
            if (i == 'USER'):
                try:
                    ui = pwd.getpwnam(cfg[i][0])
                except KeyError:
                    err.append(i)
                if (ui) :
                    try:
                        hdir = os.stat(ui.pw_dir)
                        if (hdir.st_mode & stat.S_IFDIR):
                            pass
                        else:
                            err.append(i)
                    except:
                        err.append(i)
        if err:
            cfg['ERR']= err
            cfg['OK'] = False
            T = DB[u8('CONFIGS')]
            if (T.has_key(cfg['FILE'][0])):
                del T[cfg['FILE'][0]]
            DB[u8('CONFIGS')] = T
            DB.sync()
        else:
            cfg['OK'] = True
            del cfg['ERR']
            # calculate relative paths
            ui = None
            cfg['HOME'][0] = glob_homedir(cfg['USER'][0],cfg['HOME'][0])
            for i in VIC_paths:
                if cfg.has_key(i):
                    cfg[i][0] = glob_homedir(cfg['USER'][0],cfg[i][0])
                    v = cfg[i][0]
                    if (v[0] != os.sep):
                        h = cfg['HOME'][0]
                        sep = os.sep if (h[-1] != os.sep) else ''
                        v = '{0}{1}{2}'.format(h,sep,v)
                        cfg[i][0]=v
            f = cfg['FILE'][0]
            fh= cfg['FILEHASH'][0]
            # all OK for this host, updating DB
            T = DB[u8('CHECKSUMS')]
            T[f] = fh
            DB[u8('CHECKSUMS')] = T
            #
            T = DB[u8('CONFIGS')]
            T[f] = cfg
            DB[u8('CONFIGS')] = T
            DB.sync()
    return VH
#---------------------------------------------------------------
#---------------------------------------------------------------
def main_process(argv=sys.argv):
    if argv is None:
        argv = sys.argv
    if not parse_args():
        return(2)
    pp = get_or_create_pidfile()
    if (pp[0] and not pp[1]):
        pass
    elif (pp[0]):
        print(pp[1])
    else:
        print(pp[1])
        return(2)
    Pname = get_pname()
    DB = get_or_create_db(Pname,config.get('nust','dbdir'))
    VhConfs = get_vhosts_conf(DB,glob.glob(config.get('nust','vhosts')))
    VhConfs = mk_conf(DB,VhConfs)
    # ERROR REPORTING 
    for C in VhConfs:
        if (C.get('OK',False)):
            pass
        else:
            # show errer messages
            print('ERR in {0}:  '.format(C['FILE'][0]))
            for e in C['ERR']:
                print('\t {0} option mismatch. '.format(e))
    # working with configs in DB 
    VhConfs = DB.get(u8('CONFIGS'), {})
    k = VhConfs.keys()
    k.sort()
    for cc in k:
        C = VhConfs[cc]
        if (C.get('OK',False)):
            #
            line = ''
            for c in C:
                if c in ['OK', 'FILE', 'FILEHASH']: 
                    continue
                if ((C[c][2] or (C[c][0] and not C[c][2])) and C[c][1]):
                    line += ' {0} {1}'.format(C[c][1],C[c][0])
            s = {
                    'FILE': C['FILE'][0],
                'FILEHASH': C['FILEHASH'][0],
                    'HOME': C['HOME'][0],
                     'PRJ': C['PRJ'][0],
                     'PID': C['PID'][0],
                  'SOCKET': C['SOCKET'][0],
                 'COMMAND': line,
            }
            VhStart.append(s)
    for i in xrange(len(VhStart)):
        start_uwsgi(VhStart[i],[config.get('nust','uwsgi'),config.get('nust','uwsgi_def_args')])
    DB.close()
    pp = remove_pidfile()
    if not pp[0]:
        print('Can\'t remove PID-file.\n{}\n'.format(pp[1]))
    return(0)
#---------------------------------------------------------------
#---------------------------------------------------------------
