"""Setup file for easy installation"""
from os.path import join, dirname
from setuptools import setup, find_packages

version = __import__('activitysync').__version__

setup(
    name = 'django-activitysync',
    version = version,
    author = 'Dan Carroll',
    author_email = 'dan@dancarroll.org',
    description = 'Fast, easy, and extensible social activity aggregation for Django projects',
    license = 'BSD',
    keywords = 'django, social, activity, application, twitter, reddit, google reader',
    url = 'https://bitbucket.org/dancarroll/django-activitysync',
    download_url = 'https://bitbucket.org/dancarroll/django-activitysync/downloads',
    packages = find_packages(),
    package_data = { 'activitysync':
        ['templates/*.html', 'templates/activitysync/*.html']
    },
    long_description = open(join(dirname(__file__), 'README.rst')).read(),
    classifiers = ['Framework :: Django',
                   'Development Status :: 4 - Beta',
                   'Topic :: Internet',
                   'Intended Audience :: Developers',
                   'Environment :: Web Environment',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2.6',
                   'Programming Language :: Python :: 2.7',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent'],
)

