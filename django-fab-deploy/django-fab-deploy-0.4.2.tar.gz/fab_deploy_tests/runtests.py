#!/usr/bin/env python
import sys
import os.path

# always use fab_deploy from the checkout, not the installed version
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, path)

import unittest
from fabric.api import env
from fab_deploy_tests.tests import *

if __name__ == '__main__':
    env._OS = sys.argv[1]
    env._VM_NAME = sys.argv[2]
    sys.argv = [sys.argv[0]] + sys.argv[3:]
    unittest.main()
