# -*- coding: utf-8 -*-
VERSION = '0.0.2'

from setuptools import setup, find_packages

setup(
      name='css_crawler',
      version=VERSION,
      author='Herve Coatanhay',
      author_email='herve.coatanhay@gmail.com',
      description='''CSSCrawler is a Nagare application that creates color map from website URLs''',
      license='BSD',
      keywords='Nagare CSS',
      url='https://bitbucket.org/Alzakath/csscrawler',
      packages=find_packages(),
      include_package_data=True,
      package_data={'': ['*.cfg']},
      zip_safe=False,
      install_requires=('nagare', 'cssutils', 'htmlcolor', 'simplejson', 'Babel', 'Elixir', 'SQLAlchemy', 'pysqlite'),
      entry_points="""
      [nagare.applications]
      css_crawler = css_crawler.app:app
      """,
      message_extractors={'css_crawler': [('**.py', 'python', None)]}
     )
