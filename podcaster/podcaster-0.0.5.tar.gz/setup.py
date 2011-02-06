# -*- coding:utf-8 -*-

VERSION = '0.0.5'

from setuptools import setup, find_packages

setup(
      name='podcaster',
      version=VERSION,
      author='Pierre Meyer',
      author_email='meyer.p@gmail.com',
      description="Podcaster is a Nagare application used to convert a youtube or dailymotion channel to an itunes podcast.",
      long_description=open('README.txt').read(),
      license='BSD',
      keywords='Nagare Youtube Dailymotion iTunes podcast RSS',
      url='https://bitbucket.org/droodle/podcaster',
      packages=find_packages(),
      include_package_data=True,
      package_data={'' : ['*.cfg']},
      zip_safe=False,
      install_requires=('nagare==0.3.0', 'restkit==2.2.3'),
      entry_points="""
      [nagare.applications]
      podcaster = podcaster.app:app
      """,
      classifiers=('Development Status :: 4 - Beta',
                   'License :: OSI Approved :: BSD License',
                   'Programming Language :: Python')
     )
