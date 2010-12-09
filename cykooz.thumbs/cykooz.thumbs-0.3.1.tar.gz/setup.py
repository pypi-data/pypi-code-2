import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup (
    name = 'cykooz.thumbs',
    version = '0.3.1',
    author = "Cykooz",
    author_email = "saikuz@mail.ru",
    description = "WSGI middleware for image resizing",
    long_description = (
        read('README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = "GPL",
    keywords = "wsgi middleware imaging",
    url = 'https://bitbucket.org/cykooz/cykooz.thumbs',
    classifiers = [
        'Environment :: Web Environment',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application'
        ],
    packages = find_packages('src'),
    package_dir = {'':'src'},
    namespace_packages = ['cykooz'],
    install_requires = [
        'distribute',
        'Paste',
        'WebOb',
        'zope.datetime',
        'PIL>=1.1.7',
    ],
    zip_safe = False,
    entry_points = '''
    	[paste.filter_app_factory]
    	main = cykooz.thumbs.middleware:make_thumbs
    	[paste.app_factory]
        main = cykooz.thumbs.application:make_thumbs_app'''
)
