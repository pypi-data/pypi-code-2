# Copyright 2011 Fluidinfo Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you
# may not use this file except in compliance with the License.  You
# may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.  See the License for the specific language governing
# permissions and limitations under the License.

from twisted.internet import defer
from twisted.python import failure


class ParallelCommandException(Exception):
    pass


class DeferredParallelCommandExecutor(object):
    """
    Provides a mechanism for the execution of a command by multiple methods,
    returning the result from the one that finishes first.
    """

    def __init__(self):
        self._functions = []

    def registerFunction(self, func):
        """
        Add func to the list of functions that will be run when execute is
        called.

        @param func: A callable that should be run when execute is called.
        """
        self._functions.append(func)

    def execute(self, *args, **kwargs):
        """
        Run all the functions in self._functions on the given arguments and
        keyword arguments.

        @param args: Arguments to pass to the registered functions.

        @param kwargs: Keyword arguments to pass to the registered functions.

        @raise RuntimeError: if no execution functions have been registered.

        @return: A C{Deferred} that fires when the first of the functions
        finishes.
        """
        if not self._functions:
            raise RuntimeError('No execution functions have been registered.')

        deferreds = [defer.maybeDeferred(func, *args, **kwargs)
                     for func in self._functions]
        d = defer.DeferredList(deferreds, fireOnOneCallback=1, consumeErrors=1)
        d.addCallback(self._done, deferreds)
        return d

    def _done(self, deferredListResult, deferreds):
        """
        Process the result of the C{DeferredList} execution of all the
        functions in self._functions. If result is a tuple, it's the result
        of a successful function, in which case we cancel all the other
        deferreds (none of which has finished yet) and give back the
        result.  Otherwise, all the function calls must have failed (since
        we passed fireOnOneCallback=True to the C{DeferredList} and we
        return a L{ParallelCommandException} containing the failures.

        @param deferredListResult: The result of a C{DeferredList} returned
        by self.execute firing.

        @param deferreds: A list of deferreds for other functions that were
        trying to compute the result.

        @return: Either the result of the first function to successfully
        compute the result or a C{failure.Failure} containing a
        L{ParallelCommandException} with a list of the failures from all
        functions that tried to get the result.
        """
        if isinstance(deferredListResult, tuple):
            # A tuple result means the DeferredList fired with a successful
            # result.  Cancel all other deferreds and return the result.
            result, index = deferredListResult
            for i in range(len(self._functions)):
                if i != index:
                    deferreds[i].cancel()
            return result
        else:
            # All the deferreds failed. Return a list of all the failures.
            failures = [fail for (result, fail) in deferredListResult]
            return failure.Failure(ParallelCommandException(failures))
