#!/usr/bin/env python
import sys
import os
import unittest
import atexit
from unittest import TestSuite, TestLoader

# always use fab_deploy from the checkout, not the installed version
# plus make fab_deploy_tests available for imports
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, path)

# setup git ssh environment
os.environ['GIT_SSH'] = os.path.join(path, 'fab_deploy_tests', 'git_ssh.sh')

from fab_deploy_tests.tests import *

def load(cases):
    return map(TestLoader().loadTestsFromTestCase, cases)

def help():
    print 'usage: runtests.py "VM_NAME" <what_to_run>\n'

def beep():
    print('\a')

if __name__ == '__main__':
    if len(sys.argv) == 1:
        help()
        sys.exit(1)

    atexit.register(beep)

    FabDeployTest.vm_name = sys.argv[1]
    common_tests = load([BasicTest, SshTest, MysqlTest, CrontabTest])
    suites = {
        'fast': TestSuite(common_tests + load([FastPrepareServerTest, ApacheSetupTest])),
        'slow': TestSuite(load([DeployTest, CustomLayoutDeployTest])),
        'prepare': TestSuite(common_tests + load([PrepareServerTest])),
    }
    suites['all'] = TestSuite([suites['fast'], suites['slow']])

    suite_name = sys.argv[2]
    if suite_name in suites:
        unittest.TextTestRunner().run(suites[suite_name])
    else:
        sys.argv = [sys.argv[0]] + sys.argv[2:]
        unittest.main()
