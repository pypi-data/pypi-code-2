# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

version = open(os.path.join(os.path.abspath(os.path.dirname(__file__)),
    'collective', 'testswarm', 'version.txt')).read().strip()

setup(name='collective.testswarm',
    version=version,
    description="Plone TestSwarm integration package",
    long_description="\n".join([open("README.txt").read(),
                                open("HISTORY.txt").read(),
                                "Contributors",
                                "============","",
                                open("CONTRIBUTORS.txt").read()
                                ]),
    classifiers=[
      "Framework :: Plone",
      "Programming Language :: Python",
      "Programming Language :: JavaScript",
      "Topic :: Software Development :: Testing",
      "Topic :: Software Development :: Libraries :: Python Modules",
      "License :: OSI Approved :: GNU Affero General Public License v3"
      ],
    keywords='Plone TestSwarm JavaScript Continuous-Integration',
    author=u'Cillian de Roiste',
    author_email='cillian.deroiste@gmail.com',
    url='http://cillian.wordpress.com',
    license='AGPLv3+',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['collective'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
      'setuptools',
      ],
    extras_require={
        'test':['Products.PloneTestCase','plone.app.testing']
        },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
    )
