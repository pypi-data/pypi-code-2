from setuptools import setup, find_packages
import os

__name__ = 'wsapi4plone.core'
version_txt = os.path.join('wsapi4plone', 'core', 'version.txt')
__version__ = open(version_txt).read().strip()

setup(name=__name__,
      version=__version__,
      author='WebLion Group, Penn State University',
      author_email='support@weblion.psu.edu',
      description="A Web Services API for Plone.",
      # XXX need to add a stub file to point to the built sphinx docs
      long_description='\n\n'.join([
        open('README.txt').read(),
        open(os.path.join('doc','changes.rst')).read(),
        ]),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=["Framework :: Plone",
                   "Framework :: Zope2",
                   "Programming Language :: Python",
                   "Programming Language :: Python :: 2.4",
                   "Topic :: Software Development :: Libraries :: Python Modules",
                   "Intended Audience :: Developers",
                   "Development Status :: 3 - Alpha",
                   # "Development Status :: 4 - Beta",
                   # "Development Status :: 5 - Production/Stable",
                   ],
      keywords='wsapi, api, xmlrpc, weblion',
      url='https://weblion.psu.edu/trac/weblion/wiki/WebServicesApiPlone',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'bootstrap.py']),
      namespace_packages=['wsapi4plone'],
      extras_require = dict(test=['zope.app.testing',
                                  'zope.testing',
                                  'zope.traversing',
                                  ]),
      install_requires=['setuptools',
                        'collective.autopermission',
                        # If versions of Plone < 3.2 want to be used, the Plone egg dependency
                        # can't be included (e.g Plone 3.1.7)
                        # Can not include this line, because the Plone egg is version >= 3.2
                        # 'plone',
                        # -*- Extra requirements: -*-
                        ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin] 
      target = plone 
      """,
      include_package_data=True,
      zip_safe=False,
      )
