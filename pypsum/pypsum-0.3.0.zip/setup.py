from __future__ import with_statement
from setuptools import setup
import sys
import os

wd = os.path.dirname(os.path.abspath(__file__))
os.chdir(wd)
sys.path.insert(1, wd)

name = 'pypsum'
pkg = __import__(name)
author, email = pkg.__author__.rsplit(' ', 1)

with open(os.path.join(wd, 'README.rst'),'r') as readme:
    long_description = readme.read()

python_version = sys.version_info[:2]
url = 'http://projects.monkeython.com/%s' % name

application = {
    'name': name,
    'version': pkg.__version__,
    'author': author,
    'author_email': email.strip('<>'),
    'url': '%s/html' % url,
    'description': "A RESTfull Lorem Ipsum text generator",
    'long_description': long_description,
    'classifiers': pkg.__classifiers__,
    'packages': [name],
    'install_requires': ['loremipsum', 'Flask', 'requests' ],
    'include_package_data': True,
    'exclude_package_data': {name: ["*.rst", "docs", "tests"]},
    'test_suite': 'tests.suite'}

if __name__ == '__main__':
    setup(**application)

