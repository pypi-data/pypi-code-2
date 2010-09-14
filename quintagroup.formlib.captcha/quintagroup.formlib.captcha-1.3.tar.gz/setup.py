from setuptools import setup, find_packages
import os

version = '1.3'

setup(name='quintagroup.formlib.captcha',
      version=version,
      description="Captcha field for formlib based on quintagroup.captcha.core package",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone formlib captcha',
      author='Quintagroup',
      author_email='support@quintagroup.com',
      url='http://svn.quintagroup.com/products/quintagroup.formlib.captcha',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['quintagroup', 'quintagroup.formlib'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'quintagroup.captcha.core',
          'zope.app.form',
          'zope.formlib',
          # 'five.formlib',
          # 'zope.component',
          # 'zope.interface',
          # 'zope.schema',
          # 'zope.i18n',
          # 'Products.CMFCore',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
