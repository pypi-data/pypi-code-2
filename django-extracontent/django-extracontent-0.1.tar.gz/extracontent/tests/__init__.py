from extracontent.tests.testing import *

def run():
    import sys
    from django.conf import settings
    from django.test.simple import run_tests
    failures = run_tests(['extracontent'], verbosity=1)
    if failures:
        sys.exit(failures)