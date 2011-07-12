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

from twisted.trial import unittest
from twisted.internet import task, reactor
from txdpce.dpce import (DeferredParallelCommandExecutor,
    ParallelCommandException)


class TestParallelCommand(unittest.TestCase):
    """
    Tests that check the parallel L{DeferredParallelCommandExecutor} class.
    """

    def testNoFunctions(self):
        """
        If no functions to execute have been registered with the
        DeferredParallelCommandExecutor, it should raise C{RuntimeError}
        when execute is called.
        """
        pce = DeferredParallelCommandExecutor()
        self.assertRaises(RuntimeError, pce.execute)

    def testTwoSuccessfulFunctions(self):
        """
        Run two functions that both succeed and check that the result is
        one of the values they return.
        """
        def check(result):
            self.assertTrue(result is True or result == 3)
        getBool = lambda: True
        getInt = lambda: 3
        pce = DeferredParallelCommandExecutor()
        pce.registerFunction(getBool)
        pce.registerFunction(getInt)
        d = pce.execute()
        d.addCallback(check)
        return d

    def testTwoFunctionsOneSlowOneFast(self):
        """
        Run two simple functions that both succeed and check the result.
        One function is very slow and its deferred will be cancelled.
        """
        def check(result):
            self.assertEqual(result, True)

        def cancel(d):
            pass

        getBool = lambda: True

        def getInt():
            d = task.deferLater(reactor, 1.0, lambda: 3)
            d.addErrback(cancel)
            return d

        pce = DeferredParallelCommandExecutor()
        pce.registerFunction(getBool)
        pce.registerFunction(getInt)
        d = pce.execute()
        d.addCallback(check)
        return d

    def testTwoFunctionsOneSucceedsOneFails(self):
        """
        Run two simple functions, one of which fails and one which
        succeeds.  Check the result.
        """
        def check(result):
            self.assertEqual(result, 3)

        pce = DeferredParallelCommandExecutor()
        pce.registerFunction(lambda: 1 / 0)
        pce.registerFunction(lambda: 3)
        d = pce.execute()
        d.addCallback(check)
        return d

    def testTwoFunctionsOneSucceedsSlowOneFailsFast(self):
        """
        Run two simple functions, one of which fails immediately and one
        which succeeds after a while.  Check the result.
        """
        def check(result):
            self.assertEqual(result, 3)

        pce = DeferredParallelCommandExecutor()
        pce.registerFunction(lambda: 1 / 0)
        pce.registerFunction(lambda: task.deferLater(reactor, 0.2, lambda: 3))
        d = pce.execute()
        d.addCallback(check)
        return d

    def testTwoFunctionsThatBothFail(self):
        """
        Run two simple functions that both fail. Check the result
        has the failures.
        """
        def check(result):
            self.assertTrue(isinstance(result.value, ParallelCommandException))
            failures = result.value.args[0]
            self.assertTrue(isinstance(failures[0].value, ZeroDivisionError))
            self.assertTrue(isinstance(failures[1].value, AttributeError))

        pce = DeferredParallelCommandExecutor()
        pce.registerFunction(lambda x: 1 / 0)  # Raises ZeroDivisionError
        pce.registerFunction(lambda x: x.blah)  # Raises AttributeError
        d = pce.execute('dummy')
        d.addErrback(check)
        return d
