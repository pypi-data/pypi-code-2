from setuptools import setup, find_packages
import sys, os

def read(*names):
    values = dict()
    for name in names:
        filename = name+'.txt'
        if os.path.isfile(filename):
            value = open(name+'.txt').read()
        else:
            value = ''
        values[name] = value
    return values

long_description="""
%(README)s

See http://packages.python.org/DjangoPluggableApp/ for the full documentation

News
====

%(CHANGES)s

""" % read('README', 'CHANGES')

version = '0.5'

setup(name='DjangoPluggableApp',
      version=version,
      description="A pluggable system for django applications",
      long_description=long_description,
      classifiers=[
          'Framework :: Django',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: POSIX',
      ],
      keywords='django plugin apps',
      author='Gael Pasgrimaud',
      author_email='gpasgrimaud@bearstech.com',
      url='http://packages.python.org/DjangoPluggableApp/',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'PasteScript',
          'django-webtest',
          'WebTest',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      django-pluggableapp = pluggableapp.scripts:main

      [paste.paster_create_template]
      django_project = pluggableapp.template:DjangoProjectTemplate
      django_app = pluggableapp.template:DjangoAppTemplate

      [django.pluggable_app]
      admin = pluggableapp.apps:admin
      admin_docs = pluggableapp.apps:admin_docs
      pluggable_registration = pluggableapp.apps:registration
      pluggable_pagination = pluggableapp.apps:pagination
      pluggable_reversion= pluggableapp.apps:reversion
      pluggable_messages = pluggableapp.apps:messages
      pluggable_attachments = pluggableapp.apps:attachments
      pluggable_thumbnails = pluggableapp.apps:easy_thumbnails
      """,
      )
