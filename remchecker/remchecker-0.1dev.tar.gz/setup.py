from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='remchecker',
      version=version,
      description="check followers remove",
      long_description="""\
""",
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: End Users/Desktop',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: Japanese',
          'Programming Language :: Python',
          'Topic :: Communications'
          ],
      keywords='twitter remove',
      author='seikichi',
      author_email='seikichi@kmc.gr.jp',
      url='',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'tweepy',
          'pyyaml',
          'simplejson'
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      remchecker = remchecker:main
      """,
      )
