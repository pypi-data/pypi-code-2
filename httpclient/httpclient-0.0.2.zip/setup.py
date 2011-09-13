'''
Created on Aug 14, 2011
@author: guillaume
'''
import os
here = os.path.dirname(os.path.abspath(__file__))
## Get long_description from long_description.txt:
f = open(os.path.join(here, 'doc', 'long_description.txt'))
long_description = f.read().strip()
f.close()

from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

setup(name='httpclient',
      version='0.0.2',
      author='Guillaume Humbert',
      author_email='guillaume.humbert.jp@gmail.com',
	  maintainer='Guillaume Humbert',
      maintainer_email='guillaume.humbert.jp@gmail.com',
      url='https://github.com/guillaume-humbert/httpclient',
	  download_url='https://github.com/guillaume-humbert/httpclient',
      description="A headless HTTP browser.",
	  long_description=long_description,
	  classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
		'Natural Language :: English',
		'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.2',
		'Topic :: Internet :: WWW/HTTP',
		'Topic :: Internet :: WWW/HTTP :: Browsers',
        ],
	  keywords='http headless browser crawler html',
	  platforms='Unix, Windows',
      license='GNU General Public License (GPL) v3',
      package_dir = {'': 'src'},
      packages = find_packages('src'),
      test_suite = 'httpclient_test',
      tests_require = 'mockito')