from setuptools import setup

setup(name='djangocms-utils',
      version='0.9.3',
      description='Utilities for django-cms',
      author='Oyvind Saltvik',
      author_email='oyvind.saltvik@gmail.com',
      url='http://github.com/fivethreeo/djangocms-utils/',
      packages = ['djangocms_utils', 'djangocms_utils.templatetags'],
      test_suite = 'djangocms_utils.test.run_tests.run_tests',
      install_requires = ['django-cms>=2.1.0']
)
