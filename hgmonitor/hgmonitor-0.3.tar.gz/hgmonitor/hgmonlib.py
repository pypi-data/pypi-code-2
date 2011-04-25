# -*- coding: utf-8 -*-
"""
This is the class library for the mercurial extension hg-monitor with automated
monitor and backup facilities. 
"""

from mercurial import cmdutil, commands, hg, mail, patch, util
from mercurial.i18n import _
import mercurial
from hglib import *
#from autfunc import *
import os
import re
import platform
import datetime
import zipfile
import shutil

def repo_list(root_dirs,mq=False):
    repos = []
    
    def check_mq(repo):
        potential = os.path.join(repo,".hg","patches")
        if mq and os.path.exists(potential) and is_repo(potential):
            repos.append(potential)

    for root_dir in root_dirs:
        if is_repo(root_dir):
            # the directory itself is a repository, stop
            repos = [root_dir]
            check_mq(root_dir)
        else:
            # no repository here, recurse
            kids = [os.path.join(root_dir,thisd) for thisd in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir,thisd))]
            for sub_dir in kids:
                if is_repo(sub_dir):
                    # the directory itself is a repository, stop
                    repos.append(sub_dir)
                    check_mq(sub_dir)

    return repos

def sanitize_standard_options(ui,opts):
    if opts["dir"] == []:
        opts["dir"] += ['.']
    #ui.status(_('options %s\n') % opts)

def monitor_cmd(ui, **opts):
    """
    Enumerates uncommitted and unpushed changes.
    """
    sanitize_standard_options(ui,opts)
    for r in repo_list(opts["dir"], opts.has_key('mq') and opts['mq']):
        repo = hg.repository(ui,r)
        ui.write("{0}\n".format(r))
        ui.pushbuffer()
        commands.status(ui,repo)
        for line in stat_parse(ui.popbuffer()):
            ui.write(' '.join(line)+'\n')
        def_path = repo.ui.config('paths','default')
        if def_path is not None:
            ui.pushbuffer()
            commands.outgoing(ui,repo,def_path)
            for cset in parse_log_output(ui.popbuffer()):
                ui.write("""changeset:   {0.label}\nsummary:     {0.summary}\n""".format(cset))
        if os.path.exists(os.path.join(r,".hg","patches")):
            for f in mq_files(r):
                ui.write( 'MQ {0}\n'.format(f) )

def mlist_cmd(ui, **opts):
    """
    Shows a list of repositories impacted by the given monitor settings.
    """
    sanitize_standard_options(ui,opts)
    #ui.write("Repositories in:  {dir}\n".format(dir=opts["dir"]))
    for r in repo_list(opts["dir"], opts.has_key('mq') and opts['mq']):
        ui.write("{0}\n".format(r))

class LazyZipFile:
    """
    This class wraps zipfile.ZipFile for the purposes of not actually 
    creating a file unless we actually have something to put into it.
    """
    def __init__(self,file,mode):
        self.file = file
        self.mode = mode
        self._zipfile = None

    def init_now(self):
        if self._zipfile is None:
            self._zipfile = zipfile.ZipFile(self.file,self.mode)

    def close(self):
        if self._zipfile is not None:
            self._zipfile.close()

    def write(self,filename,arcname=None):
        self.init_now()
        self._zipfile.write(filename,arcname)
        

def mbackup_cmd(ui, **opts):
    """
    Backs up uncommitted changes to .hg/mbackup and optionally copies this 
    backup to a (remote) file system.
    
    Destination dest is the name of the zip file name in .hg/backup which holds
    the backup.  Auxiliary files may also be created in .hg/backup having the
    same base name with-out the zip extension.  The dest parameter may contain
    the following place-holders which will be expanded:

    - clone: last path component of the directory containing the repository
    - fullclone: full path of repository directory with special chars replaced by '_'
    - date: current date formatted as YYYY-MM-DD
    - datetime: current date and time formatted as YYYY-MM-DD-HH-MM-SS
    - time: current time formatted as HH-MM-SS
    - sysname: the hostname of the computer
    
    TODO:  Options allow including unpushed changesets in this backup.

    """
    sanitize_standard_options(ui,opts)
    #ui.write('Repositories in:  {dir}\n'.format(dir=opts['dir']))
    for r in repo_list(opts['dir'], opts.has_key('mq') and opts['mq']):
        dest = opts['dest']
        d = datetime.datetime.now()
        dest = dest.format(
                    clone=os.path.basename(r),
                    fullclone=r.replace('/','_').replace('\\','_'),
                    date=d.strftime('%Y-%m-%d'),
                    datetime=d.strftime('%Y-%m-%d-%H-%M-%S'),
                    time=d.strftime('%H-%M-%S'),
                    sysname=platform.node())
        if not os.path.exists(os.path.join(r,'.hg','mbackup')):
            os.makedirs(os.path.join(r,'.hg','mbackup'))
        zipfilename = os.path.join(r,'.hg','mbackup',dest)
        zipdest = LazyZipFile(zipfilename,'w')

        repo = hg.repository(ui,r)
        ui.write('{0}\n'.format(r))
        ui.pushbuffer()
        commands.status(ui,repo)
        for line in stat_parse(ui.popbuffer()):
            zipdest.write(os.path.join(r,line[1]),line[1])
        #def_path = repo.ui.config('paths','default')
        #if def_path is not None:
            #ui.pushbuffer()
            #commands.outgoing(ui,repo,def_path)
            #for cset in parse_log_output(ui.popbuffer()):
                #ui.write('''changeset:   {0.label}\nsummary:     {0.summary}\n'''.format(cset))
        if os.path.exists(os.path.join(r,'.hg','patches')) and \
                not (opts.has_key('mq') and opts['mq']):
            for f in mq_files(r):
                f_ = os.path.join('.hg','patches',f)
                zipdest.write(os.path.join(r,f_),f_)
        zipdest.close()
        if zipdest._zipfile is not None:
            ui.write('wrote {0}\n'.format(zipfilename))
            if opts['remote'] != '':
                shutil.copy(zipfilename,opts['remote'])

def mpull_cmd(ui, **opts):
    """
    Pulls incoming changes for all directories in this group.
    """
    sanitize_standard_options(ui,opts)
    for r in repo_list(opts["dir"], opts.has_key('mq') and opts['mq']):
        repo = hg.repository(ui,r)
        def_path = repo.ui.config('paths','default')
        if def_path is None:
            ui.status( "skip {0}:  no default pull source\n".format(r) )
        else:
            ui.status( "pulling in {0}\n".format(r) )
            pull_args = {}
            if opts["update"]:
                pull_args["update"] = True
            if opts.has_key("fetch") and opts["fetch"]:
                pull_args["fetch"] = True
            if opts.has_key("rebase") and opts["rebase"]:
                pull_args["rebase"] = True
            commands.pull(ui,repo,def_path,**opts)

def mpush_cmd(ui, **opts):
    """
    Pushs outgoing changes for all directories in this group.
    """
    sanitize_standard_options(ui,opts)
    for r in repo_list(opts["dir"], opts.has_key('mq') and opts['mq']):
        repo = hg.repository(ui,r)
        def_path = repo.ui.config('paths','default')
        if def_path is None:
            ui.status( "skip {0}:  no default push source\n".format(r) )
        else:
            ui.status( "pushing in {0}\n".format(r) )
            commands.push(ui,repo,def_path)
