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

import sys
import traceback
import datetime

def get_active_context():
    return TaskContext.Active()

def call_task(*args, **kwargs):
    cntxt = TaskContext.Active()
    cntxt.call_task(*args, **kwargs)

class Task(object):
    __doc__ = ""
    _tasks            = []
    _task_by_name     = {}
    _task_by_fullname = {}

    def __init__(self, func):
        self.func     = func
        self.__name__ = func.__name__
        self.name     = func.__name__
        self.fullname = "%s.%s" % (func.__module__, func.__name__)
        if hasattr(func, '__doc__'):
            self.__doc__ = func.__doc__
        self.depends  = []

        self._started    = None
        self._completed  = None
        self._started_by = None

        self._tasks.append(self)
        self._task_by_name[self.name] = self
        self._task_by_fullname[self.fullname] = self

    def __call__(self, *args, **kwargs):
        ctxt = TaskContext(self, args, kwargs)
        return ctxt.run()

    def __str__(self):
        return '<Task %r>' % self.fullname

    def __repr__(self):
        return '<Task %r>' % self.fullname

    @classmethod
    def Tasks(cls):
        return list(cls._tasks)

    @classmethod
    def TaskFromShortName(cls, name):
        return cls._task_by_name.get(name, None)
    @classmethod
    def TaskFromFullName(cls, name):
        return cls._task_by_fullname.get(name, None)
    @classmethod
    def TaskFromName(cls, name):
        return cls.TaskFromFullName(name) or cls.TaskFromShortName(name)

def task(f):
    """@task decorator"""
    if isinstance(f, Task):
        return f
    return Task(f)

class depends(object):
    """@depends decorator"""
    def __init__(self, *args):
        self.args = args

    def __call__(self, f):
        if not isinstance(f, Task):
            f = Task(f)
        f.depends = self.args
        return f

class TaskContext(object):
    _active_task_context = None

    def __init__(self, task, args=None, kwargs=None, cmdline_args=None,
                 called_from=None, level=1):
        self.task   = task
        self.args   = args or []
        self.kwargs = kwargs or {}
        self.cmdline_args = cmdline_args

        self.called_from = called_from
        self.level       = level
        self._logger     = None

        self.executed    = []  # tasks which have been started
        self.completed   = []  # tasks which have been executed up to completion

    def __repr__(self):
        return '<TaskContext 0x%X task:%r>' % (id(self), self.task.fullname)

    def run(self):
        TaskContext._active_task_context = self
        self.notify("TASK %s CALLED (ctxt:0x%X)" % (self.task.name, id(self)), color='bold magenta', level=self.level-1)
        assert isinstance(self.task, Task)
        if len(self.task.depends) > 0:
            self.notify("DEPENDS ON %s" % str(self.task.depends), color='bold magenta')
            for item in self.task.depends:
                if isinstance(item, basestring):
                    item = Task.TaskFromName(item)
                if isinstance(item, Task):
                    if not self.task_is_needed(item):
                        self.notify("TASK %s IS NOT NEEDED" % item, color='bold magenta')
                        continue
                    self.notify("NEEDED %s BY %s" % (item, self.task), color='bold magenta')
                    ctxt = TaskContext(item, cmdline_args=self.cmdline_args)
                    ctxt._logger = self._logger
                    ctxt.called_from = self
                    ctxt.level = self.level + 1
                    ctxt.run()
        self.notify("TASK %s STARTED" % self.task.name, color='bold magenta', level=self.level-1)
        self.executed.append(self.task)
        if self.called_from:
            self.task._started_by = self.called_from.task
        self.task._started = datetime.datetime.now()
        rv = self.task.func(self)
        self.task._completed = datetime.datetime.now()
        self.completed.append(self.task)
        self.notify("TASK %s COMPLETED" % self.task.name, color='bold magenta', level=self.level-1)
        return rv

    def task_is_needed(self, task):
        assert isinstance(task, Task)
        return task._started is None

    def __call__(self, *args, **kwargs):
        self.args   = args or self.args
        self.kwargs = kwargs or self.kwargs
        return self.run()

    def call_task(self, taskname, *args, **kwargs):
        task = Task.TaskFromName(taskname)
        ctxt = TaskContext(task, args=args, kwargs=kwargs, cmdline_args=self.cmdline_args)
        ctxt._logger = self._logger
        ctxt.called_from = self
        ctxt.level = self.level + 1
        return ctxt.run()

    @classmethod
    def Active(cls):
        return TaskContext._active_task_context

    @property
    def logger(self):
        if self._logger:
            return self._logger
        if self.cmdline_args:
            self._logger = self.cmdline_args.logger
        else:
            import cmdutils, sys
            self._logger = cmdutils.log.Logger([(cmdutils.log.Logger.NOTIFY, sys.stderr)])
        return self._logger

    def _indent_text(self, text, amount, space="  "):
        indent = space * amount
        lines = text.split('\n')
        return '\n'.join([(indent + line) for line in lines])

    def debug(self, msg, color='cyan', level=None, extra_indent=0, *args, **kwargs):
        if level is None:
            level = self.level
        level += extra_indent
        return self.logger.debug(self._indent_text('DEBUG: ' + msg, level),  color=color)
    def info(self, msg, color=None, level=None, extra_indent=0, *args, **kwargs):
        if level is None:
            level = self.level
        level += extra_indent
        return self.logger.info(self._indent_text(msg, level), color=color)
    def notify(self, msg, color='green', level=None, extra_indent=0, *args, **kwargs):
        if level is None:
            level = self.level
        level += extra_indent
        return self.logger.notify(self._indent_text(msg, level), color=color)
    def warn(self, msg, color='bold yellow', level=None, extra_indent=0, *args, **kwargs):
        if level is None:
            level = self.level
        level += extra_indent
        return self.logger.warn(self._indent_text('WARN: ' + msg, level), color=color)
    def error(self, msg, color='bold red', level=None, extra_indent=0, ignore_errors=None, *args, **kwargs):
        if level is None:
            level = self.level
        level += extra_indent
        if ignore_errors is None:
            if self.cmdline_args:
                ignore_errors = self.cmdline_args.ignore_errors
        prefix = 'ERROR: '
        if ignore_errors:
            prefix = 'ERROR (ignored): '
        text = prefix + msg
        exctype, value = sys.exc_info()[:2]
        if exctype is not None:
            text += "\nEXCEPTION\n%s" % traceback.format_exc()
        rv = self.logger.error(self._indent_text(text, level), color=color)
        if not ignore_errors:
            sys.exit(1)
        return rv
    def fatal(self, msg, color='bold red_bg', level=None, extra_indent=0, *args, **kwargs):
        if level is None:
            level = self.level
        level += extra_indent
        text = '\n\nFATAL: ' + msg
        exctype, value = sys.exc_info()[:2]
        if exctype is not None:
            text += "\nEXCEPTION\n%s" % traceback.format_exc()
        text += '\n\n'
        rv = self.logger.error(self._indent_text(text, level), color=color)
        sys.exit(1)
        return rv
