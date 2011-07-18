from setuptools import setup, find_packages
import sys, os

version = '0.1.1'

setup(name='textconverter',
      version=version,
      description="convert text encoding utility",
      long_description="""\

Example

::

    from textconverter import convert
    
    text = 'nanika'
    text = convert.to_utf8(text)
    text = convert.utf8_to_eucjp(text)
    
    texts = ['hoge', 'fuga']
    texts = convert.to_sjis(texts)
    texts = convert.sjis_to_utf8(texts)

""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='text encoding convert',
      author='ukyo',
      author_email='ukyo.web@gmail.com',
      url='https://github.com/ukyo/textconverter',
      license='Apache',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'chardet'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
