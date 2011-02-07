"""Setup file for easy installation"""
from os.path import join, dirname
from setuptools import setup, find_packages

version = __import__('activitysync').__version__

setup(
    name = 'django-activitysync',
    version = version,
    author = 'Dan Carroll',
    author_email = 'dan@dancarroll.org',
    description = 'Fast and easy social activity aggregation for Django projects',
    license = 'GPL',
    keywords = 'django, social, application, twitter',
    url = 'https://bitbucket.org/dancarroll/django-activitysync',
    download_url = 'https://bitbucket.org/dancarroll/django-activitysync/downloads',
    packages = find_packages(),
    long_description = open(join(dirname(__file__), 'README.rst')).read(),
    classifiers = ['Framework :: Django',
                   'Development Status :: 4 - Beta',
                   'Topic :: Internet',
                   'Intended Audience :: Developers',
                   'Environment :: Web Environment',
                   'Programming Language :: Python :: 2.6',
                   'Programming Language :: Python :: 2.7'],
)
