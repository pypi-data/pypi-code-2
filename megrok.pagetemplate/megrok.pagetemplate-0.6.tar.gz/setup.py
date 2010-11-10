# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

version = '0.6'
history = open(os.path.join("docs", "HISTORY.txt")).read()
readme = open(os.path.join(
    "src", "megrok", "pagetemplate", "README.txt")).read()

setup(name='megrok.pagetemplate',
      version=version,
      description=("Page template component for Grok, "
                   "based on zope.pagetemplate"),
      long_description = u"%s\n\n%s" % (readme, history),
      classifiers=[
        'Environment :: Web Environment',
        'Framework :: Zope3',
        'Intended Audience :: Other Audience',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        ],
      keywords='Grok Pagetemplate Zope Layout Dolmen',
      author='Souheil Chelfouh',
      author_email='trollfot@gmail.com',
      url='http://pypi.python.org/pypi/megrok.pagetemplate',
      license='GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages=['megrok'],
      include_package_data=True,
      zip_safe=False,
      platforms = 'Any',
      extras_require={'test': [
          'zope.browserpage',
          'zope.container',
          'zope.interface',
          'zope.site',
          'zope.traversing',
          'zope.security',
          ]},
      install_requires=[
          'grokcore.component',
          'grokcore.view>=2.0',
          'martian',
          'setuptools',
          'zope.component >= 3.9.1',
          'zope.pagetemplate',
          'zope.publisher',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
