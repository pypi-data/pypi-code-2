#!/usr/bin/env python
# -*0 coding: utf-8 -*-
import sys, os

try:
    from setuptools import setup, find_packages, Command
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages, Command

version = '2.1.4'

setup(name='celery-pylons',
      version=version,
      description="Celery integration with Pylons.",
      long_description=""" """,
      classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Pylons",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: System :: Distributed Computing"
        ],
      keywords='paste pylons celery message queue amqp job task distributed',
      author='Jonathan Stasiak',
      author_email='jonathan.stasiak@gmail.com',
      url='http://pypi.python.org/pypi/celery-pylons',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
        "Pylons>=1.0",
        "celery==2.1.4",
      ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.global_paster_command]
      celeryd=celerypylons.commands:CeleryDaemonCommand
      celerybeat=celerypylons.commands:CeleryBeatCommand
      camqadm=celerypylons.commands:CAMQPAdminCommand
      celeryev=celerypylons.commands:CeleryEventCommand
      """,
      )
