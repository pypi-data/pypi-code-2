from setuptools import setup, find_packages
import os

version = '1.0b2'

tests_require = ['unittest2',
                 'plone.app.testing',
                 ]

setup(name='plone.cachepurging',
      version=version,
      description="Cache purging support for Zope 2 applications",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone cache purge',
      author='Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://pypi.python.org/pypi/plone.cachepurging',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.interface',
          'zope.component',
          'zope.event',
          'zope.annotation',
          'zope.lifecycleevent',
          'zope.i18nmessageid',
          'five.globalrequest',
          'plone.registry',
          'Zope2',
      ],
      tests_require=tests_require,
      extras_require={
        'test': tests_require,
      },
      )
