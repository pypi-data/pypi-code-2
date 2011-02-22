from setuptools import setup, find_packages
import os

version = '0.3'
readme = open(os.path.join(
    'src', 'dolmen', 'security', 'policies', 'README.txt')).read()
history = open(os.path.join("docs", "HISTORY.txt")).read()

install_requires = [
    'setuptools',
    'zope.annotation',
    'zope.security',
    'zope.securitypolicy',
    'grokcore.component',
    ]

tests_require = [
    'zope.component',
    'zope.location',
    'zope.interface',
    'zope.principalregistry',
    ]

setup(name='dolmen.security.policies',
      version=version,
      description="A collection of security maps baseclasses",
      long_description=readme + "\n\n" + history,
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='Grok security',
      author='Souheil Chelfouh',
      author_email='trollfot@gmail.com',
      url='http://www.dolmen-project.org',
      license = 'GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages = ['dolmen', 'dolmen.security'],
      include_package_data = True,
      platforms = 'Any',
      zip_safe = False,
      tests_require = tests_require,
      install_requires = install_requires,
      extras_require = {'test': tests_require},
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
