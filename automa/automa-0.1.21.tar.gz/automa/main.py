#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ex:ts=4:sw=4:sts=4:et
# -*- tab-width: 4; c-basic-offset: 4; indent-tabs-mode: t -*-
#
# Copyright (C) 2010-2011 Marco Pantaleoni. All rights reserved.
# Marco Pantaleoni <marco.pantaleoni@gmail.com>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License version 2 as
#    published by the Free Software Foundation.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

__author__    = "Marco Pantaleoni"
__copyright__ = "Copyright (C) 2010-2011 Marco Pantaleoni"
__license__   = "GPL v2"

import os
import sys
import optparse

from automa.tasks import task, Task, TaskContext
from automa.opts import options
from automa.path import Path
from automa.log import *
import automa.virtual

PROGNAME = 'automa'

DEFAULT_AUTOMATE_FILE = 'automate.py'

def usage():
    sys.stderr.write("%s TASKNAME\n" % sys.argv[0])

def load_module(pathname):
    """Dynamically load a Python module."""
    import imp
    import traceback
    try:
        import hashlib
        m = hashlib.md5()
        m.update(pathname)
        mhash = m.hexdigest()
    except ImportError:
        import md5
        mhash = md5.new(pathname).hexdigest()
    f_in = open(pathname, 'rb')
    try:
        py_mod = imp.load_source(mhash, pathname, f_in)
    except ImportError, x:
        traceback.print_exc(file = sys.stderr)
        raise
    except:
        traceback.print_exc(file = sys.stderr)
        raise
    finally:
        try: fin.close()
        except: pass
    return py_mod

def main():
    """Program entry point."""
    import cmdutils
    from setup_info import version

    def run_named_task(taskname, opts):
        task = Task.TaskFromName(taskname)
        ctxt = TaskContext(task, global_cmdline_opts=opts)
        ctxt.run()

    log_level_choices = [
        ('VERBOSE_DEBUG', cmdutils.log.Logger.VERBOSE_DEBUG, "very verbose messages"),
        ('DEBUG', cmdutils.log.Logger.DEBUG, "debug messages"),
        ('INFO', cmdutils.log.Logger.INFO, "informational messages"),
        ('NOTIFY', cmdutils.log.Logger.NOTIFY, "more useful information messages"),
        ('WARN', cmdutils.log.Logger.WARN, "warning"),
        ('ERROR', cmdutils.log.Logger.ERROR, "an error"),
        ('FATAL', cmdutils.log.Logger.FATAL, "a fatal error")
    ]

    opt_log_level_choices = [l[0] for l in log_level_choices]
    opt_log_level_default = 'NOTIFY'

    parser = optparse.OptionParser(prog=PROGNAME,
                                   usage="usage: %prog [options] task1 [task1 options] ... [taskN [taskN options]]",
                                   version=version)
    parser.disable_interspersed_args()
    parser.set_defaults(logger = None,
                        loglevel = opt_log_level_default,
                        file = DEFAULT_AUTOMATE_FILE)
    parser.add_option('--file', '-f', dest='file',
                      help='parse FILE for task definitions (default: %r)' % DEFAULT_AUTOMATE_FILE,
                      metavar='FILE')
    parser.add_option('--list', action='store_true', dest='list',
                      help='list tasks')
    parser.add_option('--dry-run', '--dryrun', '--dry', '-n', dest='dry_run',
                      action='store_true',
                      help='simulate: don\'t execute commands and actions')
    parser.add_option('--ignore-errors', '--ignoreerrors', dest='ignore_errors',
                      action='store_true',
                      help='don\'t bail out on errors (except fatal ones)')
    parser.add_option('--loglevel', dest='loglevel',
                      choices=opt_log_level_choices,
                      help='log level (default: %s, possible values: %s)' % (opt_log_level_default, ','.join(opt_log_level_choices)))

    (opts, args) = parser.parse_args()

    level = cmdutils.log.Logger.NOTIFY
    for ll in log_level_choices:
        if ll[0] == opts.loglevel:
            level = ll[1]
            break
    logger = cmdutils.log.Logger([(level, sys.stderr)])
    opts.logger = logger
    options.logger        = logger
    options.args          = opts
    options.dry_run       = opts.dry_run
    options.ignore_errors = opts.ignore_errors

    #subparsers = parser.add_subparsers(help='task help')
    automate_path = Path(opts.file)
    if automate_path.isabs:
        load_module(automate_path.pathname)
    else:
        load_module(Path('automate.py').abspath.pathname)

    if opts.list:
        print "Tasks found:"
        for task in Task.Tasks():
            print "\t%-15s %s" % (task.name, task.fullname)
        if len(args) == 0:
            sys.exit(0)

    if len(args) == 0:
        error("No task specified.")
        sys.exit(1)

    while args:
        taskname = args[0]
        args = args[1:]
        assert not taskname.startswith('-')
        task = Task.TaskFromName(taskname)
        if task is None:
            error("can't find task with name %r" % taskname)
        assert task
        ctxt = TaskContext(task, global_cmdline_opts=opts)
        args = ctxt.parse_args(args)
        ctxt.run()

##    for task in Task.Tasks():
##        assert isinstance(task, Task)
##        help_text = task.__doc__ or '%s task' % task.name
##        subparser = subparsers.add_parser(task.name, help=help_text)
##        subparser.set_defaults(func=lambda args, n=task.name: run_named_task(n, args))
##
##    args = parser.parse_args()
##
##
##    # execute the task function
##    args.func(args)

if __name__ == '__main__':
    main()
