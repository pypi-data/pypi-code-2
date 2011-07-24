from setuptools import setup, find_packages

version = '0.2'

setup(name='fourdigits.chosen',
      version=version,
      description="Integrates the Chosen javascript library in Plone",
      long_description=open("README.txt").read() + \
                       open("docs/HISTORY.txt").read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Programming Language :: JavaScript",
        ],
      keywords='',
      author='Roel Bruggink',
      author_email='roel@jaroel.nl',
      url='https://github.com/jaroel/fourdigits.chosen/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['fourdigits'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'five.grok',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins=["ZopeSkel"],
      )
