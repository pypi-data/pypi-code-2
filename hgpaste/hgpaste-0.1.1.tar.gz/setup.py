from setuptools import setup, find_packages

version = '0.1.1'

setup(name='hgpaste',
      version=version,
      description="front-end to serve a hg webdir with paste and other",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='paste hg',
      author='Jeff Hammel',
      author_email='k0scist@gmail.com',
      url='http://k0s.org',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'mercurial',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.app_factory]
      main = hgpaste.factory:make_app
      """,
      )
