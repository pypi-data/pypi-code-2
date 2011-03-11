from distutils.core import setup

setup(
  name='django-test',
  version='0.1011dev',
  packages=['django_test', 'django_test.management', 'django_test.management.commands'],
  license='GPL',
  long_description="Awesome replacement for django test runner",
)
