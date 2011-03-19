from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='stroller',
      version=version,
      description="E-commerce module library for Turbogears",
      long_description="""\
Stroller is a indipendent module that integrates a full customizable e-commerce section under your /shop route.
The main features are:
  * Paypal payments
  * Goods categories
  * Barcodes and SKU management
  * Anonymous checkouts
  * Fully themable
  * Purchase Orders
  * Invoicing
  * Shipping time management
  * Fully l10n and i18n

Easy to use it is as easy as be imported.
""",
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Framework :: TurboGears",
          "Topic :: Office/Business :: Financial :: Point-Of-Sale",
          "Topic :: Internet :: WWW/HTTP :: Dynamic Content"
      ],
      keywords='acr turbogears ecommerce paypal shop shopify lib e-commerce',
      author='AXANT',
      author_email='tech@axant.it',
      url='http://projects.axantlabs.com/Stroller',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      package_data = {'':['*.html', '*.js', '*.css', '*.png', '*.gif']},
      message_extractors = {'stroller': [
         ('**.py', 'python', None),
         ('templates/**.mako', 'mako', None),
         ('templates/**.html', 'genshi', None),
         ('public/**', 'ignore', None)]},
      zip_safe=False,
      install_requires=[
      "PIL",
      "Babel",
      "tw.dynforms",
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
     )
