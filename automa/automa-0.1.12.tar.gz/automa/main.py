#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ex:ts=4:sw=4:sts=4:et
# -*- tab-width: 4; c-basic-offset: 4; indent-tabs-mode: t -*-
#
# Copyright (C) 2010 Marco Pantaleoni. All rights reserved
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
__copyright__ = "Copyright (C) 2010 Marco Pantaleoni"
__license__   = "GPL v2"

import os
import sys
import argparse

from automa.tasks import task, Task, TaskContext
from automa.opts import options
import automa.virtual

PROGNAME = 'Automa'

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

    def run_named_task(taskname, args):
        task = Task.TaskFromName(taskname)
        ctxt = TaskContext(task, cmdline_args=args)
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

    parser = argparse.ArgumentParser(prog=PROGNAME)
    parser.set_defaults(logger = None)
    parser.add_argument('--file', '-f', dest='file',
                        default='automate.py',
                        help='parse this file for task definitions')
    parser.add_argument('--list', action='store_true',
                        help='list tasks')
    parser.add_argument('--dry-run', '--dryrun', '--dry', '-n', dest='dry_run',
                        action='store_true',
                        help='simulate: don\'t execute commands and actions')
    parser.add_argument('--ignore-errors', '--ignoreerrors', dest='ignore_errors',
                        action='store_true',
                        help='don\'t bail out on errors (except fatal ones)')
    parser.add_argument('--loglevel', dest='loglevel',
                        choices=[l[0] for l in log_level_choices],
                        default='NOTIFY',
                        help='log level')
    subparsers = parser.add_subparsers(help='task help')

    load_module(os.path.join(os.path.abspath(os.getcwd()), 'automate.py'))

    for task in Task.Tasks():
        assert isinstance(task, Task)
        help_text = task.__doc__ or '%s task' % task.name
        subparser = subparsers.add_parser(task.name, help=help_text)
        subparser.set_defaults(func=lambda args, n=task.name: run_named_task(n, args))

    args = parser.parse_args()

    level = cmdutils.log.Logger.NOTIFY
    for ll in log_level_choices:
        if ll[0] == args.loglevel:
            level = ll[1]
            break
    logger = cmdutils.log.Logger([(level, sys.stderr)])
    args.logger = logger
    options.logger        = logger
    options.args          = args
    options.dry_run       = args.dry_run
    options.ignore_errors = args.ignore_errors

    # execute the task function
    args.func(args)

if __name__ == '__main__':
    main()
