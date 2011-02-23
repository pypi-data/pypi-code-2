from __future__ import absolute_import
from fabric.api import *
from fabtest import fab
from fab_deploy.utils import run_as
from .base import FabDeployTest

@run_as('root')
def whoami():
    return run('whoami')

class BasicTest(FabDeployTest):
    def test_run_as(self):
        user = fab(whoami)[0]
        self.assertEqual(user, 'root')

