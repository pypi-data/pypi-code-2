import os
import sys

import django

def run_tests():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'test_project.settings'
    from django.conf import settings
    from django.test.utils import get_runner
    test_labels = [settings.INSTALLED_APPS[-1]]
    if django.VERSION[0:2] <= (1, 1):
        # Prior to django 1.2 the runner was a plain function
        runner_fn = get_runner(settings)
        runner = lambda test_labels: runner_fn(test_labels, verbosity=2, interactive=False)
    else:
        # After 1.2 the runner is a class
        runner_cls = get_runner(settings)
        runner = runner_cls(verbosity=2, interactive=False).run_tests
    failures = runner(test_labels)
    sys.exit(failures)
