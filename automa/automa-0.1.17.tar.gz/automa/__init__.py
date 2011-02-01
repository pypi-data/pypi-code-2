# -*- coding: utf-8 -*-

from automa.opts import options, Options
from automa.shell import sh, cd
from automa.ssh import ssh
from automa.tasks import task, depends, Task, TaskContext, get_active_context, call_task
from automa.path import Path
try:
    from automa.virtual import bootstrap
except:
    pass
