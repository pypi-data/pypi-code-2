# -*- coding: utf-8 -*-
# Copyright (C) 2008-2010, Luis Pedro Coelho <lpc@cmu.edu>
# vim: set ts=4 sts=4 sw=4 expandtab smartindent:
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.
'''
Task: contains the Task class.

This is the main class for using jug.

There are two main alternatives:

- Use the ``Task`` class directly to build up tasks, such as
  ``Task(function, arg0, ...)``.
- Rely on the ``TaskGenerator`` decorator as a shortcut for this.
'''

from __future__ import division
import hashlib
import os
import cPickle as pickle
import itertools

alltasks = []

class Task(object):
    '''
    Task
    ----

    T = Task(f, dep0, dep1,..., kw_arg0=kw_val0, kw_arg1=kw_val1, ...)

    Defines a task, which is roughly equivalent to

    f(dep0, dep1,..., kw_arg0=kw_val0, kw_arg1=kw_val1, ...)

    '''
    store = None
    def __init__(self, f, *args, **kwargs):
        if f.func_name == '<lambda>':
            raise ValueError('''jug.Task does not work with lambda functions!

Write an email to the authors if you feel you have a strong reason to use them (they are a bit
tricky to support since the general code relies on the function name)''')

        self.name = '%s.%s' % (f.__module__, f.__name__)
        self.f = f
        self.args = args
        self.kwargs = kwargs
        self.finished = False
        self.loaded = False
        self._hash = None
        self._lock = None
        self._can_load = False
        alltasks.append(self)

    def run(self, force=False):
        '''
        task.run(force=False)

        Performs the task.

        Parameters
        ----------
          force : if True, always run the task (even if it ran before)
        '''
        assert self.can_run()
        assert force or not self.finished
        args = [value(dep) for dep in self.args]
        kwargs = dict((key,value(dep)) for key,dep in self.kwargs.iteritems())
        self._result = self.f(*args,**kwargs)
        name = self.hash()
        self.store.dump(self._result, name)
        self.finished = True
        return self._result

    def _get_result(self):
        if not self.finished: self.load()
        return self._result

    result = property(_get_result,doc='Result value')


    def can_run(self):
        '''
        bool = task.can_run()

        Returns true if all the dependencies have their results available.
        '''
        for dep in self.dependencies():
            if not dep.finished and not dep.can_load():
                return False
        return True

    def load(self):
        '''
        t.load()

        Loads the results from the storage backend.
        '''
        assert self.can_load()
        self._result = self.store.load(self.hash())
        self.finished = True

    def unload(self):
        '''
        t.unload()

        Unload results (can be useful for saving memory).
        '''
        self._result = None
        self.finished = False

    def unload_recursive(self):
        '''
        t.unload_recursive()

        Equivalent to

        for tt in recursive_dependencies(t): tt.unload()
        '''
        self.unload()
        for dep in self.dependencies():
            dep.unload_recursive()


    def dependencies(self):
        '''
        for dep in task.dependencies():
            ...

        Iterates over all the first-level dependencies of task `t`

        Parameters
        ----------
          self : Task
        Returns
        -------
          A generator over all of `self`'s dependencies
        See Also
        --------
          `recursive_dependencies`
        '''
        queue = [self.args, self.kwargs.values()]
        while queue:
            deps = queue.pop()
            for dep in deps:
                if type(dep) is Task:
                    yield dep
                elif type(dep) in (list,tuple):
                    queue.append(dep)
                elif type(dep) is dict:
                    queue.append(dep.itervalues())


    def can_load(self, store=None):
        '''
        bool = task.can_load()

        Returns whether result is available.
        '''
        if store is None:
            store = self.store
        if self.finished: return True
        if not self._can_load:
            self._can_load = store.can_load(self.hash())
        return self._can_load

    def hash(self):
        '''
        fname = t.hash()

        Returns the hash for this task.

        The results are cached, so the first call can be much slower than
        subsequent calls.
        '''
        if self._hash is None:
            M = hashlib.md5()
            def update(elems):
                for n,e in elems:
                    M.update(pickle.dumps(n))
                    if type(e) == Task:
                        M.update(e.hash())
                    elif type(e) in (list, tuple):
                        update(enumerate(e))
                    elif type(e) == dict:
                        update(e.iteritems())
                    else:
                        M.update(pickle.dumps(e))
            M.update(self.name)
            update(enumerate(self.args))
            update(self.kwargs.iteritems())
            self._hash = M.hexdigest()
        return self._hash

    def __str__(self):
        '''String representation'''
        return 'Task: %s()' % self.name

    def __repr__(self):
        '''Detailed representation'''
        return 'Task(%s, args=%s, kwargs=%s)' % (self.name, self.args, self.kwargs)

    def lock(self):
        '''
        locked = task.lock()

        Tries to lock the task for the current process.

        Returns True if the lock was acquired. The correct usage pattern is::

            locked = task.lock()
            if locked:
                task.run()
            else:
                # someone else is already running this task!

        Not that using can_lock() can lead to race conditions. The above
        is the only fully correct method.

        Returns
        -------
          Whether the lock was obtained.
        '''
        if self._lock is None:
            self._lock = self.store.getlock(self.hash())
        return self._lock.get()

    def unlock(self):
        '''
        task.unlock()

        Releases the lock.

        If the lock was not held, this may remove another thread's lock!
        '''
        self._lock.release()

    def is_locked(self):
        '''
        is_locked = t.is_locked()

        Note that only calling lock() and checking the result atomically checks
        for the lock(). This function can be much faster, though, and, therefore
        is sometimes useful.

        Returns
        -------
            Whether the task **appears** to be locked.

        See Also
        --------
        - lock()
        - unlock()
        '''
        if self._lock is None:
            self._lock = self.store.getlock(self.hash())
        return self._lock.is_locked()


def topological_sort(tasks):
    '''
    topological_sort(tasks)

    Sorts a list of tasks topologically in-place. The list is sorted when
    there is never a dependency between tasks[i] and tasks[j] if i < j.
    '''
    sorted = []
    whites = set(tasks)
    def dfs(t):
        for dep in t.dependencies():
            if dep in whites:
                whites.remove(dep)
                dfs(dep)
        sorted.append(t)
    while whites:
        next = whites.pop()
        dfs(next)
    tasks[:] = sorted

def recursive_dependencies(t, max_level=-1):
    '''
    for dep in recursive_dependencies(t, max_level=-1):
        ...

    Returns a generator that lists all recursive dependencies of task

    Parameters
    ----------
      t : task
      max_level : Maximum recursion depth. Set to -1 or None for no recursion limit.
    Returns
    -------
      A generator
    '''
    if max_level is None:
        max_level = -1
    if max_level == 0:
        return

    for dep in t.dependencies():
        yield dep
        for d2 in recursive_dependencies(dep, max_level - 1):
            yield d2

def value(elem):
    '''
    value = value(task)

    Loads a task object recursively. This correcly handles lists,
    dictonaries and eny other type handled by the tasks themselves.
    '''
    if type(elem) is Task:
        return elem.result
    elif type(elem) is list:
        return [value(e) for e in elem]
    elif type(elem) is tuple:
        return tuple([value(e) for e in elem])
    elif type(elem) is dict:
        return dict((x,value(y)) for x,y in elem.iteritems())
    else:
        return elem

def CachedFunction(f,*args,**kwargs):
    '''
    value = CachedFunction(f, *args, **kwargs)

    is equivalent to:

    task = Task(f, *args, **kwargs)
    if not task.can_load():
        task.run()
    value = task.result

    That is, it calls the function if the value is available,
    but caches the result for the future.
    '''
    t = Task(f,*args, **kwargs)
    if not t.can_load():
        if not t.can_run():
            raise ValueError('jug.CachedFunction: unable to run task %s' % t)
        t.run()
    return t.result

def TaskGenerator(f):
    '''
    @TaskGenerator
    def f(arg0, arg1, ...)
        ...

    Turns f from a function into a task generator.

    This means that calling ``f(arg0, arg1)`` results in:
    ``Task(f, arg0, arg1)``
    '''
    from functools import wraps
    @wraps(f)
    def task_generator(*args, **kwargs):
        return Task(f, *args, **kwargs)
    task_generator.__name__ = ('TaskGenerator(%s)' % task_generator.__name__)
    return task_generator 

