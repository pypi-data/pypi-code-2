from setuptools import setup, find_packages
import os

version = "1.1.6"

setup(name='Products.PloneInvite',
      version=version,
      description="Members can invite new members; registration only possible if invited",
      long_description="\n\n".join([
        open(os.path.join("README.txt")).read(),
        open(os.path.join("docs", "NEWS.txt")).read(),
        open(os.path.join("docs", "TODO.txt")).read(),
        ]),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Plone"
        ],
      keywords='Plone PloneInvite',
      author='Giovani Spagnolo',
      author_email='no_mail_please@example.com',
      maintainer='Kees Hink',
      maintainer_email='hink@gw20e.com',
      url='http://plone.org/products/plone-invite/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
