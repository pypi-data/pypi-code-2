"""
Unit tests for ``eyes``

Won't run if we let setuptools to install dependancies inside current
directory - we need to install external packages before running test
suite.
"""
import os
import sys

os.environ["DJANGO_SETTINGS_MODULE"] = "eyeswebapp.settings"
from eyeswebapp import settings

def main():
    sys.path.insert(0, os.path.abspath(os.path.curdir))
    from django.test.utils import get_runner
    test_runner = get_runner(settings)(verbosity=1)

    failures = test_runner.run_tests(['core', 'util', 'api'])
    sys.exit(failures)

if __name__ == '__main__':
    main()

