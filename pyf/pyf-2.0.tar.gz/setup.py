from setuptools import setup, find_packages
import sys, os

version = '2.0'

minimal = [
        'pyf.dataflow >= 2.0',
        'pyf.dataflow  < 2.1',
        'pyf.manager >= 2.0',
        'pyf.manager  < 2.1',
        'pyf.splitter >= 2.0',
        'pyf.splitter  < 2.1',
        'pyf.warehouse >= 2.0',
        'pyf.warehouse  < 2.1',
        ]
components = [
        'pyf.componentized >= 2.0',
        'pyf.componentized  < 2.1',
        'pyf.components.adapters.standardtools >= 1.0',
        'pyf.components.consumers.csvwriter >= 0.7',
        'pyf.components.consumers.fixedlengthwriter >= 0.7',
        'pyf.components.consumers.ooowriter >= 0.2',
        'pyf.components.consumers.rmlpdfwriter >= 0.7',
        'pyf.components.consumers.xhtmlpdfwriter >= 0.2',
        'pyf.components.consumers.xmlwriter >= 0.6',
        'pyf.components.producers.descriptorsource >= 0.5',
        'pyf.components.producers.webextractor >= 0.2',
        ]
fullstack = components + [
        'pyf.services >= 2.0',
        'pyf.services  < 2.1',
        'pyf.components.postprocess.email_sender',
        'pyf.components.postprocess.files_post_handler',
        ]

setup(name='pyf',
      version=version,
      description="Pyf is a dataflow library",
      long_description="""\
""",
      classifiers=['Topic :: Software Development :: Libraries :: Python Modules',
                   'Development Status :: 4 - Beta'], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Jonathan Schemoul, Florent Aide, Jerome Collette',
      author_email='jonathan.schemoul@gmail.com, florent.aide@gmail.com, collette.jerome@gmail.com',
      url='http://pyfproject.org',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      namespace_packages=['pyf'],
      include_package_data=True,
      zip_safe=False,
      install_requires=minimal,
      extras_require={
          'minimal': minimal,
          'components': components,
          'fullstack': fullstack,
      },
      entry_points="""
      # -*- Entry points: -*-
      """,
      test_suite = 'nose.collector',
      )
