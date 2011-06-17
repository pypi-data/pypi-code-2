from setuptools import setup, find_packages
import sys, os

version = '0.4.1'

setup(name='zopyx.ep2011',
      version=version,
      description="Europython MongoDB/Python training material",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Andreas Jung',
      author_email='info@zopyx.com',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'pymongo',
          # -*- Extra requirements: -*-
      ],
      entry_points=dict(
        console_scripts=['do-import=zopyxep2011.do_import:main'],
        ),
      )
