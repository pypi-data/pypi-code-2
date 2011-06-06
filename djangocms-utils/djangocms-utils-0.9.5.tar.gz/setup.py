from setuptools import setup

setup(name='djangocms-utils',
      version='0.9.5',
      description='Utilities for django-cms',
      author='Oyvind Saltvik',
      author_email='oyvind.saltvik@gmail.com',
      url='http://github.com/fivethreeo/djangocms-utils/',
      packages = ['djangocms_utils', 'djangocms_utils.templatetags'],
      test_suite = 'djangocms_utils.test.run_tests.run_tests'
)
