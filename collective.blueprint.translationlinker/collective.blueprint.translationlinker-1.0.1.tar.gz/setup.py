from setuptools import setup, find_packages
import os

version = '1.0.1'
readme = open("README.txt").read()

setup(name='collective.blueprint.translationlinker',
      version=version,
      description="",
      long_description=readme[readme.find('\n\n'):] + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Florian Schulze',
      author_email='florian.schulze@gmx.net',
      url='http://svn.plone.org/svn/collective/collective.blueprint.translationlinker',
      license='GPL',
      packages=['collective', 'collective.blueprint',
                'collective.blueprint.translationlinker'],
      namespace_packages=['collective', 'collective.blueprint'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.transmogrifier',
          'Products.LinguaPlone',
      ],
      )
