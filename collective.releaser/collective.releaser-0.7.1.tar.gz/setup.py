# -*- coding: utf-8 -*-
"""
This module contains the tool of collective.releaser
"""
import os
from setuptools import setup, find_packages

version = '0.7.1'

def read(*args):
    filename = os.path.join(*args)
    return open(filename).read() + '\n\n'

long_description = read('README.txt') + read('docs', 'README.txt') + read('CHANGES')

tests_require=['zope.testing', 'iw.email', 'zope.component', 'zope.interface']

setup(name='collective.releaser',
      version=version,
      description="Setuptools extension to release an egg",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='egg setuptools extension',
      author='Ingeniweb',
      author_email='support@ingeniweb.com',
      url='http://pypi.python.org/pypi/collective.releaser',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      test_suite = "collective.releaser.tests.test_releaserdocs.test_suite",
      install_requires=[
          'setuptools',
          'zc.buildout',
          # -*- Extra requirements: -*-
          'multiprocessing',
          'collective.dist',
          'docutils',
          'ZopeSkel',
          'PasteScript',
          'virtualenv',
      ],
      tests_require=tests_require,
      extras_require=dict(test=tests_require),
      entry_points = {
        "distutils.commands": [
            "release = collective.releaser.commands.release:release",
            "build_mo = collective.releaser.commands.build_mo:build_mo"],
        "console_scripts": [
            "project_release = collective.releaser.project:make_release",
            "project_deploy = collective.releaser.project:deploy_release",
            "project_diff = collective.releaser.project:diff_releases",
            "project_md5 = collective.releaser.project:console_build_md5",
            "project_eggs = collective.releaser.project:console_project_eggs",
            "release_eggs = collective.releaser.project:release_eggs",
            "package_svn_prepare = collective.releaser.project:console_make_svn_structure_for_package",
            ],
        "distutils.release.post_hook": [
            "upgrade_change_file =  collective.releaser.hook:upgrade_change_file",
            "mail = collective.releaser.hook:mail_hook"],
        "distutils.release.pre_hook": [
            "raise_version =  collective.releaser.hook:raise_version",
            "create_svn_tag = collective.releaser.hook:create_tag"],
        "paste.paster_create_template" : [
            "releaser_project = collective.releaser.templates:ReleaserProject"
            ]
        },
      )
