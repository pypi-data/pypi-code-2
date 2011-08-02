from setuptools import setup, find_packages
import os

__name__ = 'wsapi4plone.core'
version_txt = os.path.join('wsapi4plone', 'core', 'version.txt')
__version__ = open(version_txt).read().strip()

setup(name=__name__,
      version=__version__,
      author='WebLion Group, Penn State University',
      author_email='support@weblion.psu.edu',
      description="A Web Services API for Plone (>=3.x).",
      long_description='\n\n'.join([
        open('README.txt').read(),
        open(os.path.join('doc','changes.rst')).read(),
        ]),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=["Framework :: Plone",
                   "Framework :: Zope2",
                   "Programming Language :: Python",
                   "Topic :: Software Development :: Libraries :: Python Modules",
                   "Intended Audience :: Developers",
                   # "Development Status :: 3 - Alpha",
                   "Development Status :: 4 - Beta",
                   # "Development Status :: 5 - Production/Stable",
                   ],
      keywords='wsapi, api, xmlrpc, weblion',
      url='http://packages.python.org/wsapi4plone.core/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'bootstrap.py']),
      namespace_packages=['wsapi4plone'],
      extras_require = dict(test=['zope.app.testing',
                                  'zope.testing',
                                  'zope.traversing',
                                  ],
                            blob=['plone.app.blob'],
                            plone33=['collective.autopermission==1.0b2',
                                     'plone.app.blob==1.5',
                                     'ZODB3==3.8.3',
                                     ],
                            ),
      install_requires=['setuptools',
                        'collective.autopermission',
                        ##'Plone',
                        # We have support for plone.app.blob, but only use it
                        # when it's already available (e.g Plone >= 4).
                        ##'plone.app.blob',
                        ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin] 
      target = plone 
      """,
      include_package_data=True,
      zip_safe=False,
      )
