#
# Copyright (c) 2010 Testrepository Contributors
# 
# Licensed under either the Apache License, Version 2.0 or the BSD 3-clause
# license at the users choice. A copy of both licenses are available in the
# project source as Apache-2.0 and BSD. You may not use this file except in
# compliance with one of these two licences.
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under these licenses is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# license you chose for the specific language governing permissions and
# limitations under that license.

"""Tests for the last command."""

import testtools

from testrepository.commands import last
from testrepository.ui.model import UI
from testrepository.repository import memory
from testrepository.tests import ResourcedTestCase


class TestCommand(ResourcedTestCase):

    def get_test_ui_and_cmd(self,args=()):
        ui = UI(args=args)
        cmd = last.last(ui)
        ui.set_command(cmd)
        return ui, cmd

    def test_shows_last_run(self):
        ui, cmd = self.get_test_ui_and_cmd()
        cmd.repository_factory = memory.RepositoryFactory()
        repo = cmd.repository_factory.initialise(ui.here)
        inserter = repo.get_inserter()
        inserter.startTestRun()
        class Cases(ResourcedTestCase):
            def failing(self):
                self.fail('foo')
            def ok(self):
                pass
        Cases('failing').run(inserter)
        Cases('ok').run(inserter)
        id = inserter.stopTestRun()
        self.assertEqual(1, cmd.execute())
        self.assertEqual('results', ui.outputs[0][0])
        suite = ui.outputs[0][1]
        ui.outputs[0] = ('results', None)
        # We should have seen test outputs (of the failure) and summary data.
        self.assertEqual([
            ('results', None),
            ('values', [('id', id), ('tests', 2), ('failures', 1)])],
            ui.outputs)
        result = testtools.TestResult()
        result.startTestRun()
        try:
            suite.run(result)
        finally:
            result.stopTestRun()
        self.assertEqual(1, result.testsRun)
        self.assertEqual(1, len(result.failures))
