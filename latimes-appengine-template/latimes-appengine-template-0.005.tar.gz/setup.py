"""
Tricks lifted from Django's own setup.py and django_debug_toolbar.
"""
from setuptools import setup, find_packages

setup(
      name='latimes-appengine-template',
      version='0.005',
      description='A basic template to start a new Django application hosted by Google App Engine.',
      author='Ben Welsh',
      author_email='ben.welsh@gmail.com',
      url='https://github.com/datadesk/latimes-appengine-template',
      download_url='git@github.com:datadesk/latimes-appengine-template.git',
      packages=find_packages(),
      package_data={
        'appengine_template': [
             '*.yaml',
             'django.zip',
            ],
        },
      data_files={
        'appengine_template': [
            '.google_appengine/bulkloader.py'
           ]
        },
      entry_points = {
        'console_scripts': [
            'startappengineproject = appengine_template.command:execute_from_command_line',
        ],
    },
)

