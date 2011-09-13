# -*- coding: utf-8 -*-
# $Id$
import os
from setuptools import setup, find_packages

version = '1.0'

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()
except:  # doesn't work under tox/pip
    README = ''
    CHANGES = ''

setup(name='collective.collage.feedfeeder',
      version=version,
      description="Collage add-on that allows displaying RSS-feeds.",
      long_description="\n\n".join((README, CHANGES)),
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Plone",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Development Status :: 5 - Production/Stable",
        ],
      keywords='collage plone rss feedfeeder',
      author='Malthe Borch',
      author_email='mborch@gmail.com',
      url='http://www.plone.org/products/collective.collage.feedfeeder',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.collage'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.Collage',
          'Products.feedfeeder',
          # -*- Extra requirements: -*-
      ],
      )
