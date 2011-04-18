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
