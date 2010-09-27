from setuptools import setup, find_packages
import os

setup(name='themetweaker.themeswitcher',
      version='1.0',
      author='Six Feet Up, Inc. <info at sixfeetup com> | WebLion Group, Penn State University',
      author_email='support@weblion.psu.edu',
      description="A product for switching themes in Plone.",
      long_description=open('README.txt').read() + "\n\n" +
                       open(os.path.join("docs", "INSTALL.txt")).read() + "\n\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.4",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
        "Development Status :: 4 - Beta",
        ],
      keywords='themeswitcher themetweaker theme switcher weblion',
      url='https://weblion.psu.edu/trac/weblion/wiki/ThemeSwitcher',
      license='GPL',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['themetweaker',],
      extras_require = dict(test=['zope.app.testing',
                                  'zope.testing',
                                  'zope.traversing',
                                  ]),
      install_requires=[
          'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      include_package_data=True,
      zip_safe=False,
      )
