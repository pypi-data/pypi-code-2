from setuptools import setup

setup(name='djangocms-utils',
      version='0.9b',
      description='Utilities for django-cms',
      author='Oyvind Saltvik',
      author_email='oyvind.saltvik@gmail.com',
      url='http://bitbucket.org/fivethreeo/djangocms-utils/',
      packages = ['djangocms_utils', 'djangocms_utils.templatetags'],
      test_suite = 'djangocms_utils.runtests.runtests'
)
