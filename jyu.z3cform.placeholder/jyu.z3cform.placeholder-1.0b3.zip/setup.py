from setuptools import setup, find_packages

version = '1.0b3'

setup(name='jyu.z3cform.placeholder',
      version=version,
      description="Integrates jQuery Watermark for z3c.form on Plone.",
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
      url='http://pypi.python.org/pypi/jyu.z3cform.placeholder',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['jyu', 'jyu.z3cform'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Plone requirements: -*-
          'five.grok',
	  'plone.directives.form',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
