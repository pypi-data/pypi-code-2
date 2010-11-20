from setuptools import setup, find_packages
import os

version = '0.6'

setup(name='collective.skinny',
      version=version,
      description="Plone theming for mortals: A simple example to get you started quickly with your own public skin",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "THANKS.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
        "Framework :: Plone",
        "Framework :: Zope2",
        ],
      keywords='plone zope public skin template theming',
      author='Daniel Nouri',
      author_email='daniel.nouri@gmail.com',
      url='http://pypi.python.org/pypi/collective.skinny',
      license='LGPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'beautifulsoup',
          'plone.postpublicationhook',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
