from setuptools import setup, find_packages

version = '1.0b6'

setup(name='jyu.formwidget.object',
      version=version,
      description="Introduces experimental schema.Object support for plone.autoform and plone.app.z3cform.",
      long_description=open("README.txt").read() + "\n" +
                       open("HISTORY.txt").read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Asko Soukka',
      author_email='asko.soukka@iki.fi',
      url='http://pypi.python.org/pypi/jyu.formwidget.object',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['jyu', 'jyu.formwidget'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Requires grok and z3cform for Plone: -*-
          'five.grok',
          'plone.autoform',
          'plone.app.z3cform',
          # -*- Requires monkeypatcher to fix formwidget traversal: -*-
          'collective.monkeypatcher',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
