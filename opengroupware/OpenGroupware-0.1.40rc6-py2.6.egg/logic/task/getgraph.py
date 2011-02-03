#!/usr/bin/python
# Copyright (c) 2010 Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
from sqlalchemy import *
import coils.core
from coils.foundation import Project, Appointment, Contact, Enterprise

class Get(coils.core.Command):
    __domain__ = "task"
    __operation__ = "get-graph"
    root = None

    def __init__(self):
        coils.core.Command.__init__(self)

    def _chase_root(self, task):
        if (task.parent_id is None):
            return task
        else:
            parent = self._ctx.run_command(id=task.parent_id)
            if (parent is not None):
                return self._chase_root(parent)
            else:
                return task
        raise COILSException(500, 'Incoherent condition in Logic command get-graph')

    def _get_children(self, task):
        db = self._ctx.db_session()
        query = db.query(Task).filter(Task.parent_id == task.object_id)
        return self._ctx.access_manager.filter_by_access(self._ctx, 'r', query.all())

    def _get_graph(self, task):
        graph = { }
        for child in self._get_children(task):
            graph[child.object_id] = self._get_graph(child)
        return graph

    def run(self, **params):
        db = self._ctx.db_session()
        if (params.has_key('id')):
            x = params['id']
            query = db.query(Task).filter(Task.object_id == x)
            data = self._ctx.access_manager.filter_by_access(self._ctx, 'r', query.all())
        elif (params.has_key('object')):
            x = params['object']
            # Object was already aquired, this check seems paranoid; is paranoia a virtue?
            data = self._ctx.access_manager.filter_by_access(self._ctx, 'r', [x])
        else:
            raise COILSException(404, "No Task provided to command get-graph")
        if (len(data) == 0):
            raise COILSException(401, "No access to specified task")
        task = data[0]
        root = self._chase_root(task)
        self._result = { root.object_id : self._get_graph(root) }
